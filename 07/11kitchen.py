import json
import os
import sys

import pygame

# Settings
episode_id = None
all_logs = {}
burger_logs = []

NUM_AGENTS = 2  # amount of agents
agent_positions = [[1, 1], [1, 2]]
agent_items = [None for _ in range(NUM_AGENTS)]
agent_logs = {f"agent_{i}": [] for i in range(NUM_AGENTS)}
agent_dirs = ["move_down" for _ in range(NUM_AGENTS)]


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

tile_images = {}
robot_images = {}
item_images = {}
objects_on_map = {}





def log_agent_action(agent_id, action_type, position, details=None):
    entry = {
        "step": pygame.time.get_ticks(),
        "position": tuple(position),
        "action": action_type,
        "details": details or {}
    }
    agent_logs[f"agent_{agent_id}"].append(entry)


def load_tile_images():
    for symbol in ["B", "L", "TO", "C", "P", "M", "PL", "D", "X"]:
        path = os.path.join("img", f"{symbol}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
            except pygame.error:
                print(f"Warning: Missing image file {path}")
                continue

            tile_images[symbol] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

def load_robot_images():
    for direction in ["move_up", "move_down", "move_left", "move_right"]:
        path = os.path.join("img", f"{direction}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path)
            except pygame.error:
                print(f"Warning: Missing image file {path}")
                continue

            robot_images[direction] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

def load_item_images():
    folder = os.path.join("img", "items")
    for fname in os.listdir(folder):
        if fname.endswith(".png"):
            key = fname.replace(".png", "")
            path = os.path.join(folder, fname)
            try:
                img = pygame.image.load(path)
            except pygame.error:
                print(f"Warning: Missing image file {path}")
                continue

            item_images[key] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

MERGEABLE_INGREDIENTS = ["meat_cooked", "tomato_chopped", "lettuce_chopped", "bread_whole"]

CHOP_RULES = {
    "tomato_raw": "tomato_chopped",
    "lettuce_raw": "lettuce_chopped"
}


def can_merge(item):
    return item["type"] in MERGEABLE_INGREDIENTS

def can_merge_to_plate(plate, item_type):
    current_types = set(i["type"] for i in plate.get("contents", []))
    
    # if titem added before, you cannot add it again
    if item_type in current_types:
        return False
    
    allowed_types = set(PLATE_MERGE_RULES.get(plate["type"], []))
    return item_type in allowed_types


def combine_plate_contents(contents):
    types = set(item["type"] for item in contents)

    if types == {"bread_whole", "tomato_chopped", "lettuce_chopped", "meat_cooked"}:
        return "plate_burger"
    elif types == {"bread_whole", "lettuce_chopped", "meat_cooked"}:
        return "plate_bread_lettuce_meat"
    elif types == {"bread_whole", "tomato_chopped", "lettuce_chopped"}:
        return "plate_bread_tomato_lettuce"
    elif types == {"bread_whole", "tomato_chopped", "meat_cooked"}:
        return "plate_bread_tomato_meat"
    elif types == {"tomato_chopped", "lettuce_chopped", "meat_cooked"}:
        return "plate_tomato_lettuce_meat"
    elif types == {"bread_whole", "tomato_chopped"}:
        return "plate_bread_tomato"
    elif types == {"bread_whole", "lettuce_chopped"}:
        return "plate_bread_lettuce"
    elif types == {"bread_whole", "meat_cooked"}:
        return "plate_bread_meat"
    elif types == {"tomato_chopped", "lettuce_chopped"}:
        return "plate_tomato_lettuce"
    elif types == {"tomato_chopped", "meat_cooked"}:
        return "plate_tomato_meat"
    elif types == {"lettuce_chopped", "meat_cooked"}:
        return "plate_lettuce_meat"
    elif types == {"bread_whole"}:
        return "plate_bread"
    elif types == {"tomato_chopped"}:
        return "plate_tomato"
    elif types == {"lettuce_chopped"}:
        return "plate_lettuce"
    elif types == {"meat_cooked"}:
        return "plate_meat"
    else:
        return "plate_clean"



PLATE_MERGE_RULES = {
    "plate_clean": ["bread_whole", "tomato_chopped", "lettuce_chopped", "meat_cooked"],
    "plate_meat": ["bread_whole", "tomato_chopped", "lettuce_chopped"],
    "plate_tomato": ["bread_whole", "meat_cooked", "lettuce_chopped"],
    "plate_lettuce": ["bread_whole", "meat_cooked", "tomato_chopped"],
    "plate_bread": ["meat_cooked", "tomato_chopped", "lettuce_chopped"],
    "plate_bread_meat": ["tomato_chopped", "lettuce_chopped"],
    "plate_bread_tomato": ["meat_cooked", "lettuce_chopped"],
    "plate_bread_lettuce": ["meat_cooked", "tomato_chopped"],
    "plate_tomato_lettuce": ["bread_whole", "meat_cooked"],
    "plate_tomato_meat": ["bread_whole", "lettuce_chopped"],
    "plate_lettuce_meat": ["bread_whole", "tomato_chopped"],
    "plate_bread_tomato_lettuce": ["meat_cooked"],
    "plate_bread_tomato_meat": ["lettuce_chopped"],
    "plate_bread_lettuce_meat": ["tomato_chopped"],
    "plate_tomato_lettuce_meat": ["bread_whole"],
    "plate_burger": [] 
}


grid = [
    ["T", "B", "T", "T", "T", "T", "C", "P", "M", "T"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "D"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "PL"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "P"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "X"],
    ["T", ".", ".", ".", ".", ".", ".", ".", ".", "T"],
    ["T", "T", "T", "L", "TO", "T", "T", "C", "T", "T"],
]

def main():
    controlled_agent_id = 0
    global episode_id, all_logs

    log_file = "episode_logs.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            all_logs = json.load(f)
        existing_ids = [int(k.split("_")[1]) for k in all_logs.keys() if k.startswith("episode_")]
        episode_counter = max(existing_ids) + 1 if existing_ids else 1
    else:
        episode_counter = 1
        all_logs = {}

    episode_id = f"episode_{episode_counter:07d}"


    agent_pos = agent_positions[controlled_agent_id]
    agent_item = agent_items[controlled_agent_id]

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mini Kitchen Environment")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    load_tile_images()
    load_robot_images()
    load_item_images()

    agent_dir = "move_down"

    snapshot_logs = []

    while True:
        screen.fill(WHITE)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = grid[y][x]
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile in tile_images:
                    screen.blit(tile_images[tile], rect)
                else:
                    pygame.draw.rect(screen, tile_colors.get(tile, DARK_GRAY), rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

                if (x, y) in objects_on_map:
                    item = objects_on_map[(x, y)]
                    img = item_images.get(item["type"])
                    if img:
                        screen.blit(img, rect)

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

        item_text = agent_item["type"] if agent_item else "Nothing"
        screen.blit(font.render(f"Item: {item_text}", True, BLACK), (GRID_WIDTH * TILE_SIZE + 10, 110))

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                all_logs[episode_id] = {
                    "burger_logs": burger_logs,
                    "agent_logs": agent_logs,
                    "snapshots": snapshot_logs
                }
                with open(log_file, "w") as f:
                    json.dump(all_logs, f, indent=2)


                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    new_pos = list(agent_pos)
                    if event.key == pygame.K_UP:
                        agent_dir = "move_up"; new_pos[1] -= 1
                    elif event.key == pygame.K_DOWN:
                        agent_dir = "move_down"; new_pos[1] += 1
                    elif event.key == pygame.K_LEFT:
                        agent_dir = "move_left"; new_pos[0] -= 1
                    elif event.key == pygame.K_RIGHT:
                        agent_dir = "move_right"; new_pos[0] += 1
                    if 0 <= new_pos[0] < GRID_WIDTH and 0 <= new_pos[1] < GRID_HEIGHT and grid[new_pos[1]][new_pos[0]] == ".":
                        agent_pos[:] = new_pos

                elif event.key == pygame.K_SPACE:
                    fx, fy = agent_pos
                    if agent_dir == "move_up": fy -= 1
                    elif agent_dir == "move_down": fy += 1
                    elif agent_dir == "move_left": fx -= 1
                    elif agent_dir == "move_right": fx += 1

                    if 0 <= fx < GRID_WIDTH and 0 <= fy < GRID_HEIGHT:
                        tile = grid[fy][fx]
                        item_on_tile = objects_on_map.get((fx, fy))

                        if agent_item is None:
                            if item_on_tile:
                                agent_item = item_on_tile
                                del objects_on_map[(fx, fy)]
                                agent_items[controlled_agent_id] = agent_item

                            elif tile == "TO":
                                agent_item = {"type": "tomato_raw"}
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "pickup", (fx, fy), {"item": agent_item["type"]})

                            elif tile == "L":
                                agent_item = {"type": "lettuce_raw"}
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "pickup", (fx, fy), {"item": agent_item["type"]})

                            elif tile == "M":
                                agent_item = {"type": "meat_raw"}
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "pickup", (fx, fy), {"item": agent_item["type"]})

                            elif tile == "B":
                                agent_item = {"type": "bread_whole"}
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "pickup", (fx, fy), {"item": agent_item["type"]})

                            elif tile == "PL":
                                agent_item = {"type": "plate_clean", "contents": []}
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "pickup", (fx, fy), {"item": agent_item["type"]})

                        else:
                            if tile == "C" and agent_item["type"] in CHOP_RULES:
                                previous_type = agent_item["type"]
                                agent_item["type"] = CHOP_RULES[agent_item["type"]]
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "chop", (fx, fy), {"from": previous_type, "to": agent_item["type"]})


                            elif tile == "P" and agent_item["type"] == "meat_raw":
                                agent_item["type"] = "meat_cooked"
                                agent_items[controlled_agent_id] = agent_item
                                log_agent_action(controlled_agent_id, "cook", (fx, fy), {"from": "meat_raw", "to": "meat_cooked"})

                            elif tile in ["X", "D"]:
                                log_agent_action(controlled_agent_id, "discard", (fx, fy), {"item": agent_item["type"]})
                                agent_item = None
                                agent_items[controlled_agent_id] = agent_item



                            elif item_on_tile and "contents" in item_on_tile:
                                plate_type = item_on_tile["type"]
                                held_type = agent_item["type"]
                                if plate_type in PLATE_MERGE_RULES and held_type in PLATE_MERGE_RULES[plate_type]:
                                    current_types = set(i["type"] for i in item_on_tile.get("contents", []))
                                    
                                    
                                    if held_type not in current_types:
                                        item_on_tile["contents"].append(dict(agent_item))
                                        item_on_tile["type"] = combine_plate_contents(item_on_tile["contents"])

                                        # Environment Log: burger_logs
                                        burger_logs.append({
                                            "step": pygame.time.get_ticks(),
                                            "position": (fx, fy),
                                            "plate_type": item_on_tile["type"],
                                            "contents": list(item_on_tile["contents"]),
                                            "ingredients_added_by": [controlled_agent_id], 
                                            "created_by": controlled_agent_id
                                        })

                                        # Agent Log
                                        log_agent_action(controlled_agent_id, "merge_to_plate", (fx, fy), {
                                            "ingredient": held_type,
                                            "plate_type": item_on_tile["type"]
                                        })


                                        agent_item = None
                                        agent_items[controlled_agent_id] = agent_item



                            
                            elif isinstance(agent_item, dict) and "contents" in agent_item and item_on_tile and can_merge(item_on_tile):

                                
                                agent_item["contents"].append(dict(item_on_tile))
                                
                                
                                updated_type = combine_plate_contents(agent_item["contents"])
                                agent_item["type"] = updated_type  

                                
                                new_plate = {
                                    "type": updated_type,
                                    "contents": list(agent_item["contents"])
                                }
                                del objects_on_map[(fx, fy)]
                                objects_on_map[(fx, fy)] = new_plate

                                agent_item = None
                                agent_items[controlled_agent_id] = agent_item





                            
                            elif tile in ["T", "PL"] and (fx, fy) not in objects_on_map:
                                if isinstance(agent_item, dict) and agent_item.get("type") == "plate_clean" and "contents" in agent_item:

                                    updated_type = combine_plate_contents(agent_item["contents"])
                                    objects_on_map[(fx, fy)] = {
                                        "type": updated_type,
                                        "contents": list(agent_item["contents"])
                                    }

                                    # Agent Log: drop
                                    log_agent_action(controlled_agent_id, "drop", (fx, fy), {"item": updated_type})

                                else:
                                    objects_on_map[(fx, fy)] = agent_item

                                    # Agent Log: drop
                                    log_agent_action(controlled_agent_id, "drop", (fx, fy), {"item": agent_item["type"]})

                                agent_item = None
                                agent_items[controlled_agent_id] = agent_item


        snapshot_entry = {
            "step": pygame.time.get_ticks(),
            "agents": [
                {
                    "id": i,
                    "position": agent_positions[i],
                    "item": agent_items[i]["type"] if agent_items[i] else None
                }
                for i in range(NUM_AGENTS)
            ]
        }
        snapshot_logs.append(snapshot_entry)
        

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()

