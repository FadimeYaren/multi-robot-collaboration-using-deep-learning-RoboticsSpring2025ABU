# Multi Robot Collaboration Using Deep Learning - Robotics Spring 2025 ABU
Developers: Fadime Yaren Durmuş & Mustafa Kağan Aytaç | Instructor: Asst. Prof. Deniz Gencaga

# 01:
Multi-robot systems can perform complex tasks that a single robot cannot perform more efficiently and effectively. When equipped with deep learning and communication capabilities, robots can adapt to the environment, learn from experience, and develop collective strategies. These systems can act more flexibly, scalably, and organized with approaches such as swarm intelligence inspired by nature. Robots can share information fully or partially; predetermined strategies can be developed to continue their tasks even in the event of communication interruptions. Task sharing, route planning, and distributed optimization (e.g. ADMM, aggregative optimization) are important issues in this area. In addition, the ability of robots to establish reliable cooperation with humans raises questions about whether principles such as the classic “three laws of robotics” are sufficient today.

# 02:
This report describes how multi-robot systems (MRS) can be made more effective with deep learning. MRS enables robots to coordinate towards a common goal. Centralized and distributed architectures are compared, and the effects of deep learning on perception, decision-making, and task sharing are highlighted. Reinforcement learning (RL) and multi-agent learning (MARL) algorithms are also introduced. The report reviews prominent literature and open source tools, with plans to delve into MARL and implement it on a simple scenario next week.

# 03:
# Robot Grid Environment
    This code implements a simple grid environment for a robot using OpenAI's Gym library.
    The robot can move in a grid, collect tasks, and recharge its energy at charging stations.
    The environment is designed to be used for reinforcement learning tasks.
    The robot starts at the top-left corner of the grid and can move in four directions (up, down, left, right).
    The robot has a limited energy supply and can recharge at designated charging stations.
#
In the codes simultanously, grid system and first environment is created, than some this environment is developed with some algortihms: Auction Based Algorithm and Contact Net Protocol.
And for the same environment, a reinforcement system applied with Q-Learning algorithm. Agent(Thuban) rewarded according to its actions and results(rewards) of each episodes represented with a graph. Also some upper level algorithms are mentioned in the report such as MADDPG (Multi-Agent Deep Deterministic Policy Gradient), QMIX, and MAAC. I said them "upper level" because robot has another feedback mechanism (named critic), it makes robot change its actions according to meaningful self analysis...

# 04:
In the report, reinforcement learning basic concepts are explained. Also, an example (frozenlake) is given as a code.
# FrozenLake Game
Here, the agent learns how to reach the goal in a 4x4 FrozenLake 
map by trial and error. The Q-table stores the expected reward for every 
state-action pair. During training, we visualize the learning progress using a heatmap. 
After training, the agent successfully navigates the environment using the learned optimal 
policy.
