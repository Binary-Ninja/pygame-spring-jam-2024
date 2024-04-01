import sys
from pathlib import Path

import pygame as pg

from colors import *
import maps
import tiles
import mobs
import images


SCREEN_SIZE = (800, 600)
SCREEN_CENTER = pg.Vector2(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
SCREEN_TITLE = "Xenoreactor Overload"

PLAYER_SPEED = 80


def get_screen(size: tuple[int, int], full_screen: bool = True) -> pg.Surface:
    """Return a pygame display surface for rendering."""
    return pg.display.set_mode(size, pg.FULLSCREEN if full_screen else 0)


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
            return mob
    else:
        p = mobs.Mob((0, 0), "@")
        mob_objects.add(p)
        return p


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
    if font_path.exists():
        font = pg.font.Font(font_path, 12)
    else:
        font = pg.font.Font(None, 12)
    # Make the images.
    images.make_images()
    # Set up game world.
    tile_objects, mob_objects = load_map(maps.TESTING)
    # Find the player.
    player = find_player(mob_objects)
    # Key events.
    w = s = a = d = False

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                elif event.key == pg.K_w:
                    w = True
                elif event.key == pg.K_s:
                    s = True
                elif event.key == pg.K_a:
                    a = True
                elif event.key == pg.K_d:
                    d = True
            elif event.type == pg.KEYUP:
                if event.key == pg.K_w:
                    w = False
                elif event.key == pg.K_s:
                    s = False
                elif event.key == pg.K_a:
                    a = False
                elif event.key == pg.K_d:
                    d = False

        # Update stuff.
        dt = clock.tick() / 1000.0

        # Move player.
        moving_vertical = w ^ s
        moving_horizontal = a ^ d
        amount = PLAYER_SPEED * dt * (0.707 if moving_horizontal and moving_vertical else 1)
        if moving_vertical:
            if w:
                player.pos.y -= amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    # player.pos.y += amount
                    player.rect.top = hit.rect.bottom
                    player.pos.y = hit.rect.bottom
            if s:
                player.pos.y += amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    # player.pos.y -= amount
                    player.rect.bottom = hit.rect.top
                    player.pos.y = hit.rect.top - player.rect.height
        if moving_horizontal:
            if a:
                player.pos.x -= amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    # player.pos.x += amount
                    player.rect.left = hit.rect.right
                    player.pos.x = hit.rect.right
            if d:
                player.pos.x += amount
                player.update()
                if hit := pg.sprite.spritecollideany(player, tile_objects):
                    # player.pos.x -= amount
                    player.rect.right = hit.rect.left
                    player.pos.x = hit.rect.left - player.rect.width

        # Update all the mobs.
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

        # Draw targeting reticule.
        mpos = pg.mouse.get_pos()
        pg.draw.circle(screen, RED, mpos, 8, 1)
        pg.draw.line(screen, RED, (mpos[0], mpos[1] - 4), (mpos[0], mpos[1] - 12), 1)
        pg.draw.line(screen, RED, (mpos[0], mpos[1] + 4), (mpos[0], mpos[1] + 12), 1)
        pg.draw.line(screen, RED, (mpos[0] - 4, mpos[1]), (mpos[0] - 12, mpos[1]), 1)
        pg.draw.line(screen, RED, (mpos[0] + 4, mpos[1]), (mpos[0] + 12, mpos[1]), 1)

        # Show FPS.
        fps_surf = font.render(f"{int(clock.get_fps())}", True, WHITE, BLACK)
        screen.blit(fps_surf, (0, 0))
        # Update display.
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    main()
