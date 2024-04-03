import sys
from pathlib import Path
from enum import IntEnum

import pygame as pg

from colors import *
import maps
import tiles
import mobs
import weapons
import images


SCREEN_SIZE = (800, 600)
SCREEN_CENTER = pg.Vector2(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
SCREEN_TITLE = "Xenoreactor Overload"

HEALTH_BAR_FADE = 1500
PLAYER_HEAT_DECAY = 10
PLAYER_MOVE_HEAT_DECAY_PENALTY = 2
PLAYER_FIRE_HEAT_DECAY_PENALTY = 2

key_to_weapon = {
    pg.K_1: weapons.WeaponID.MINIGUN,
    pg.K_2: weapons.WeaponID.SHOTGUN,
    pg.K_3: weapons.WeaponID.RICOCHET,
    pg.K_4: weapons.WeaponID.CANNON,
    pg.K_5: weapons.WeaponID.FLAME,
    pg.K_6: weapons.WeaponID.ROCKET,
}

weapon_tuple = (
    weapons.WeaponID.MINIGUN,
    weapons.WeaponID.SHOTGUN,
    weapons.WeaponID.RICOCHET,
    weapons.WeaponID.CANNON,
    weapons.WeaponID.FLAME,
    weapons.WeaponID.ROCKET,
)

ammo_dict = {
    weapons.WeaponID.MINIGUN: weapons.weapon_max_ammo[weapons.WeaponID.MINIGUN],
    weapons.WeaponID.SHOTGUN: weapons.weapon_max_ammo[weapons.WeaponID.SHOTGUN],
    weapons.WeaponID.RICOCHET: weapons.weapon_max_ammo[weapons.WeaponID.RICOCHET],
    weapons.WeaponID.CANNON: weapons.weapon_max_ammo[weapons.WeaponID.CANNON],
    weapons.WeaponID.FLAME: weapons.weapon_max_ammo[weapons.WeaponID.FLAME],
    weapons.WeaponID.ROCKET: weapons.weapon_max_ammo[weapons.WeaponID.ROCKET],
}


class ParticleID:
    EXPLOSION = 1


class Particle(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], vel: tuple[int, int], lifetime: int, eid: ParticleID):
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.lifetime = lifetime
        self.current_life = pg.time.get_ticks()
        self.id = eid

    def update(self, dt):
        if pg.time.get_ticks() - self.current_life >= self.lifetime:
            self.kill()
            return
        self.pos += self.vel * dt


def get_screen(size: tuple[int, int], full_screen: bool = True) -> pg.Surface:
    """Return a pygame display surface for rendering."""
    return pg.display.set_mode(size, pg.FULLSCREEN if full_screen else 0)


def get_font(font_path: Path, size: int) -> pg.font.Font:
    if font_path.exists():
        return pg.font.Font(font_path, size)
    else:
        return pg.font.Font(None, size)


def int_vec(vec: pg.Vector2) -> tuple[int, int]:
    return int(vec.x), int(vec.y)


def load_map(map_str: str) -> tuple[pg.sprite.Group, pg.sprite.Group]:
    tile_objects = pg.sprite.Group()
    mob_objects = pg.sprite.Group()
    x = y = 0
    for char in map_str.strip("\n"):
        if char == "\n":
            # Go down to the next row.
            x = 0
            y += images.TILE_SIZE[1]
            continue
        if char in tiles.char_to_tile_id.keys():
            tile_objects.add(tiles.Tile((x, y), char))
        if char in mobs.char_to_mob_id.keys():
            mob_objects.add(mobs.Mob((x, y), char))
        x += images.TILE_SIZE[0]
    return tile_objects, mob_objects


def find_player(mob_objects: pg.sprite.Group) -> mobs.Mob:
    for mob in mob_objects:
        if mob.id is mobs.MobID.PLAYER:
            mob_objects.remove(mob)
            return mob
    else:
        return mobs.Mob(images.TILE_SIZE, "@")


