import gym  # Import the OpenAI Gym library to access reinforcement learning environments
import numpy as np  # Import NumPy for numerical operations and to create the Q-table

# Create the FrozenLake environment with a non-slippery surface and visual rendering
env = gym.make("FrozenLake-v1", is_slippery=False, render_mode="human")

# Initialize the Q-table with zeros
# The table has dimensions (number of states x number of actions)
q_table = np.zeros((env.observation_space.n, env.action_space.n))

# Define learning parameters
alpha = 0.1      # Learning rate - how much new information overrides old information
gamma = 0.99     # Discount factor - how much future rewards are valued
epsilon = 0.1    # Exploration rate - probability of choosing a random action

# Training loop
for episode in range(1000):  # Train over 1000 episodes
    state = env.reset()[0]  # Reset the environment and get the initial state
    done = False  # A flag to indicate if the episode has ended

    while not done:
        # Choose an action using epsilon-greedy policy
        if np.random.rand() < epsilon:
            action = env.action_space.sample()  # Explore: select a random action
        else:
            action = np.argmax(q_table[state])  # Exploit: select the best known action

        # Take the selected action and observe the result
        next_state, reward, done, _, _ = env.step(action)

        # Update the Q-value using the Q-learning formula
        q_table[state, action] = q_table[state, action] + alpha * (
            reward + gamma * np.max(q_table[next_state]) - q_table[state, action]
        )

        # Move to the next state
        state = next_state

# After training, test the learned Q-table

# Reset the environment and get the starting state
state = env.reset()[0]
env.render()  # Render the initial state

# Run a single episode using the learned policy
for _ in range(20):
    action = np.argmax(q_table[state])  # Select the best action from the Q-table
    next_state, reward, done, _, _ = env.step(action)  # Execute the action
    env.render()  # Render the current state
    state = next_state  # Move to the next state
    if done:
        break  # Stop the episode if the goal is reached or agent falls into a hole
