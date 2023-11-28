import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def objective_function(position, target):
    return np.linalg.norm(position - target)

def plot_swarm(positions, target, iteration, best_distance, bound, target_found, ax):
    ax.clear()
    ax.scatter(positions[:, 0], positions[:, 1], label='UAVs', marker='o', color='blue', s=10)
    if target_found:
        ax.scatter(target[0], target[1], label='Target', marker='x', color='red')
    ax.set_title(f'Iteration {iteration}, Best Distance {best_distance}')
    ax.legend()
    ax.grid(False)
    ax.set_xlim(0, bound)
    ax.set_ylim(0, bound)

def max_magnitude(input_val, max_val=0.5):
    if abs(input_val) > max_val:
        if input_val < 0:
            return -1 * max_val
        return max_val
    return input_val

def generate_path_1(bound, max_velocity, viewing_radius):
    path = []
    current_position = (0, 0)
    path.append(current_position)
    length_of_square = bound / viewing_radius

    while current_position[0] < length_of_square:
        # Move up in the current row
        current_position = (current_position[0], current_position[1] + 1)
        position_in_square = (current_position[0] * max_velocity + max_velocity / 2, current_position[1] * max_velocity + max_velocity / 2)
        path.append(position_in_square)

        # Move down to the next row if at the end
        if current_position[0] == length_of_square:
            current_position = (current_position[0], current_position[1])
            position_in_square = (current_position[0] * max_velocity + max_velocity / 2, current_position[1] * max_velocity + max_velocity / 2)
            path.append(current_position)

    return path

def particle_swarm_optimization_visualized(num_particles, num_dimensions, target, max_iterations=100, c1=2.0, c2=2.0, w=0.3):
    fig, ax = plt.subplots(figsize=(8, 8))

    positions = np.zeros((num_particles, num_dimensions))
    velocities = np.random.rand(num_particles, num_dimensions)
    max_velocity = 2
    bound = 100
    target_found = False
    
    scout_drone_ids = [0, 1, 2, 3]

    personal_best_positions = positions.copy()
    personal_best_values = np.array([objective_function(pos, target) for pos in personal_best_positions])

    global_best_index = np.argmin(personal_best_values)
    global_best_position = personal_best_positions[global_best_index]
    global_best_value = personal_best_values[global_best_index]

    def update(frame):
        nonlocal positions, velocities, personal_best_positions, personal_best_values, global_best_position, global_best_value

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
        plot_swarm(positions, target, frame + 1, lowest_dist, bound, target_found, ax)

    anim = FuncAnimation(fig, update, frames=max_iterations, interval=100, repeat=False)
    plt.show()

    return global_best_position, global_best_value

num_particles = 12
num_dimensions = 2
target = np.random.rand(2) * 100  # Random initialization of the target
best_position, best_value = particle_swarm_optimization_visualized(num_particles, num_dimensions, target)
print(f"Optimal Position: {best_position}, Optimal Value: {best_value}")
