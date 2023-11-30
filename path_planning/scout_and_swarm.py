import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def objective_function(position, target):
    return np.linalg.norm(position - target)

def plot_swarm(scout_positions, positions, target, iteration, best_distance, bound, target_found, ax):
    ax.clear()
    ax.scatter(scout_positions[:, 0], scout_positions[:, 1], label='Scout UAVs', marker='o', color='green', s=10)
    ax.scatter(positions[:, 0], positions[:, 1], label='Wolfpack UAVs', marker='o', color='blue', s=10)
    if target_found:
        ax.scatter(target[0], target[1], label='Target', marker='x', color='red')
    ax.set_title(f'Iteration {iteration}, Target Found: {target_found}')
    ax.legend()
    ax.grid(False)
    ax.set_xlim(0, bound)
    ax.set_ylim(0, bound)

def convert_square_coord_to_position(current_position, max_velocity):
    position_in_square = (current_position[0] * max_velocity + max_velocity / 2, current_position[1] * max_velocity + max_velocity / 2)
    return position_in_square


def double_path_size(path):
    test = path[::-1]
    return path + test
    

def generate_path_1(bound, max_velocity, viewing_radius):
    path = []
    current_position = (0, 0)
    path.append(current_position)
    length_of_square = int(bound / viewing_radius)
    
    for x_pos in range(0, length_of_square):
        for y_pos in range(0, length_of_square):
            parity = x_pos % 2
            if parity == 0:
                current_position = (x_pos, y_pos)
            else:
                current_position = (x_pos, length_of_square - y_pos - 1)
            position_in_square = convert_square_coord_to_position(current_position, max_velocity)
            path.append(position_in_square)

    return path


def generate_path_2(bound, max_velocity, viewing_radius):
    path = []
    current_position = (0, 0)
    path.append(current_position)
    length_of_square = int(bound / viewing_radius)
    
    for y_pos in range(0, length_of_square):
        for x_pos in range(0, length_of_square):
            parity = y_pos % 2
            if parity == 0:
                current_position = (x_pos, y_pos)
            else:
                current_position = (length_of_square - x_pos - 1, y_pos)
            position_in_square = convert_square_coord_to_position(current_position, max_velocity)
            path.append(position_in_square)

    return path


def check_if_target_found(scout_positions, target, viewing_radius):
    for drone_id in range(len(scout_positions)):
        fitness = objective_function(scout_positions[drone_id], target)
        if fitness < viewing_radius:
            return True
    return False

def generate_diagonal_path(bound, max_velocity, viewing_radius):
    path = []
    current_position = (0, 0)
    path.append(current_position)
    length_of_square = int(bound / viewing_radius)
    solution=[[] for i in range(2 * length_of_square - 1)]
    
    for x_pos in range(0, length_of_square):
        for y_pos in range(0, length_of_square):
            sum = x_pos + y_pos
            current_position = (x_pos, y_pos)
            if(sum % 2 ==0):
                #add at beginning
                solution[sum].insert(0,current_position)
            else:
                #add at end of the list
                solution[sum].append(current_position)

    # print the solution as it as
    for i in solution:
        for j in i:
            path.append(convert_square_coord_to_position(j, max_velocity))
    return path

def generate_diagonal_path_2(bound, max_velocity, viewing_radius):
    path = []
    current_position = (0, 0)
    path.append(current_position)
    length_of_square = int(bound / viewing_radius)
    solution=[[] for i in range(2 * length_of_square - 1)]
    
    for y_pos in range(0, length_of_square):
        for x_pos in range(0, length_of_square):
            sum = x_pos + y_pos
            current_position = (x_pos, y_pos)
            if(sum % 2 ==0):
                #add at beginning
                solution[sum].insert(0,current_position)
            else:
                #add at end of the list
                solution[sum].append(current_position)

    # print the solution as it as
    for i in solution:
        for j in i:
            path.append(convert_square_coord_to_position(j, max_velocity))
    return path

