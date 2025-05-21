import os
import sys

import pygame

# Pygame başlatıcı ayarları
TILE_SIZE = 64
GRID_WIDTH = 10
GRID_HEIGHT = 7
INFO_PANEL_WIDTH = 300
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE + INFO_PANEL_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (80, 80, 80)
LIGHT_GRAY = (220, 220, 220)

# Sembol-renk haritası
tile_colors = {
    "T": (210, 180, 140),
    "B": (255, 255, 153),
    "L": (0, 200, 0),
    "TO": (255, 102, 102),
    "C": (255, 178, 102),
    "P": (204, 153, 255),
    "M": (139, 69, 19),
    "PL": (102, 255, 255),
    "D": (102, 178, 255),
    "X": (80, 80, 80),
    ".": (255, 255, 255)
}

# Görsel eşleme
tile_images = {}
robot_images = {}

def load_tile_images():
    for symbol in ["B", "L", "TO", "C", "P", "M", "PL", "D", "X"]:
        path = os.path.join("img", f"{symbol}.png")
        if os.path.exists(path):
            image = pygame.image.load(path)
            tile_images[symbol] = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

def load_robot_images():
    for direction in ["move_up", "move_down", "move_left", "move_right"]:
        path = os.path.join("img", f"{direction}.png")
        if os.path.exists(path):
            image = pygame.image.load(path)
            robot_images[direction] = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))

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

agent_pos = [1, 1]
agent_item = None  # Yeni: robotun elindeki eşya

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mini Kitchen Environment")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    load_tile_images()
    load_robot_images()
    agent_dir = "move_down"

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

                if tile not in tile_images:
                    label = font.render(tile, True, BLACK if color != BLACK else WHITE)
                    screen.blit(label, (x * TILE_SIZE + 5, y * TILE_SIZE + 5))

        rx, ry = agent_pos
        robot_img = robot_images.get(agent_dir)
        if robot_img:
            screen.blit(robot_img, (rx * TILE_SIZE, ry * TILE_SIZE))

        info_rect = pygame.Rect(GRID_WIDTH * TILE_SIZE, 0, INFO_PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, info_rect)
        pygame.draw.line(screen, BLACK, (GRID_WIDTH * TILE_SIZE, 0), (GRID_WIDTH * TILE_SIZE, WINDOW_HEIGHT), 2)

        screen.blit(font.render("Robot info:", True, BLACK), (GRID_WIDTH * TILE_SIZE + 10, 20))
        screen.blit(font.render(f"Position: {agent_pos}", True, BLACK), (GRID_WIDTH * TILE_SIZE + 10, 50))
        screen.blit(font.render(f"Direction: {agent_dir}", True, BLACK), (GRID_WIDTH * TILE_SIZE + 10, 80))

        item_text = agent_item if agent_item else "Nothing"
        screen.blit(font.render(f"Item: {item_text}", True, BLACK), (GRID_WIDTH * TILE_SIZE + 10, 110))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    agent_dir = "move_up"
                    if ry > 0 and grid[ry - 1][rx] == ".":
                        agent_pos[1] -= 1
                elif event.key == pygame.K_DOWN:
                    agent_dir = "move_down"
                    if ry < GRID_HEIGHT - 1 and grid[ry + 1][rx] == ".":
                        agent_pos[1] += 1
                elif event.key == pygame.K_LEFT:
                    agent_dir = "move_left"
                    if rx > 0 and grid[ry][rx - 1] == ".":
                        agent_pos[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    agent_dir = "move_right"
                    if rx < GRID_WIDTH - 1 and grid[ry][rx + 1] == ".":
                        agent_pos[0] += 1

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
