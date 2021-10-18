import numpy as np
import RL_utils
from itertools import cycle

action_space = RL_utils.action_space
random_iterator = cycle(action_space)

def take_action(scheduler_name,vehicle_location):
    
    if scheduler_name == "cloud":
        return 0

    elif scheduler_name == "random":
        return np.random.randint(0, RL_utils.n_actions)

    elif scheduler_name == "cyclic":
        return next(random_iterator)

    elif scheduler_name == "closer":
        return RL_utils.get_closer_RSU(vehicle_location)["id"]

    else:
        return 0