def heat_pct_color(pct: float) -> tuple[int, int, int]:
    r = 255
    if pct < 0.5:
        r = pg.math.lerp(0, 255, pct * 2)
    g = 255
    if pct > 0.5:
        g = pg.math.lerp(255, 0, (pct - 0.5) * 2)
    return r, g, 0


def shield_pct_color(pct: float) -> tuple[int, int, int]:
    return 0, int(pg.math.lerp(0, 255, pct)), 255


def draw_pct_bar(screen: pg.Surface, pos: tuple[int, int], color: tuple[int, int, int], pct: float):
    # Draw background bar.
    pg.draw.circle(screen, WHITE, pos, 16)
    pg.draw.rect(screen, WHITE, (pos[0], pos[1] - 16, 200, 32))
    pg.draw.circle(screen, WHITE, (200 + pos[0], pos[1]), 16)
    # Draw colored bar.
    if pct > 0:
        pg.draw.circle(screen, color, pos, 16)
        pg.draw.rect(screen, color, (pos[0], pos[1] - 16, int(200 * pct), 32))
        pg.draw.circle(screen, color, (int(200 * pct) + pos[0], pos[1]), 16)


def draw_health_bar(screen: pg.Surface, pos: pg.Vector2, pct: float, length: int, color: pg.Color = ORANGE):
    pg.draw.rect(screen, WHITE, (pos[0] - 1, pos[1] - 1, length + 2, 8))
    pg.draw.rect(screen, color, (*pos, int(length * pct), 6))


