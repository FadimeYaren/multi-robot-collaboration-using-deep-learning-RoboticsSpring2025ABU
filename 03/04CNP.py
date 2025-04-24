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

# 📢 Contract Net Protocol tabanlı görev atama
def assign_tasks():
    for task in TASKS:
        # Görev zaten atanmışsa geç
        if task in [r['target'] for r in robots if r['target']]:
            continue

        print(f"\n📢 Görev duyurusu: {task} koordinatındaki görev robotlara teklif gönderiyor.")

        proposals = []
        for r in robots:
            if r['energy'] > 30 and r['target'] is None:
                distance = abs(r['pos'][0] - task[0]) + abs(r['pos'][1] - task[1])
                bid = distance + 0.3 * (100 - r['energy'])
                proposals.append((bid, r))
                print(f"📝 {r['name']} teklif verdi → Bid: {bid:.2f} | Mesafe: {distance} | Enerji: {r['energy']}")

        if proposals:
            best_bid, best_robot = min(proposals, key=lambda x: x[0])
            best_robot['target'] = task
            print(f"✅ {best_robot['name']} görevi kazandı! ({task}) | Bid: {best_bid:.2f}")

# 🦾 Robot hareketi ve enerji yönetimi
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

# 🎞️ Animasyon
fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    ax.set_xlim(-1, GRID_SIZE)
    ax.set_ylim(-1, GRID_SIZE)
    ax.set_title("CNP-Based Multi-Robot Task Assignment Simulation")

    # Görevleri çiz
    for t in TASKS:
        ax.plot(t[0], t[1], 'rx', markersize=12)

    # Şarj istasyonlarını çiz
    for cs in charging_stations:
        ax.plot(cs[0], cs[1], 'ks', markersize=10)

    # Görev atamasını yap
    assign_tasks()

    # Robotları hareket ettir ve çiz
    for r in robots:
        move_robot(r)
        ax.plot(r['pos'][0], r['pos'][1], 'o', color=r['color'], markersize=12)
        ax.text(r['pos'][0]+0.2, r['pos'][1]+0.2, f"{r['name']}\nE:{r['energy']}")
        if r['target']:
            ax.text(r['target'][0]-0.3, r['target'][1]+0.3, f"{r['name']}", color=r['color'], fontsize=9)

ani = animation.FuncAnimation(fig, update, frames=100, interval=500, repeat=False)
plt.show()
