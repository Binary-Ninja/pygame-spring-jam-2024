import sys
from pathlib import Path

import pygame as pg

from colors import *
import maps
import tiles
import images


SCREEN_SIZE = (800, 600)
SCREEN_TITLE = "Xenoreactor Overload"


def get_screen(size: tuple[int, int], full_screen: bool = True) -> pg.Surface:
    """Return a pygame display surface for rendering."""
    return pg.display.set_mode(size, pg.FULLSCREEN if full_screen else 0)


id_to_image_id = {
    tiles.TileID.WALL: images.ImageID.WALL,
}


def get_image(enum_id) -> pg.Surface:
    return images.image_dict[id_to_image_id[enum_id]]


def load_map(map_str: str) -> list[tiles.Tile]:
    tile_objects = []
    x = y = 0
    for char in map_str.strip("\n"):
        if char == "\n":
            # Go down to the next row.
            x = 0
            y += images.TILE_SIZE[1]
            continue
        if char in tiles.char_to_tile_id.keys():
            tile_objects.append(tiles.Tile((x, y), char))
        x += images.TILE_SIZE[0]
    return tile_objects


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
    tile_objects = load_map(maps.TESTING)

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

        # Update stuff.
        clock.tick()

        # Draw stuff.
        screen.fill(BLACK)

        # Draw map tiles.
        for tile in tile_objects:
            # Don't draw if tile is off the screen.
            if tile.pos[0] < -images.TILE_SIZE[0]:
                continue
            if tile.pos[0] > SCREEN_SIZE[0]:
                continue
            if tile.pos[1] < -images.TILE_SIZE[1]:
                continue
            if tile.pos[1] > SCREEN_SIZE[1]:
                continue
            # Draw the tile.
            screen.blit(get_image(tile.id), tile.pos)

        # Show FPS.
        fps_surf = font.render(f"{int(clock.get_fps())}", True, WHITE, BLACK)
        screen.blit(fps_surf, (0, 0))
        # Update display.
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    main()
