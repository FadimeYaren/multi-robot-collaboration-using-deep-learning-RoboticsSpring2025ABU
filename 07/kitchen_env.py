import copy


class KitchenEnv:
    def __init__(self, grid, num_agents=2):
        self.grid = grid
        self.grid_width = len(grid[0])
        self.grid_height = len(grid)
        self.num_agents = num_agents

        self.agent_positions = [[1, 1 + i] for i in range(num_agents)]
        self.agent_dirs = ["move_down"] * num_agents
        self.agent_items = [None for _ in range(num_agents)]

        self.objects_on_map = {}

        self.agent_logs = {f"agent_{i}": [] for i in range(num_agents)}
        self.burger_logs = []
        self.snapshot_logs = []

        self.time_step = 0
        self.terminated = False

    def reset(self):
        self.agent_positions = [[1, 1 + i] for i in range(self.num_agents)]
        self.agent_dirs = ["move_down"] * self.num_agents
        self.agent_items = [None for _ in range(self.num_agents)]
        self.objects_on_map = {}

        self.agent_logs = {f"agent_{i}": [] for i in range(self.num_agents)}
        self.burger_logs = []
        self.snapshot_logs = []

        self.time_step = 0
        self.terminated = False

        return [self.get_state(i) for i in range(self.num_agents)]

    def get_state(self, agent_id):
        pos = self.agent_positions[agent_id]
        onehot_pos = [0] * (self.grid_width * self.grid_height)
        idx = pos[1] * self.grid_width + pos[0]
        onehot_pos[idx] = 1

        item = self.agent_items[agent_id]
        item_types = ["None", "Tomato", "Meat", "Lettuce", "Plate"]
        item_type = item["type"] if item else "None"
        onehot_item = [1 if item_type == t else 0 for t in item_types]


        return onehot_pos + onehot_item

    def step(self, actions):
        rewards = [0.0 for _ in range(self.num_agents)]

        for agent_id, action in enumerate(actions):
            x, y = self.agent_positions[agent_id]
            old_pos = (x, y)

            if action == 0:  # Move Up
                new_pos = (x, y - 1)
            elif action == 1:  # Move Down
                new_pos = (x, y + 1)
            elif action == 2:  # Move Left
                new_pos = (x - 1, y)
            elif action == 3:  # Move Right
                new_pos = (x + 1, y)
            elif action == 4:  # Interact
                rewards[agent_id] += self.handle_interact(agent_id)
                new_pos = (x, y)
            else:
                new_pos = (x, y)  # invalid action

            if (0 <= new_pos[0] < self.grid_width) and (0 <= new_pos[1] < self.grid_height):
                self.agent_positions[agent_id] = list(new_pos)

            self.agent_logs[f"agent_{agent_id}"].append({
                "step": self.time_step,
                "position": self.agent_positions[agent_id],
                "action": action,
                "item": copy.deepcopy(self.agent_items[agent_id])
            })

        self.snapshot_logs.append({
            "step": self.time_step,
            "agents": copy.deepcopy(self.agent_positions),
            "items": copy.deepcopy(self.agent_items),
            "objects": copy.deepcopy(self.objects_on_map)
        })

        self.time_step += 1
        return [self.get_state(i) for i in range(self.num_agents)], rewards, self.is_done(), {}


    def handle_interact(self, agent_id):
        x, y = self.agent_positions[agent_id]
        cell = self.grid[y][x]
        item = self.agent_items[agent_id]
        reward = 0.0

        pos_key = (x, y)
        ground_obj = self.objects_on_map.get(pos_key)

        if item is None and cell in ["T", "B", "TO", "M", "L", "PL"]:
            new_item = self.generate_item_from_station(cell)
            if new_item:
                self.agent_items[agent_id] = new_item
                return 0.2

        if item is None and ground_obj:
            self.agent_items[agent_id] = ground_obj
            del self.objects_on_map[pos_key]
            return 0.2

        if item and cell == "T" and pos_key not in self.objects_on_map:
            self.objects_on_map[pos_key] = item
            self.agent_items[agent_id] = None
            return 0.2

        if item and cell == "C":
            if item["type"] in ["Tomato", "Lettuce"] and item["state"] == "Raw":
                item["state"] = "Chopped"
                return 0.5

        if item and cell == "P":
            if item["type"] == "Meat" and item["state"] == "Raw":
                item["state"] = "Cooked"
                return 0.7

        if item and cell == "X":
            self.agent_items[agent_id] = None
            return -0.2

        if item and ground_obj:
            merged = self.try_merge(item, ground_obj)
            if merged:
                self.objects_on_map[pos_key] = merged
                self.agent_items[agent_id] = None
                return 1.0

        return -0.1


    def generate_item_from_station(self, cell):
        if cell == "B":
            return {"type": "Bread", "state": "Whole"}
        elif cell == "M":
            return {"type": "Meat", "state": "Raw"}
        elif cell == "TO":
            return {"type": "Tomato", "state": "Raw"}
        elif cell == "L":
            return {"type": "Lettuce", "state": "Raw"}
        elif cell == "PL":
            return {"type": "Plate", "state": "Clean", "contents": []}
        return None


    def try_merge(self, item, plate):
        if plate["type"] != "Plate":
            return None
        if "contents" not in plate:
            return None

        if item["type"] in plate["contents"]:
            return None

        mergeable = ["Tomato", "Lettuce", "Meat", "Bread"]
        if item["type"] not in mergeable:
            return None

        if item["type"] in ["Tomato", "Lettuce"] and item["state"] != "Chopped":
            return None
        if item["type"] == "Meat" and item["state"] != "Cooked":
            return None

        new_plate = copy.deepcopy(plate)
        new_plate["contents"].append(item["type"])
        new_plate["contents"] = sorted(new_plate["contents"])

        new_plate["type"] = self.get_plate_type(new_plate["contents"])
        return new_plate


    def get_plate_type(self, contents):
        if not contents:
            return "plate_clean"
        name = "plate_" + "_".join(c.lower() for c in contents)
        if set(contents) == {"Bread", "Tomato", "Lettuce", "Meat"}:
            return "plate_burger"
        return name


    def is_done(self):
        for obj in self.objects_on_map.values():
            if isinstance(obj, dict) and obj.get("type") == "plate_burger":
                self.terminated = True
                return True
        return False


    def get_episode_log(self, episode_id):
        return {
            episode_id: {
                "agent_logs": self.agent_logs,
                "burger_logs": self.burger_logs,
                "snapshots": [
                    {
                        "step": snap["step"],
                        "agents": snap["agents"],
                        "items": snap["items"],
                        "objects": {
                            f"{x},{y}": v
                            for (x, y), v in snap["objects"].items()
                        }
                    }
                    for snap in self.snapshot_logs
                ]
            }
        }
