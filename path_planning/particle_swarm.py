import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def objective_function(position, target):
    return np.linalg.norm(position - target)

def plot_swarm(positions, target, iteration, best_distance, acceptable_radius, ax):
    ax.clear()
    ax.scatter(positions[:, 0], positions[:, 1], label='UAVs', marker='o', color='blue', s=10)
    ax.scatter(target[0], target[1], label='Target', marker='x', color='red')
    ax.set_title(f'Iteration {iteration}, Best Distance {best_distance}')
    ax.legend()
    ax.grid(False)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

def max_magnitude(input_val, max_val=0.5):
    if abs(input_val) > max_val:
        if input_val < 0:
            return -1 * max_val
        return max_val
    return input_val

def particle_swarm_optimization_visualized(num_particles, num_dimensions, target, max_iterations=100, c1=2.0, c2=2.0, w=0.3):
    fig, ax = plt.subplots(figsize=(8, 8))

    positions = np.zeros((num_particles, num_dimensions))
    velocities = np.random.rand(num_particles, num_dimensions)
    max_velocity = 2
    acceptable_radius = 4

    personal_best_positions = positions.copy()
    personal_best_values = np.array([objective_function(pos, target) for pos in personal_best_positions])

    global_best_index = np.argmin(personal_best_values)
    global_best_position = personal_best_positions[global_best_index]
    global_best_value = personal_best_values[global_best_index]

    def update(frame):
        nonlocal positions, velocities, personal_best_positions, personal_best_values, global_best_position, global_best_value

        for i in range(num_particles):
            r1, r2 = np.random.rand(), np.random.rand()
            velocities[i] = w * velocities[i] + c1 * r1 * (personal_best_positions[i] - positions[i]) + \
                            c2 * r2 * (global_best_position - positions[i])
            normalized_velocity = max_velocity * velocities[i]/np.linalg.norm(velocities[i])

            positions[i] = positions[i] + normalized_velocity

            fitness = objective_function(positions[i], target)

            if fitness < personal_best_values[i]:
                personal_best_values[i] = fitness
                personal_best_positions[i] = positions[i]

            if fitness < global_best_value:
                global_best_value = fitness
                global_best_position = positions[i]

        print(f"Iteration {frame + 1}: Best Fitness = {global_best_value}")
        lowest_dist = np.linalg.norm(global_best_position - target)
        plot_swarm(positions, target, frame + 1, lowest_dist, acceptable_radius, ax)

    anim = FuncAnimation(fig, update, frames=max_iterations, interval=100, repeat=False)
    plt.show()

    return global_best_position, global_best_value

num_particles = 12
num_dimensions = 2
target = np.random.rand(2) * 100  # Random initialization of the target
best_position, best_value = particle_swarm_optimization_visualized(num_particles, num_dimensions, target)
print(f"Optimal Position: {best_position}, Optimal Value: {best_value}")