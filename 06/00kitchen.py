import sys

import pygame

# Ayarlar
TILE_SIZE = 64
GRID_WIDTH = 10
GRID_HEIGHT = 7
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (80, 80, 80)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 140, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)
GRAY = (160, 160, 160)

# Tile renk eşlemeleri
tile_colors = {
    "T": GRAY,
    "B": YELLOW,
    "L": GREEN,
    "TO": RED,
    "C": ORANGE,
    "P": PURPLE,
    "M": BROWN,
    "PL": CYAN,
    "D": BLUE,
    "X": BLACK,
    ".": WHITE
}

# Grid tanımı
grid = [
    ["T", "B", "T", "T", "T", "T", "C", "P", "M", "T"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "D"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "PL"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "P"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "X"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "T"],
    ["T", "T", "T", "L", "TO", "T", "T", "C", "T", "T"],
]

# Oyun döngüsü
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mini Kitchen Environment")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)

    while True:
        screen.fill(WHITE)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = grid[y][x]
                color = tile_colors.get(tile, DARK_GRAY)
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

                # Sembolü çiz
                label = font.render(tile, True, BLACK if color != BLACK else WHITE)
                screen.blit(label, (x * TILE_SIZE + 5, y * TILE_SIZE + 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