def main():
    # Set up the game window.
    icon_image = pg.Surface((32, 32))
    icon_image.fill(BLACK)
    pg.draw.line(icon_image, CYAN, (8, 4), (24, 28), 3)
    pg.draw.line(icon_image, CYAN, (24, 4), (8, 28), 3)
    pg.display.set_icon(icon_image)
    full_screen = False
    screen = get_screen(SCREEN_SIZE, full_screen)
    pg.display.set_caption(SCREEN_TITLE)
    pg.mouse.set_visible(False)
    # Set up useful objects.
    clock = pg.time.Clock()
    font_path = Path() / "Kenney Future.ttf"
    font12 = get_font(font_path, 12)
    font24 = get_font(font_path, 24)
    debug = False
    # Make the images.
    images.make_images()
    # Set up game world.
    tile_objects, mob_objects = load_map(maps.TESTING)
    bullets = pg.sprite.Group()
    player_bullets = pg.sprite.Group()
    particles = pg.sprite.Group()
    # Find the player.
    player = find_player(mob_objects)
    max_shield = 100
    shield = 100
    # Key events.
    w = s = a = d = firing = False
    reload_timer = pg.time.get_ticks()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                elif event.key == pg.K_F5:
                    full_screen = not full_screen
                    screen = get_screen(SCREEN_SIZE, full_screen)
                elif event.key in key_to_weapon.keys():
                    player.weapon = key_to_weapon[event.key]
                elif event.key == pg.K_e:
                    if player.heat > 0 and shield >= 10:
                        player.heat -= 20
                        player.heat = max(0, player.heat)
                        shield -= 10
                elif event.key == pg.K_w or event.key == pg.K_UP:
                    w = True
                elif event.key == pg.K_s or event.key == pg.K_DOWN:
                    s = True
                elif event.key == pg.K_a or event.key == pg.K_LEFT:
                    a = True
                elif event.key == pg.K_d or event.key == pg.K_RIGHT:
                    d = True
            elif event.type == pg.KEYUP:
                if event.key == pg.K_w or event.key == pg.K_UP:
                    w = False
                elif event.key == pg.K_s or event.key == pg.K_DOWN:
                    s = False
                elif event.key == pg.K_a or event.key == pg.K_LEFT:
                    a = False
                elif event.key == pg.K_d or event.key == pg.K_RIGHT:
                    d = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    firing = True
                elif event.button == 3:
                    if player.heat > 0 and shield >= 10:
                        player.heat -= 20
                        player.heat = max(0, player.heat)
                        shield -= 10
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    firing = False
            elif event.type == pg.MOUSEWHEEL:
                current_w = weapon_tuple.index(player.weapon)
                if event.flipped:
                    current_w += event.y
                else:
                    current_w -= event.y
                current_w %= len(weapon_tuple)
                player.weapon = weapon_tuple[current_w]

        # Update stuff.
        dt = clock.tick() / 1000.0

        # Move player and do collisions.
        moving_vertical = w ^ s
        moving_horizontal = a ^ d
        amount = mobs.mob_speed[player.id] * dt * (0.707 if moving_horizontal and moving_vertical else 1)
        if moving_vertical:
            if w:
                player.pos.y -= amount
                player.update_rect()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.top = hit.rect.bottom
                    player.pos.y = hit.rect.bottom
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.top = hit.rect.bottom
                    player.pos.y = hit.rect.bottom
            if s:
                player.pos.y += amount
                player.update_rect()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.bottom = hit.rect.top
                    player.pos.y = hit.rect.top - player.rect.height
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.bottom = hit.rect.top
                    player.pos.y = hit.rect.top - player.rect.height
        if moving_horizontal:
            if a:
                player.pos.x -= amount
                player.update_rect()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.left = hit.rect.right
                    player.pos.x = hit.rect.right
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.left = hit.rect.right
                    player.pos.x = hit.rect.right
            if d:
                player.pos.x += amount
                player.update_rect()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.right = hit.rect.left
                    player.pos.x = hit.rect.left - player.rect.width
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.right = hit.rect.left
                    player.pos.x = hit.rect.left - player.rect.width

        # Camera math.
        camera_shift = pg.Vector2(int_vec(SCREEN_CENTER - player.rect.center))

        # Fire the weapon.
        if firing and ammo_dict[player.weapon] > 0:
            if pg.time.get_ticks() - reload_timer >= weapons.weapon_reload[player.weapon]:
                if player.weapon is not weapons.WeaponID.MINIGUN:
                    ammo_dict[player.weapon] -= 1
                reload_timer = pg.time.get_ticks()
                b = weapons.Bullet(player.rect.center, pg.mouse.get_pos() - SCREEN_CENTER, player.weapon, True)
                player_bullets.add(b)
                if player.weapon is weapons.WeaponID.SHOTGUN:
                    for _ in range(9):
                        b = weapons.Bullet(player.rect.center, pg.mouse.get_pos() - SCREEN_CENTER, player.weapon, True)
                        player_bullets.add(b)

        # Update all the mobs.
        mob_objects.add(player)
        los_lines = []
        for m in mob_objects:
            if m.update(dt, tile_objects, mob_objects, player, bullets):
                los_lines.append(m.rect.center)
        player_bullets.update(dt, tile_objects, mob_objects, pg.mouse.get_pos(), player, camera_shift)
        bullets.update(dt, tile_objects, mob_objects, pg.mouse.get_pos(), player, camera_shift)
        mob_objects.remove(player)

        # Update particles.
        particles.update(dt)

        # Reduce player heat.
        decay = (PLAYER_HEAT_DECAY - (PLAYER_FIRE_HEAT_DECAY_PENALTY if firing else 0)
                 - (PLAYER_MOVE_HEAT_DECAY_PENALTY if moving_horizontal or moving_vertical else 0))
        player.heat -= decay * dt
        player.heat = max(0, player.heat)

        # Draw stuff.
        screen.fill(BLACK)

        # Draw map tiles.
        for tile in tile_objects:
            screen.blit(tile.image, camera_shift + tile.rect.topleft)

        # Draw mobs.
        for mob in mob_objects:
            screen.blit(mob.image, camera_shift + mob.rect.topleft)
        screen.blit(player.image, camera_shift + player.rect.topleft)

        # Draw bullets.
        for b in bullets:
            pg.draw.circle(screen, weapons.weapon_color[b.id], camera_shift + int_vec(b.pos),
                           weapons.weapon_radius[b.id])
        for b in player_bullets:
            pg.draw.circle(screen, weapons.weapon_color[b.id], camera_shift + int_vec(b.pos), weapons.weapon_radius[b.id])

        # Draw tile health.
        for tile in tile_objects:
            if pg.time.get_ticks() - tile.last_hit <= HEALTH_BAR_FADE:
                if tile.health < tile.max_health:
                    draw_health_bar(screen, camera_shift + (tile.rect.left, tile.rect.top - 9),
                                    tile.health / tile.max_health, images.TILE_SIZE[0])

        # Draw mob heat.
        for mob in mob_objects:
            if pg.time.get_ticks() - mob.last_hit <= HEALTH_BAR_FADE:
                if mob.heat > 0:
                    draw_health_bar(screen, camera_shift + (mob.rect.left, mob.rect.top - 9),
                                    mob.heat / mob.max_heat, images.TANK_SIZE[0], RED)

        # Draw the particles.
        for p in particles:
            pass

        # Draw debug lines.
        if debug:
            for p in los_lines:
                pg.draw.line(screen, RED, camera_shift + p, camera_shift + player.rect.center)

        # Draw UI.

        # Draw heat meter.
        heat_pct = player.heat / player.max_heat
        draw_pct_bar(screen, (20, 20), heat_pct_color(heat_pct), heat_pct)
        heat_text_surf = font24.render(f"HEAT: {int(player.heat)}/{player.max_heat}", True, BLACK)
        screen.blit(heat_text_surf, (15, 7))

        # Draw current weapon.
        weapon_text_surf = font24.render(f" WEAPON: {weapons.weapon_names[player.weapon]}", True, BLACK,
                                         weapons.weapon_color[player.weapon])
        screen.blit(weapon_text_surf, (SCREEN_CENTER[0] - (weapon_text_surf.get_width() // 2), 4))
        for i in range(6):
            num_surf = font12.render(f" {i + 1}", True, BLACK, weapons.weapon_color[weapon_tuple[i]])
            screen.blit(num_surf, ((SCREEN_CENTER[0] - (weapon_text_surf.get_width() // 2)) + (i * 13),
                                   weapon_text_surf.get_height() + 4))

        # Draw shield meter.
        shield_pct = shield / max_shield
        draw_pct_bar(screen, (20, 60), shield_pct_color(shield_pct), shield_pct)
        shield_text_surf = font24.render(f"COOL: {shield}/{max_shield}", True, BLACK)
        screen.blit(shield_text_surf, (15, 47))
        hint_text = font12.render("E OR RIGHT CLICK TO COOL", True, CYAN)
        screen.blit(hint_text, (25, 75))

        # Draw ammo meter.
        ammo_pct = ammo_dict[player.weapon] / weapons.weapon_max_ammo[player.weapon]
        draw_pct_bar(screen, (SCREEN_SIZE[0] - 220, 20), weapons.weapon_color[player.weapon], ammo_pct)
        if player.weapon is weapons.WeaponID.MINIGUN:
            text = "INFINITE AMMO"
        else:
            text = f"AMMO: {ammo_dict[player.weapon]}/{weapons.weapon_max_ammo[player.weapon]}"
        ammo_text_surf = font24.render(text, True, BLACK)
        screen.blit(ammo_text_surf, (SCREEN_SIZE[0] - 230, 7))

        # Draw targeting reticule.
        mpos = pg.mouse.get_pos()
        pg.draw.circle(screen, RED, mpos, 8, 1)
        pg.draw.line(screen, RED, (mpos[0], mpos[1] - 4), (mpos[0], mpos[1] - 12), 1)
        pg.draw.line(screen, RED, (mpos[0], mpos[1] + 4), (mpos[0], mpos[1] + 12), 1)
        pg.draw.line(screen, RED, (mpos[0] - 4, mpos[1]), (mpos[0] - 12, mpos[1]), 1)
        pg.draw.line(screen, RED, (mpos[0] + 4, mpos[1]), (mpos[0] + 12, mpos[1]), 1)

        # Show FPS.
        fps_surf = font12.render(f"{int(clock.get_fps())}", True, WHITE, BLACK)
        screen.blit(fps_surf, (0, SCREEN_SIZE[1] - fps_surf.get_height()))
        # Update display.
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    main()
