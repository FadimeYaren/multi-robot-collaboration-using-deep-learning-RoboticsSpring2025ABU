import random

import matplotlib.animation as animation
import matplotlib.pyplot as plt

GRID_SIZE = 10
TASKS = [(random.randint(0, 9), random.randint(0, 9)) for _ in range(20)]


robots = [
    {'name': 'Robot1', 'pos': [0, 0], 'energy': 100, 'color': 'blue', 'target': None},
    {'name': 'Robot2', 'pos': [9, 9], 'energy': 100, 'color': 'green', 'target': None},
]

charging_stations = [(0, 9), (9, 0)]

def assign_tasks():
    for task in TASKS:
        # Görev zaten atanmışsa geç
        if task in [r['target'] for r in robots if r['target']]:
            continue

        # 📣 Görev duyuruldu — robotlar teklif veriyor
        proposals = []
        for r in robots:
            if r['energy'] > 30 and r['target'] is None:
                distance = abs(r['pos'][0] - task[0]) + abs(r['pos'][1] - task[1])
                bid = distance + 0.3 * (100 - r['energy'])  # teklif = mesafe + enerji kaybı etkisi
                proposals.append((bid, r))

        # 🏆 En iyi teklifi veren robot görevi alır
        if proposals:
            best_bid, best_robot = min(proposals, key=lambda x: x[0])
            best_robot['target'] = task


def move_robot(robot):
    if robot['target']:
        tx, ty = robot['target']
        x, y = robot['pos']
        if x != tx:
            x += 1 if tx > x else -1
        elif y != ty:
            y += 1 if ty > y else -1
        robot['pos'] = [x, y]
        robot['energy'] -= 2
        if [x, y] == [tx, ty]:
            if (tx, ty) in TASKS:
                TASKS.remove((tx, ty))
            robot['target'] = None
    elif robot['energy'] <= 30:
        cs = min(charging_stations, key=lambda c: abs(c[0]-robot['pos'][0]) + abs(c[1]-robot['pos'][1]))
        tx, ty = cs
        x, y = robot['pos']
        if x != tx:
            x += 1 if tx > x else -1
        elif y != ty:
            y += 1 if ty > y else -1
        robot['pos'] = [x, y]
        if [x, y] == [tx, ty]:
            robot['energy'] = 100

fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    ax.set_xlim(-1, GRID_SIZE)
    ax.set_ylim(-1, GRID_SIZE)
    ax.set_title("Battery-aware Task Assignment Simulation")

    for t in TASKS:
        ax.plot(t[0], t[1], 'rx', markersize=12)

    for cs in charging_stations:
        ax.plot(cs[0], cs[1], 'ks', markersize=10)

    assign_tasks()

    for r in robots:
        move_robot(r)
        ax.plot(r['pos'][0], r['pos'][1], 'o', color=r['color'], markersize=12)
        ax.text(r['pos'][0]+0.2, r['pos'][1]+0.2, f"{r['name']}\nE:{r['energy']}")

ani = animation.FuncAnimation(fig, update, frames=100, interval=500, repeat=False)
plt.show()
