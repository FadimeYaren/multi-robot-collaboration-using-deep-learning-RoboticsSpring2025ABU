import os
import random
import shutil

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# === Parameters ===
GRID_SIZE = 8
COOKING_TIME = 3
EPISODES = 3000
MAX_STEPS = 50
DELIVERY_POS = [0, 0]
ORDER_INTERVAL = 20
FRAME_DIR = "frames_full_learning"
VIDEO_NAME = "full_learning_video.mp4"
FPS = 2
ACTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
ALPHA = 0.1
GAMMA = 0.95
EPSILON = 0.3

q_r1 = np.zeros((GRID_SIZE, GRID_SIZE, len(ACTIONS)))
q_r2 = np.zeros((GRID_SIZE, GRID_SIZE, len(ACTIONS)))

OBJECTS = {
    0: 'empty', 1: 'robot1', 2: 'lettuce', 3: 'tomato',
    4: 'meat_raw', 5: 'meat_cooked', 6: 'plate',
    7: 'burger', 8: 'grill', 9: 'pickle',
    10: 'bread_top', 11: 'bread_bottom', 12: 'robot2'
}
REQUIRED = [10, 5, 11]
OPTIONAL = [2, 3, 9]

def create_env():
    env = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    env[6, 1] = 2; env[6, 2] = 3
    env[1, 5] = 4; env[1, 6] = 6
    env[2, 6] = 8; env[5, 3] = 9
    env[0, 3] = 10; env[0, 4] = 11
    return env

def generate_order():
    extras = random.sample(OPTIONAL, random.randint(0, len(OPTIONAL)))
    return sorted(REQUIRED + extras)

def choose_action(pos, q_table):
    y, x = pos
    return np.random.randint(4) if np.random.rand() < EPSILON else np.argmax(q_table[y, x])

def get_reward(env, pos, inv, plate, order, ready, carrying_to_delivery):
    y, x = pos
    obj = env[y, x]
    if obj in order and obj not in inv and len(inv) < 2:
        inv.append(obj); env[y, x] = 0
        return 2, inv, plate, ready, carrying_to_delivery
    elif obj == 8 and 4 in inv:
        return -0.1, inv, plate, ready, carrying_to_delivery
    elif obj == 6 and inv:
        plate.extend(inv); inv.clear()
        if sorted(plate) == order:
            return 5, [], plate, True, True
        elif len(plate) >= len(order):
            return -2, [], [], False, False
        return 1, inv, plate, ready, carrying_to_delivery
    elif ready and [y, x] == DELIVERY_POS:
        return 10, inv, [], False, False
    return -0.1, inv, plate, ready, carrying_to_delivery

def assign_task(robot_name, robot_pos, needed, env, communication_bus):
    best = None; min_dist = float('inf')
    for ing in needed:
        if ing in communication_bus.values() and communication_bus.get(robot_name) != ing:
            continue
        positions = np.argwhere(env == ing)
        for pos in positions:
            dist = abs(pos[0] - robot_pos[0]) + abs(pos[1] - robot_pos[1])
            if dist < min_dist:
                min_dist = dist; best = ing
    if best is not None:
        communication_bus[robot_name] = best
    return best

def render_frame(env, r1, r2, i1, i2, plate, order, step):
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_xlim(0, GRID_SIZE); ax.set_ylim(0, GRID_SIZE); ax.grid(True)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            obj = env[y, x]
            if obj != 0:
                ax.text(x+0.5, GRID_SIZE - y - 0.5, OBJECTS[obj], ha='center', va='center', fontsize=7)
    ax.add_patch(patches.Circle((r1[1]+0.5, GRID_SIZE - r1[0] - 0.5), 0.3, color='blue'))
    ax.add_patch(patches.Circle((r2[1]+0.5, GRID_SIZE - r2[0] - 0.5), 0.3, color='green'))
    ax.add_patch(patches.Rectangle((DELIVERY_POS[1], GRID_SIZE - DELIVERY_POS[0] - 1), 1, 1, fill=False, edgecolor='red', linewidth=2))
    ax.set_title(f"Step {step}\nOrder: {[OBJECTS[i] for i in order]}\nPlate: {[OBJECTS[i] for i in plate]}")
    os.makedirs(FRAME_DIR, exist_ok=True)
    plt.savefig(f"{FRAME_DIR}/frame_{step:03d}.png")
    plt.close()

if os.path.exists(FRAME_DIR):
    shutil.rmtree(FRAME_DIR)

for episode in range(EPISODES):
    env = create_env()
    r1, r2 = [1, 1], [6, 6]; i1, i2 = [], []
    g1 = g2 = 0
    plate = []
    burger_ready = False
    carrying = False
    order_queue = [generate_order()]
    current_order = order_queue[0]

    for step in range(MAX_STEPS):
        if step % ORDER_INTERVAL == 0 and step != 0:
            order_queue.append(generate_order())
            if current_order is None and order_queue:
                current_order = order_queue.pop(0)

        needed = [i for i in current_order if i not in plate and i not in i1 + i2]
        communication_bus = {}
        assign_task('robot1', r1, needed, env, communication_bus)
        assign_task('robot2', r2, needed, env, communication_bus)

        for idx, (r, i, g, q, name) in enumerate([(r1, i1, g1, q_r1, 'robot1'), (r2, i2, g2, q_r2, 'robot2')]):
            y, x = r
            a = choose_action(r, q)
            dy, dx = ACTIONS[a]
            ny, nx = y + dy, x + dx
            if 0 <= ny < GRID_SIZE and 0 <= nx < GRID_SIZE:
                reward, i, plate, burger_ready, carrying = get_reward(env, [ny, nx], i, plate, current_order, burger_ready, carrying)
                if env[ny, nx] == 8 and 4 in i:
                    g += 1
                    if g >= COOKING_TIME:
                        i = [5 if m == 4 else m for m in i]
                        g = 0
                else:
                    g = 0
                max_next = np.max(q[ny, nx])
                q[y, x, a] += ALPHA * (reward + GAMMA * max_next - q[y, x, a])
                if idx == 0:
                    r1, i1, g1 = [ny, nx], i, g
                else:
                    r2, i2, g2 = [ny, nx], i, g
                if reward == 10:
                    current_order = order_queue.pop(0) if order_queue else None
                    plate = []
                    burger_ready = False
                    carrying = False
            else:
                q[y, x, a] += ALPHA * (-1 - q[y, x, a])

        if episode == EPISODES - 1:
            render_frame(env, r1, r2, i1, i2, plate, current_order, step)

np.save("q_table_robot1.npy", q_r1)
np.save("q_table_robot2.npy", q_r2)

image_files = sorted([f"{FRAME_DIR}/{f}" for f in os.listdir(FRAME_DIR) if f.endswith(".png")])
clip = ImageSequenceClip(image_files, fps=FPS)
clip.write_videofile(VIDEO_NAME, codec='libx264')

from google.colab import files

files.download(VIDEO_NAME)
