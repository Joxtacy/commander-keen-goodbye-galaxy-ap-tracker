# /// script
# requires-python = ">=3.10"
# dependencies = ["pygame-ce"]
# ///
"""Open a map image and display pixel coordinates on hover/click."""

import sys

import pygame


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "images/map_keen4.png"

    pygame.init()
    img = pygame.image.load(path)
    w, h = img.get_size()

    bar_height = 32
    screen = pygame.display.set_mode((w, h + bar_height))
    pygame.display.set_caption(f"Map Coordinate Picker — {path}")

    font = pygame.font.SysFont("monospace", 18)
    running = True
    coord_text = "x: 0, y: 0"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my < h:
                    coord_text = f"x: {mx}, y: {my}"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if my < h:
                    coord_text = f"x: {mx}, y: {my}"
                    print(coord_text)

        screen.blit(img, (0, 0))
        pygame.draw.rect(screen, (30, 30, 30), (0, h, w, bar_height))
        text_surface = font.render(coord_text, True, (255, 255, 255))
        screen.blit(text_surface, (8, h + 6))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