def generate_spiral_path(bound, max_velocity, viewing_radius):
    result = []
    current_position = (0, 0)
    length_of_square = int(bound / viewing_radius)
    result.append(current_position)

    direction = 0
    top, bottom, left, right = 0, length_of_square - 1, 0, length_of_square - 1

    count = 1

    while top <= bottom and left <= right:
        if direction == 0:  # Traverse right
            for i in range(left, right + 1):
                result.append(convert_square_coord_to_position((top, i), max_velocity))
                count += 1
            top += 1

        elif direction == 1:  # Traverse down
            for i in range(top, bottom + 1):
                result.append(convert_square_coord_to_position((i, right), max_velocity))
                count += 1
            right -= 1

        elif direction == 2:  # Traverse left
            for i in range(right, left - 1, -1):
                result.append(convert_square_coord_to_position((bottom, i), max_velocity))
                count += 1
            bottom -= 1

        elif direction == 3:  # Traverse up
            for i in range(bottom, top - 1, -1):
                result.append(convert_square_coord_to_position((i, left), max_velocity))
                count += 1
            left += 1

        direction = (direction + 1) % 4

    return result

def particle_swarm_optimization_visualized(num_particles, num_dimensions, target, max_iterations=2000, c1=1.0, c2=2.0, w=0.8):
    fig, ax = plt.subplots(figsize=(8, 8))
    scout_drone_ids = [0, 1, 2, 3, 4]
    
    scout_positions = np.zeros((len(scout_drone_ids), num_dimensions))

    positions = np.zeros((num_particles, num_dimensions))
    velocities = np.random.rand(num_particles, num_dimensions)
    max_velocity = 2
    bound = 100
    target_found = False
    path_1 = generate_path_1(bound, max_velocity, max_velocity)
    path_2 = generate_path_2(bound, max_velocity, max_velocity)
    path_3 = generate_diagonal_path(bound, max_velocity, max_velocity)
    path_4 = generate_diagonal_path_2(bound, max_velocity, max_velocity)
    path_5 = generate_spiral_path(bound, max_velocity, max_velocity)
    
    path_1_full = double_path_size(double_path_size(path_1))
    path_2_full = double_path_size(double_path_size(path_2))
    path_3_full = double_path_size(double_path_size(path_3))
    path_4_full = double_path_size(double_path_size(path_4))
    path_5_full = double_path_size(double_path_size(path_5))
    
    all_paths = [path_1_full, path_2_full, path_3_full, path_4_full, path_5_full]
    
    personal_best_positions = positions.copy()
    personal_best_values = np.array([objective_function(pos, target) for pos in personal_best_positions])

    global_best_index = np.argmin(personal_best_values)
    global_best_position = personal_best_positions[global_best_index]
    global_best_value = personal_best_values[global_best_index]
    path_index = 0

    def update(frame):
        nonlocal positions, velocities, personal_best_positions, personal_best_values, global_best_position, global_best_value, target_found, max_velocity, path_index
        
        if (not target_found):
            for drone_id in scout_drone_ids:
                scout_positions[drone_id] = all_paths[drone_id][path_index]
            path_index += 1
            target_found = check_if_target_found(scout_positions, target, max_velocity)
        else:
            for drone_id in scout_drone_ids:
                scout_positions[drone_id] = all_paths[drone_id][path_index]
            path_index += 1
            for drone_id in range(num_particles):
                r1, r2 = np.random.rand(), np.random.rand()
                velocities[drone_id] = w * velocities[drone_id] + c1 * r1 * (personal_best_positions[drone_id] - positions[drone_id]) + \
                                c2 * r2 * (global_best_position - positions[drone_id])
                normalized_velocity = max_velocity * velocities[drone_id]/np.linalg.norm(velocities[drone_id])
                
                positions[drone_id] = positions[drone_id] + normalized_velocity

                fitness = objective_function(positions[drone_id], target)

                if fitness < personal_best_values[drone_id]:
                    personal_best_values[drone_id] = fitness
                    personal_best_positions[drone_id] = positions[drone_id]

                if fitness < global_best_value:
                    global_best_value = fitness
                    global_best_position = positions[drone_id]

        print(f"Iteration {frame + 1}: Best Fitness = {global_best_value}")
        lowest_dist = np.linalg.norm(global_best_position - target)
        plot_swarm(scout_positions, positions, target, frame + 1, lowest_dist, bound, target_found, ax)

    anim = FuncAnimation(fig, update, frames=max_iterations, interval=1, repeat=False)
    plt.show()

    return global_best_position, global_best_value

num_particles = 7
num_dimensions = 2
# target = np.random.rand(2) * 100  # Random initialization of the target
target = (30, 30)
best_position, best_value = particle_swarm_optimization_visualized(num_particles, num_dimensions, target)
print(f"Optimal Position: {best_position}, Optimal Value: {best_value}")
