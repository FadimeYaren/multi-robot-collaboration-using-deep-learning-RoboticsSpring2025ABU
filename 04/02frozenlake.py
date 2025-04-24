import time

import gym
import matplotlib.pyplot as plt
import numpy as np

env = gym.make("FrozenLake-v1", is_slippery=False, render_mode="human")
q_table = np.zeros((env.observation_space.n, env.action_space.n))

alpha = 0.1
gamma = 0.99
epsilon = 0.1

# Set up matplotlib for real-time updating
plt.ion()
fig, ax = plt.subplots()
img = ax.imshow(q_table, cmap='coolwarm', interpolation='nearest')
plt.colorbar(img)
plt.title("Q-Table Heatmap (State x Action)")

def update_plot():
    img.set_data(q_table)
    fig.canvas.draw()
    fig.canvas.flush_events()
    time.sleep(0.05)

# Training
for episode in range(1000):
    state = env.reset()[0]
    done = False

    while not done:
        if np.random.rand() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state])

        next_state, reward, done, _, _ = env.step(action)

        q_table[state, action] = q_table[state, action] + alpha * (
            reward + gamma * np.max(q_table[next_state]) - q_table[state, action]
        )

        state = next_state

        # Update the plot every few episodes or steps
        update_plot()


# Final Q-table visualization
update_plot()
plt.ioff()
plt.show()
