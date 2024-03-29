import sys
from pathlib import Path

import pygame as pg


BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(255, 255, 255)
RED = pg.Color(255, 0, 0)
GREEN = pg.Color(0, 255, 0)
BLUE = pg.Color(0, 0, 255)
CYAN = pg.Color(0, 255, 255)
MAGENTA = pg.Color(255, 0, 255)
YELLOW = pg.Color(255, 255, 0)

SCREEN_SIZE = (800, 600)
SCREEN_TITLE = "Xenoreactor Overload"


def get_screen(size: tuple[int, int], full_screen: bool = True) -> pg.Surface:
    """Return a pygame display surface for rendering."""
    return pg.display.set_mode(size, pg.FULLSCREEN if full_screen else 0)


def main():
    icon_image = pg.Surface((32, 32))
    icon_image.fill(BLACK)
    pg.draw.line(icon_image, CYAN, (8, 4), (24, 28), 3)
    pg.draw.line(icon_image, CYAN, (24, 4), (8, 28), 3)
    pg.display.set_icon(icon_image)
    full_screen = False
    screen = get_screen(SCREEN_SIZE, full_screen)
    pg.display.set_caption(SCREEN_TITLE)
    clock = pg.time.Clock()
    font_path = Path() / "Kenney Future.ttf"
    if font_path.exists():
        font = pg.font.Font(font_path, 12)
    else:
        font = pg.font.Font(None, 12)

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

        # Show FPS.
        fps_surf = font.render(f"{int(clock.get_fps())}", True, WHITE, BLACK)
        screen.blit(fps_surf, (0, 0))
        # Update display.
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    main()
