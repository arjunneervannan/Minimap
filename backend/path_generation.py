import matplotlib.pyplot as plt
import math


def generate_paths(startx, starty, endx, endy, amplitude, direction='horizontal'):
    points = []
    half_amp = amplitude / 2  # Middle of the amplitude

    if direction == 'horizontal':
        # Starting point in the middle of the amplitude horizontally
        x, y = startx + half_amp, starty + half_amp
        points.append((x, y))

        # Zigzag across the specified width
        while y <= endy:
            x = endx - half_amp if x == startx + half_amp else startx + half_amp  # Switch between start and end of width
            points.append((x, y))
            y += amplitude  # Move down by one amplitude
            if y <= endy:  # Check if next point is within the specified bounds
                points.append((x, y))

    elif direction == 'vertical':
        # Starting point in the middle of the amplitude vertically
        x, y = startx + half_amp, starty + half_amp
        points.append((x, y))

        # Zigzag down the specified height
        while x <= endx:
            y = endy - half_amp if y == starty + half_amp else starty + half_amp  # Switch between top and bottom of height
            points.append((x, y))
            x += amplitude  # Move right by one amplitude
            if x <= endx:  # Check if next point is within the specified bounds
                points.append((x, y))

    return points


def visualize_test_paths(points, startx, starty, endx, endy, title='Zigzag Path'):
    plt.figure(figsize=(8, 6))
    # Unzip the points into separate x and y lists
    x_points, y_points = zip(*points)

    # Plot the points and connect them with lines
    plt.plot(x_points, y_points, marker='o', linestyle='-', color='blue')

    # Draw the rectangle around the zigzag path
    rectangle = plt.Rectangle((startx, starty), endx - startx, endy - starty, fill=False, edgecolor='red', linewidth=2)
    plt.gca().add_patch(rectangle)

    # Set plot limits to slightly larger than the rectangle for clarity
    plt.xlim(startx - 5, endx + 5)
    plt.ylim(starty - 5, endy + 5)
    plt.gca().invert_yaxis()  # Invert y-axis to start from top left corner

    # Add titles and labels for clarity
    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)

    # Show the plot
    plt.show()


def feet_to_latlon(feet, current_lat):
    # Constants
    feet_per_mile = 5280
    miles_per_degree_lat = 69

    # Convert feet to miles
    miles = feet / feet_per_mile

    # Calculate change in latitude
    delta_lat = miles / miles_per_degree_lat

    # Calculate change in longitude, adjusting for current latitude
    # Cosine requires radians, so convert current latitude from degrees to radians
    current_lat_rad = math.radians(current_lat)
    miles_per_degree_lon = miles_per_degree_lat * math.cos(current_lat_rad)
    delta_lon = miles / miles_per_degree_lon

    return delta_lat, delta_lon


def test_paths():
    # Example usage with start and end coordinates:
    points_horizontal_centered = generate_paths(startx=15, starty=20, endx=100, endy=50,
                                                amplitude=10, direction='horizontal')
    points_vertical_centered = generate_paths(startx=15, starty=20, endx=100, endy=50,
                                              amplitude=10, direction='vertical')

    print("Centered Horizontal Zigzag Points:", points_horizontal_centered)
    print("Centered Vertical Zigzag Points:", points_vertical_centered)

    print("Centered Horizontal Zigzag Points:", points_horizontal_centered)
    print("Centered Vertical Zigzag Points:", points_vertical_centered)

    # Assuming you have the points from the previous example
    visualize_test_paths(points_horizontal_centered, startx=15, starty=20, endx=100, endy=50,
                         title='Horizontal Zigzag Path with Rectangle')
    visualize_test_paths(points_vertical_centered, startx=15, starty=20, endx=100, endy=50,
                         title='Vertical Zigzag Path with Rectangle')


# Example usage
delta_lat, delta_lon = feet_to_latlon(5280, 39.9546186)  # 5280 feet at 45 degrees latitude
print(f"Change in Latitude: {delta_lat} degrees")
print(f"Change in Longitude: {delta_lon} degrees")
