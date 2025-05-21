import os
import sys

import pygame

# Pygame başlatıcı ayarları
TILE_SIZE = 64
GRID_WIDTH = 10
GRID_HEIGHT = 7
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Renk yedeği (fallback)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (80, 80, 80)

# Sembol-renk haritası (yedek)
tile_colors = {
    "T": (210, 180, 140),  # Tezgah - açık tahta rengi
    "B": (255, 255, 153),  # Bread
    "L": (0, 200, 0),       # Lettuce
    "TO": (255, 102, 102),  # Tomato
    "C": (255, 178, 102),   # Cutting board
    "P": (204, 153, 255),   # Pan
    "M": (139, 69, 19),     # Meat
    "PL": (102, 255, 255),  # Plate
    "D": (102, 178, 255),   # Delivery
    "X": (80, 80, 80),      # Trash
    ".": (255, 255, 255)     # Yürüme alanı
}

# Görsel eşleme (img klasöründen alır)
tile_images = {}
def load_tile_images():
    for symbol in ["B", "L", "TO", "C", "P", "M", "PL", "D", "X"]:
        path = os.path.join("img", f"{symbol}.png")
        if os.path.exists(path):
            image = pygame.image.load(path)
            tile_images[symbol] = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

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
    load_tile_images()

    while True:
        screen.fill(WHITE)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile in tile_images:
                    screen.blit(tile_images[tile], rect)
                else:
                    color = tile_colors.get(tile, DARK_GRAY)
                    pygame.draw.rect(screen, color, rect)

                pygame.draw.rect(screen, BLACK, rect, 1)

                # Sembol yazısı (isteğe bağlı)
                if tile not in tile_images:
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