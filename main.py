import sys
from pathlib import Path
import math
import random

import pygame as pg

from colors import *
import maps
import tiles
import mobs
import weapons
import images
import effects


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


def get_screen(size: tuple[int, int], full_screen: bool = True) -> pg.Surface:
    """Return a pygame display surface for rendering."""
    return pg.display.set_mode(size, (pg.FULLSCREEN if full_screen else 0))


def get_font(font_path: Path, size: int) -> pg.font.Font:
    return pg.font.Font(font_path, size)
    # if font_path.exists():
    #     return pg.font.Font(font_path, size)
    # else:
    #     return pg.font.Font(None, size)


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
        if char == "x":
            mob_objects.add(mobs.Mob((x, y), random.choice("msicfrb")))
        if char == "X":
            mob_objects.add(mobs.Mob((x, y), random.choice("MSICFRB")))
        if char == "Z":
            mob_objects.add(mobs.Mob((x, y), random.choice("MSICFRBmsicfrb")))
        if char == "&":
            mob_objects.add(mobs.Mob((x, y), random.choice("*!>$")))
        if char == "_":
            mob_objects.add(mobs.Mob((x, y), random.choice("^%")))
        if char == "-":
            mob_objects.add(mobs.Mob((x, y), random.choice("^%^%*!$>")))
        if char == "<":
            mob_objects.add(mobs.Mob((x, y), random.choice("*!")))
        if char == "`":
            tile_objects.add(tiles.Tile((x, y), random.choice("~=")))
        if char == "0":
            tile_objects.add(tiles.Tile((x, y), random.choice("#=+~")))
        if char == "O":
            tile_objects.add(tiles.Tile((x, y), random.choice("#=+")))
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


def count_coolers(objs: pg.sprite.Group) -> int:
    c = 0
    for t in objs:
        if t.id is tiles.TileID.COOLER:
            c += 1
    return c


class MenuText:
    def __init__(self, img: pg.Surface, pos: tuple[float, int]):
        self.img = img.convert()
        self.hover_img = img.convert_alpha()
        temp_img = pg.Surface(self.hover_img.get_size()).convert_alpha()
        temp_img.fill((*WHITE, 64))
        self.hover_img.blit(temp_img, (0, 0))
        self.rect = self.img.get_rect().move(pos)
        self.hover = False

    def handle_hover(self, pos: tuple[int, int]):
        self.hover = self.rect.collidepoint(pos)

    def get_img(self) -> pg.Surface:
        return self.hover_img if self.hover else self.img


