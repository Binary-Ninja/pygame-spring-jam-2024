import sys
from pathlib import Path

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

PLAYER_SPEED = 80


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


id_to_image_id = {
    tiles.TileID.WALL: images.ImageID.WALL,
    mobs.MobID.PLAYER: images.ImageID.PLAYER,
}


def get_image(enum_id) -> pg.Surface:
    return images.image_dict[id_to_image_id[enum_id]]


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
    # Make the images.
    images.make_images()
    # Set up game world.
    tile_objects, mob_objects = load_map(maps.TESTING)
    bullets = pg.sprite.Group()
    # Find the player.
    player = find_player(mob_objects)
    max_shield = 100
    shield = 100
    # Key events.
    w = s = a = d = firing = False

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
                firing = True
            elif event.type == pg.MOUSEBUTTONUP:
                firing = False

        # Update stuff.
        dt = clock.tick() / 1000.0

        # Move player and do collisions.
        moving_vertical = w ^ s
        moving_horizontal = a ^ d
        amount = PLAYER_SPEED * dt * (0.707 if moving_horizontal and moving_vertical else 1)
        if moving_vertical:
            if w:
                player.pos.y -= amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.top = hit.rect.bottom
                    player.pos.y = hit.rect.bottom
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.top = hit.rect.bottom
                    player.pos.y = hit.rect.bottom
            if s:
                player.pos.y += amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.bottom = hit.rect.top
                    player.pos.y = hit.rect.top - player.rect.height
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.bottom = hit.rect.top
                    player.pos.y = hit.rect.top - player.rect.height
        if moving_horizontal:
            if a:
                player.pos.x -= amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.left = hit.rect.right
                    player.pos.x = hit.rect.right
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.left = hit.rect.right
                    player.pos.x = hit.rect.right
            if d:
                player.pos.x += amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    player.rect.right = hit.rect.left
                    player.pos.x = hit.rect.left - player.rect.width
                if hit := pg.sprite.spritecollideany(player, mob_objects):
                    player.rect.right = hit.rect.left
                    player.pos.x = hit.rect.left - player.rect.width

        # Update all the mobs.
        player.update()
        mob_objects.update()

        # Draw stuff.
        screen.fill(BLACK)

        # Camera math.
        camera_shift = pg.Vector2(int_vec(SCREEN_CENTER - player.rect.center))

        # Draw map tiles.
        for tile in tile_objects:
            screen.blit(tile.image, camera_shift + tile.rect.topleft)

        # Draw mobs.
        for mob in mob_objects:
            screen.blit(mob.image, camera_shift + mob.rect.topleft)
        screen.blit(player.image, camera_shift + player.rect.topleft)

        # Draw UI.

        # Draw heat meter.
        heat_pct = player.heat / player.max_heat
        draw_pct_bar(screen, (20, 20), heat_pct_color(heat_pct), heat_pct)
        heat_text_surf = font24.render(f"HEAT: {player.heat}/{player.max_heat}", True, BLACK)
        screen.blit(heat_text_surf, (20, 8))

        # Draw current weapon.
        weapon_text_surf = font24.render(f" WEAPON: {weapons.weapon_names[player.weapon]}", True, BLACK,
                                         weapons.weapon_color[player.weapon])
        screen.blit(weapon_text_surf, (SCREEN_CENTER[0] - (weapon_text_surf.get_width() // 2), 8))

        # Draw shield meter.
        shield_pct = shield / max_shield
        draw_pct_bar(screen, (SCREEN_SIZE[0] - 220, 20), shield_pct_color(shield_pct), shield_pct)
        shield_text_surf = font24.render(f"COOL: {shield}/{max_shield}", True, BLACK)
        screen.blit(shield_text_surf, (SCREEN_SIZE[0] - 220, 8))

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
