import time  # For controlling the update frequency of the visualization

import gym  # OpenAI Gym library for reinforcement learning environments
import matplotlib.pyplot as plt  # For visualizing the Q-table as a heatmap
import numpy as np  # For numerical operations and creating the Q-table

# Create the training environment (no rendering)
env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=False)

# Create a separate testing environment with rendering enabled (visual output)
test_env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=False, render_mode="human")

# Initialize the Q-table with zeros (states: 0-15, actions: 0-3)
q_table = np.zeros((env.observation_space.n, env.action_space.n))

# Define learning parameters
alpha = 0.3      # Learning rate: how much new info overrides old info
gamma = 0.99     # Discount factor: importance of future rewards
epsilon = 0.5    # Exploration rate: chance to explore instead of exploit
episodes = 3000  # Total number of training episodes

# Set up real-time Q-table visualization using matplotlib
plt.ion()  # Turn on interactive mode for live updating
fig, ax = plt.subplots()
img = ax.imshow(q_table, cmap='coolwarm', interpolation='nearest')  # Display the Q-table as a heatmap
plt.colorbar(img)  # Show color scale
plt.title("Q-Table Heatmap (State x Action)")  # Chart title

# Function to update the heatmap during training
def update_plot():
    img.set_data(q_table)  # Update heatmap data with current Q-table
    ax.set_xlabel("Actions (0:Left, 1:Down, 2:Right, 3:Up)")  # Label x-axis
    ax.set_ylabel("States (0-15)")  # Label y-axis
    fig.canvas.draw()  # Redraw the figure
    fig.canvas.flush_events()  # Flush GUI events to update the window
    time.sleep(0.01)  # Short delay to control update speed

# Training loop for Q-learning
for episode in range(episodes):
    state = env.reset()[0]  # Reset environment and get the initial state
    done = False  # Flag to indicate whether the episode has ended

    while not done:
        # Choose an action using epsilon-greedy policy
        if np.random.rand() < epsilon:
            action = env.action_space.sample()  # Explore: choose random action
        else:
            action = np.argmax(q_table[state])  # Exploit: choose best known action

        # Take the action and observe the outcome
        next_state, reward, done, _, _ = env.step(action)

        # Update the Q-value using the Q-learning formula
        q_table[state, action] = q_table[state, action] + alpha * (
            reward + gamma * np.max(q_table[next_state]) - q_table[state, action]
        )

        # Move to the next state
        state = next_state

    # Update the Q-table heatmap every 100 episodes
    if episode % 100 == 0:
        update_plot()

# Final update of the plot before closing
update_plot()
plt.ioff()  # Turn off interactive plotting mode
plt.show()  # Keep the final plot visible after training ends

# Testing phase: Use the learned Q-table to navigate the environment
state = test_env.reset()[0]  # Reset the test environment
test_env.render()  # Show initial state

# Execute the learned policy for up to 20 steps
for _ in range(20):
    action = np.argmax(q_table[state])  # Choose the best action for the current state
    next_state, reward, done, _, _ = test_env.step(action)  # Perform the action
    test_env.render()  # Show the result visually
    state = next_state  # Move to the next state
    if done:
        break  # Stop if goal is reached or game ends (e.g., falling into a hole)