level_dict = {
    0: maps.TESTING,
    1: maps.LEVEL1,
    2: maps.LEVEL2,
    3: maps.LEVEL3,
    4: maps.LEVEL4,
    5: maps.LEVEL5,
    6: maps.LEVEL6,
    7: maps.LEVEL7,
    8: maps.LEVEL8,
    9: maps.LEVEL9,
    10: maps.LEVEL10,
    11: maps.LEVEL11,
    12: maps.LEVEL12,
    13: maps.LEVEL13,
    14: maps.LEVEL14,
    15: maps.TESTING,
}


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
    font36 = get_font(font_path, 36)
    debug = False
    draw_particles = True
    # Make the images.
    images.make_images()
    # Menu texts.
    next_level_text = font36.render(" ALL COOLERS DESTROYED", True, BLACK, CYAN)
    next_level_text = MenuText(next_level_text, (SCREEN_CENTER[0] - next_level_text.get_width() // 2, 100))
    game_over_text = font36.render(" CORE OVERHEATED", True, BLACK, RED)
    game_over_text = MenuText(game_over_text, (SCREEN_CENTER[0] - game_over_text.get_width() // 2, 100))
    quit_button = font24.render(" QUIT PROGRAM", True, BLACK, RED)
    quit_button = MenuText(quit_button, (SCREEN_CENTER[0] - quit_button.get_width() // 2, 450))
    next_level_button = font24.render(" NEXT STAGE", True, BLACK, GREEN)
    next_level_button = MenuText(next_level_button, (SCREEN_CENTER[0] - next_level_button.get_width() // 2, 400))
    restart_button = font24.render(" RESTART PROGRAM", True, BLACK, GREEN)
    restart_button = MenuText(restart_button, (SCREEN_CENTER[0] - restart_button.get_width() // 2, 400))
    overheating_surf = pg.Surface(SCREEN_SIZE).convert_alpha()
    overheating_surf.fill((*RED, 64))
    # Key events.
    w = s = a = d = firing = False
    reload_timer = pg.time.get_ticks()
    # Set up game world.
    current_level = 1
    tile_objects, mob_objects = load_map(level_dict[current_level])
    bullets = pg.sprite.Group()
    player_bullets = pg.sprite.Group()
    particles = pg.sprite.Group()
    # Find the player.
    player = find_player(mob_objects)
    max_shield = 10
    shield = 10
    p_m_heat = player.max_heat
    ammo_dict = {
        weapons.WeaponID.MINIGUN: weapons.weapon_max_ammo[weapons.WeaponID.MINIGUN],
        weapons.WeaponID.SHOTGUN: weapons.weapon_max_ammo[weapons.WeaponID.SHOTGUN],
        weapons.WeaponID.RICOCHET: weapons.weapon_max_ammo[weapons.WeaponID.RICOCHET],
        weapons.WeaponID.CANNON: weapons.weapon_max_ammo[weapons.WeaponID.CANNON],
        weapons.WeaponID.FLAME: weapons.weapon_max_ammo[weapons.WeaponID.FLAME],
        weapons.WeaponID.ROCKET: weapons.weapon_max_ammo[weapons.WeaponID.ROCKET],
    }

    unlock_dict = {
        weapons.WeaponID.MINIGUN: True,
        weapons.WeaponID.SHOTGUN: False,
        weapons.WeaponID.RICOCHET: False,
        weapons.WeaponID.CANNON: False,
        weapons.WeaponID.FLAME: False,
        weapons.WeaponID.ROCKET: False,
    }
    # Scene variables.
    game_over = False
    next_level = False
    level_timer_start = pg.time.get_ticks()
    run_start = pg.time.get_ticks()
    run_ms = 0
    run_cum = 0

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
                elif event.key == pg.K_F6:
                    debug = not debug
                elif event.key in key_to_weapon.keys():
                    if unlock_dict[key_to_weapon[event.key]]:
                        player.weapon = key_to_weapon[event.key]
                elif event.key == pg.K_e:
                    if next_level or game_over:
                        continue
                    if player.heat > 0 and shield <= max_shield and shield > 0:
                        player.heat -= 20
                        player.heat = max(0, player.heat)
                        shield -= 1
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
                    if next_level:
                        if quit_button.rect.collidepoint(event.pos):
                            pg.quit()
                            sys.exit()
                        if next_level_button.rect.collidepoint(event.pos):
                            # Set up game world.
                            current_level += 1
                            tile_objects, mob_objects = load_map(level_dict[current_level])
                            bullets = pg.sprite.Group()
                            player_bullets = pg.sprite.Group()
                            particles = pg.sprite.Group()
                            # Find the player.
                            player = find_player(mob_objects)
                            player.max_heat = p_m_heat
                            shield = max_shield
                            ammo_dict = {
                                weapons.WeaponID.MINIGUN: weapons.weapon_max_ammo[weapons.WeaponID.MINIGUN],
                                weapons.WeaponID.SHOTGUN: weapons.weapon_max_ammo[weapons.WeaponID.SHOTGUN],
                                weapons.WeaponID.RICOCHET: weapons.weapon_max_ammo[weapons.WeaponID.RICOCHET],
                                weapons.WeaponID.CANNON: weapons.weapon_max_ammo[weapons.WeaponID.CANNON],
                                weapons.WeaponID.FLAME: weapons.weapon_max_ammo[weapons.WeaponID.FLAME],
                                weapons.WeaponID.ROCKET: weapons.weapon_max_ammo[weapons.WeaponID.ROCKET],
                            }
                            # Scene variables.
                            game_over = False
                            next_level = False
                            level_timer_start = pg.time.get_ticks()
                            run_ms = 0
                    elif game_over:
                        if quit_button.rect.collidepoint(event.pos):
                            pg.quit()
                            sys.exit()
                        if restart_button.rect.collidepoint(event.pos):
                            # Set up game world.
                            current_level = 1
                            tile_objects, mob_objects = load_map(level_dict[current_level])
                            bullets = pg.sprite.Group()
                            player_bullets = pg.sprite.Group()
                            particles = pg.sprite.Group()
                            # Find the player.
                            mobs.mob_speed[mobs.MobID.PLAYER] = 80
                            player = find_player(mob_objects)
                            p_m_heat = player.max_heat
                            shield = max_shield
                            ammo_dict = {
                                weapons.WeaponID.MINIGUN: weapons.weapon_max_ammo[weapons.WeaponID.MINIGUN],
                                weapons.WeaponID.SHOTGUN: weapons.weapon_max_ammo[weapons.WeaponID.SHOTGUN],
                                weapons.WeaponID.RICOCHET: weapons.weapon_max_ammo[weapons.WeaponID.RICOCHET],
                                weapons.WeaponID.CANNON: weapons.weapon_max_ammo[weapons.WeaponID.CANNON],
                                weapons.WeaponID.FLAME: weapons.weapon_max_ammo[weapons.WeaponID.FLAME],
                                weapons.WeaponID.ROCKET: weapons.weapon_max_ammo[weapons.WeaponID.ROCKET],
                            }
                            unlock_dict = {
                                weapons.WeaponID.MINIGUN: True,
                                weapons.WeaponID.SHOTGUN: False,
                                weapons.WeaponID.RICOCHET: False,
                                weapons.WeaponID.CANNON: False,
                                weapons.WeaponID.FLAME: False,
                                weapons.WeaponID.ROCKET: False,
                            }
                            # Scene variables.
                            game_over = False
                            next_level = False
                            level_timer_start = pg.time.get_ticks()
                            run_start = pg.time.get_ticks()
                            run_ms = 0
                            run_cum = 0
                    else:
                        firing = True
                elif event.button == 3:
                    if player.heat > 0 and shield <= max_shield and shield > 0:
                        player.heat -= 20
                        player.heat = max(0, player.heat)
                        shield -= 1
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    firing = False
            elif event.type == pg.MOUSEWHEEL:
                current_w = weapon_tuple.index(player.weapon)
                direction = int(math.copysign(1, event.y)) if event.flipped else -int(math.copysign(1, event.y))
                while True:
                    current_w += direction
                    current_w %= len(weapon_tuple)
                    if unlock_dict[weapon_tuple[current_w]]:
                        player.weapon = weapon_tuple[current_w]
                        break
            elif event.type == pg.MOUSEMOTION:
                if next_level:
                    next_level_button.handle_hover(event.pos)
                if game_over:
                    restart_button.handle_hover(event.pos)
                if next_level or game_over:
                    quit_button.handle_hover(event.pos)

        # Update stuff.
        ems = clock.tick()
        dt = ems / 1000.0

        # Move player and do collisions.
        moving_vertical = w ^ s
        moving_horizontal = a ^ d
        if next_level or game_over:
            moving_horizontal = moving_vertical = False
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

        # Update all the mobs and bullets.
        mob_objects.add(player)
        los_lines = []
        for m in mob_objects:
            if m.update(dt, tile_objects, mob_objects, player, bullets, particles):
                los_lines.append(m.rect.center)
        for pb in player_bullets:
            pb.update(dt, tile_objects, mob_objects, pg.mouse.get_pos(), player, camera_shift, particles)
        for b in bullets:
            b.update(dt, tile_objects, mob_objects, pg.mouse.get_pos(), player, camera_shift, particles)
        mob_objects.remove(player)

        # Update particles.
        for p in particles:
            if not p.resolved:
                p.resolved = True
                if p.id is effects.ParticleID.AMMO:
                    ammo_choices = []
                    for i in range(6):
                        if (unlock_dict[weapon_tuple[i]] and
                                ammo_dict[weapon_tuple[i]] < weapons.weapon_max_ammo[weapon_tuple[i]]):
                            ammo_choices.append(i)
                    if ammo_choices:
                        ammo_choice = random.choice(ammo_choices)
                        ammo_dict[weapon_tuple[ammo_choice]] += 10
                        ammo_dict[weapon_tuple[ammo_choice]] = min(weapons.weapon_max_ammo[weapon_tuple[ammo_choice]],
                                                                   ammo_dict[weapon_tuple[ammo_choice]])
                        p.weapon_id = weapon_tuple[ammo_choice]
                    else:
                        p.lifetime = 0
                elif p.id is effects.ParticleID.SPEED:
                    mobs.mob_speed[mobs.MobID.PLAYER] += 2
                elif p.id is effects.ParticleID.COOLING:
                    if shield < max_shield:
                        shield += 1
                    else:
                        p.lifetime = 0
                elif p.id is effects.ParticleID.MAX_HEAT:
                    player.max_heat += 5
                    p_m_heat += 5
                elif p.id is effects.ParticleID.WEAPON_GAIN:
                    if unlock_dict[p.weapon_id]:
                        ammo_dict[p.weapon_id] = weapons.weapon_max_ammo[p.weapon_id]
                    else:
                        unlock_dict[p.weapon_id] = True
            p.update(dt)

        # Detect coolers.
        cooler_count = count_coolers(tile_objects)
        if cooler_count == 0:
            next_level = True
            firing = False

        # Reduce player heat.
        if not next_level:
            decay = (PLAYER_HEAT_DECAY - (PLAYER_FIRE_HEAT_DECAY_PENALTY if firing else 0)
                     - (PLAYER_MOVE_HEAT_DECAY_PENALTY if moving_horizontal or moving_vertical else 0))
            player.heat -= decay * dt
            player.heat = max(0, player.heat)
        if game_over:
            player.heat = player.max_heat

        # Detect game over.
        if player.heat > player.max_heat:
            game_over = True
            firing = False

        # Level timer.
        if game_over or next_level:
            pass
        else:
            run_ms = pg.time.get_ticks() - level_timer_start

        # Run timer.
        if game_over or next_level or current_level == 14:
            run_start += ems
        else:
            run_cum = pg.time.get_ticks() - run_start

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
        if draw_particles:
            for p in particles:
                if p.id is effects.ParticleID.EXPLOSION:
                    expl_img = pg.Surface((p.radius * 2, p.radius * 2)).convert_alpha()
                    expl_img.fill((0, 0, 0, 0))
                    pg.draw.circle(expl_img, (*ORANGE, 128), (p.radius, p.radius), p.radius)
                    screen.blit(expl_img, camera_shift + p.pos - (p.radius, p.radius))
                else:
                    if p.id in (effects.ParticleID.WEAPON_GAIN, effects.ParticleID.AMMO):
                        if p.id is effects.ParticleID.AMMO:
                            text = f"+10 {weapons.weapon_names[p.weapon_id]}"
                        else:
                            text = f"+{weapons.weapon_names[p.weapon_id]}"
                        color = weapons.weapon_color[p.weapon_id]
                    else:
                        text = effects.id_to_text[p.id]
                        color = effects.id_to_color[p.id]
                    p_text = font12.render(text, True, color)
                    screen.blit(p_text, camera_shift + p.pos - (p_text.get_width() // 2, p_text.get_height() // 2))

        # Mouse over text.
        if not firing:
            for mob in mob_objects:
                if mob.rect.move(camera_shift).collidepoint(pg.mouse.get_pos()):
                    help_text = font12.render(" " + mobs.mob_names[mob.id], True, BLACK, WHITE)
                    screen.blit(help_text, camera_shift + mob.rect.midtop - (help_text.get_width() // 2, 15))
                    break
            for tile in tile_objects:
                if tile.rect.move(camera_shift).collidepoint(pg.mouse.get_pos()):
                    help_text = font12.render(" " + tiles.tile_names[tile.id], True, BLACK, WHITE)
                    screen.blit(help_text, camera_shift + tile.rect.midtop - (help_text.get_width() // 2, 15))
                    break

        # Draw debug lines.
        if debug:
            for p in los_lines:
                pg.draw.line(screen, RED, camera_shift + p, camera_shift + player.rect.center)

        # Draw over heating warning.
        if player.heat / player.max_heat > 0.75:
            screen.blit(overheating_surf, (0, 0))

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
            color = weapons.weapon_color[weapon_tuple[i]] if unlock_dict[weapon_tuple[i]] else MED_GRAY
            num_surf = font12.render(f" {i + 1}{" " if i == 0 else ""}", True, BLACK, color)
            screen.blit(num_surf, ((SCREEN_CENTER[0] - (weapon_text_surf.get_width() // 2)) + (i * 13),
                                   weapon_text_surf.get_height() + 4))
        wheel_text_surf = font12.render(" SCROLL TO SWAP", True, BLACK, MED_GRAY)
        screen.blit(wheel_text_surf, (SCREEN_CENTER[0], weapon_text_surf.get_height() + 4))

        # Draw shield meter.
        shield_pct = shield / max_shield
        draw_pct_bar(screen, (20, 60), shield_pct_color(shield_pct), shield_pct)
        shield_text_surf = font24.render(f"COOL: {shield}/{max_shield}", True, BLACK)
        screen.blit(shield_text_surf, (15, 47))
        hint_text = font12.render("E OR RIGHT CLICK TO COOL", True, CYAN)
        screen.blit(hint_text, (25, 77))

        # Draw ammo meter.
        ammo_pct = ammo_dict[player.weapon] / weapons.weapon_max_ammo[player.weapon]
        draw_pct_bar(screen, (SCREEN_SIZE[0] - 220, 20), weapons.weapon_color[player.weapon], ammo_pct)
        if player.weapon is weapons.WeaponID.MINIGUN:
            text = "INFINITE AMMO"
        else:
            text = f"AMMO: {ammo_dict[player.weapon]}/{weapons.weapon_max_ammo[player.weapon]}"
        ammo_text_surf = font24.render(text, True, BLACK)
        screen.blit(ammo_text_surf, (SCREEN_SIZE[0] - 230, 7))
        cooler_text = font12.render(f"LEVEL {current_level} - {cooler_count} COOLERS REMAIN", True, CYAN)
        screen.blit(cooler_text, (SCREEN_SIZE[0] - cooler_text.get_width() - 5, 38))
        cooler_text = font12.render(f"SPEED: {mobs.mob_speed[player.id]}", True, YELLOW)
        screen.blit(cooler_text, (SCREEN_SIZE[0] - cooler_text.get_width() - 5, 50))

        # Level timer.
        x = run_ms // 1000
        run_s = x % 60
        x //= 60
        run_m = x % 60
        x //= 60
        run_h = x % 24
        s_z = "0" if run_s < 10 else ""
        trail = run_ms % 1000
        timer_text = font12.render(f"TIMER: {run_h:0>2}:{run_m:0>2}:{s_z}{run_s}.{trail}", True, GREEN)
        screen.blit(timer_text, (0, SCREEN_SIZE[1] - timer_text.get_height() - 15))

        # Run timer.
        x = run_cum // 1000
        crun_s = x % 60
        x //= 60
        crun_m = x % 60
        x //= 60
        crun_h = x % 24
        cs_z = "0" if crun_s < 10 else ""
        ctrail = run_cum % 1000
        timer_text = font12.render(f"TOTAL: {crun_h:0>2}:{crun_m:0>2}:{cs_z}{crun_s}.{ctrail}", True, GREEN)
        screen.blit(timer_text, (0, SCREEN_SIZE[1] - timer_text.get_height()))

        # Draw the next level screen.
        if next_level:
            screen.blit(next_level_text.get_img(), next_level_text.rect)
            screen.blit(next_level_button.get_img(), next_level_button.rect)
            screen.blit(quit_button.get_img(), quit_button.rect)
            timer_text = font24.render(f" TIMER: {run_h:0>2}:{run_m:0>2}:{s_z}{run_s}.{trail}",
                                       True, BLACK, YELLOW)
            screen.blit(timer_text, (SCREEN_CENTER[0] - timer_text.get_width() // 2, 150))
        # Draw the game over screen.
        elif game_over:
            screen.blit(game_over_text.get_img(), game_over_text.rect)
            screen.blit(restart_button.get_img(), restart_button.rect)
            screen.blit(quit_button.get_img(), quit_button.rect)
            timer_text = font24.render(f" TIMER: {run_h:0>2}:{run_m:0>2}:{s_z}{run_s}.{trail}",
                                       True, BLACK, YELLOW)
            screen.blit(timer_text, (SCREEN_CENTER[0] - timer_text.get_width() // 2, 150))

        # Draw targeting reticule.
        mpos = pg.mouse.get_pos()
        pg.draw.circle(screen, RED, mpos, 8, 1)
        pg.draw.line(screen, RED, (mpos[0], mpos[1] - 4), (mpos[0], mpos[1] - 12), 1)
        pg.draw.line(screen, RED, (mpos[0], mpos[1] + 4), (mpos[0], mpos[1] + 12), 1)
        pg.draw.line(screen, RED, (mpos[0] - 4, mpos[1]), (mpos[0] - 12, mpos[1]), 1)
        pg.draw.line(screen, RED, (mpos[0] + 4, mpos[1]), (mpos[0] + 12, mpos[1]), 1)

        # Show FPS.
        if debug:
            fps_surf = font12.render(f"{int(clock.get_fps())}", True, WHITE, BLACK)
            screen.blit(fps_surf, (SCREEN_SIZE[0] - fps_surf.get_width(), SCREEN_SIZE[1] - fps_surf.get_height()))
        # Update display.
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    main()
