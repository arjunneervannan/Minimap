import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import numpy as np


def old_generate_paths(startx, starty, endx, endy, amplitude, direction='horizontal'):
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


def generate_paths(startx, starty, endx, endy, x_home, y_home, amplitude, direction='horizontal'):
    points = generate_rectangle_paths(startx, starty, endx, endy, amplitude, direction)

    outside_point = generate_outside_point(startx, starty, endx, endy, points[-1][0], points[-1][1], amplitude)
    points.append(outside_point)
    home_sequence = go_home(outside_point[0], outside_point[1], x_home, y_home, startx, starty, endx, endy)
    points.extend(home_sequence)
    return points


def generate_outside_point(startx, starty, endx, endy, last_pointx, last_pointy, amplitude):
    corner, _ = closest_corner(last_pointx, last_pointy, startx, starty, endx, endy)

    move_x_direction = 0
    move_y_direction = 0

    if corner == "top right":
        move_x_direction = amplitude
        move_y_direction = amplitude
    elif corner == "top left":
        move_x_direction = -amplitude
        move_y_direction = amplitude
    elif corner == "bottom right":
        move_x_direction = amplitude
        move_y_direction = -amplitude
    elif corner == "bottom left":
        move_x_direction = -amplitude
        move_y_direction = -amplitude

    # Calculate new point
    new_x = last_pointx + move_x_direction
    new_y = last_pointy + move_y_direction

    return new_x, new_y


def closest_corner(x, y, startx, starty, endx, endy):
    # Determine corners with corresponding labels
    corners = {
        (min(startx, endx), min(starty, endy)): "bottom left",
        (min(startx, endx), max(starty, endy)): "top left",
        (max(startx, endx), min(starty, endy)): "bottom right",
        (max(startx, endx), max(starty, endy)): "top right"
    }

    # Calculate the Euclidean distance to each corner
    def distance(point1, point2):
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    # Find the corner with the minimum distance to the point (x, y)
    closest = min(corners.keys(), key=lambda corner: distance(corner, (x, y)))

    # Return the description of the closest corner
    return corners[closest], closest


def generate_rectangle_paths(startx, starty, endx, endy, amplitude, direction='horizontal'):
    points = []
    half_amp = amplitude / 2  # Middle of the amplitude

    # Determine movement direction and adjustment for coordinates
    x_step = amplitude if startx <= endx else -amplitude
    y_step = amplitude if starty <= endy else -amplitude

    if direction == 'horizontal':
        # Start with x initially set based on direction
        x = startx + half_amp if startx <= endx else startx - half_amp
        y = starty + half_amp if starty <= endy else starty - half_amp
        points.append((x, y))

        # Toggle x between startx + half_amp and endx - half_amp or vice versa
        while (y - starty) * y_step <= (endy - starty) * y_step:
            x = (endx - half_amp if x == startx + half_amp else startx + half_amp) if startx <= endx \
                else (endx + half_amp if x == startx - half_amp else startx - half_amp)
            points.append((x, y))
            y += y_step
            if (y - starty) * y_step <= (endy - starty) * y_step:
                points.append((x, y))

    elif direction == 'vertical':
        # Start with y initially set based on direction
        x = startx + half_amp if startx <= endx else startx - half_amp
        y = starty + half_amp if starty <= endy else starty - half_amp
        points.append((x, y))

        # Toggle y between starty + half_amp and endy - half_amp or vice versa
        while (x - startx) * x_step <= (endx - startx) * x_step:
            y = (endy - half_amp if y == starty + half_amp else starty + half_amp) if starty <= endy \
                else (endy + half_amp if y == starty - half_amp else starty - half_amp)
            points.append((x, y))
            x += x_step
            if (x - startx) * x_step <= (endx - startx) * x_step:
                points.append((x, y))

    return points


def go_home(x1, y1, x2, y2, startx, starty, endx, endy):
    def line_intersects_rect(p1, p2, r):
        """Check if line segment p1-p2 intersects with rectangle r."""
        r_minx, r_miny = min(r[0], r[2]), min(r[1], r[3])
        r_maxx, r_maxy = max(r[0], r[2]), max(r[1], r[3])
        # Rectangle sides
        rect_sides = [
            ((r_minx, r_miny), (r_maxx, r_miny)),  # Bottom side
            ((r_maxx, r_miny), (r_maxx, r_maxy)),  # Right side
            ((r_maxx, r_maxy), (r_minx, r_maxy)),  # Top side
            ((r_minx, r_maxy), (r_minx, r_miny))   # Left side
        ]
        for rect_side in rect_sides:
            if segments_intersect(p1, p2, rect_side[0], rect_side[1]):
                return True
        return False

    def segments_intersect(p1, p2, p3, p4):
        """Return True if line segments p1-p2 and p3-p4 intersect."""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    # Define the rectangle
    rectangle = (startx, starty, endx, endy)

    r_minx, r_miny = min(startx, endx), min(starty, endy)
    r_maxx, r_maxy = max(startx, endx), max(starty, endy)
    if r_minx <= x2 <= r_maxx and r_miny <= y2 <= r_maxy:
        return [(x1, y1), (x2, y2)]

    # Check if line intersects with rectangle
    if line_intersects_rect((x1, y1), (x2, y2), rectangle):

        # Determine reroute path around the rectangle
        waypoints = []
        # Simply going to add waypoints around the rectangle at the corners
        if y2 > max(starty, endy):
            # Pass above the rectangle
            waypoints = [(x1, y1), (x1, max(starty, endy)), (x2, y2)]
        elif y2 < min(starty, endy):
            # Pass below the rectangle
            waypoints = [(x1, y1), (x1, min(starty, endy)), (x2, y2)]
        else:
            # Pass through the sides of the rectangle
            if x2 < min(startx, endx):
                # Pass through the left side of the rectangle
                waypoints = [(x1, y1), (min(startx, endx), y1), (x2, y2)]
            elif x2 > max(startx, endx):
                # Pass through the right side of the rectangle
                waypoints = [(x1, y1), (max(startx, endx), y1), (x2, y2)]
        return waypoints
    else:
        # No intersection, direct line is fine
        return [(x1, y1), (x2, y2)]


def calculate_flight_path(waypoints, cruising_altitude, descent_angle):
    # Constants
    final_descent_distance = 25  # meters
    final_descent_start_altitude = 3  # meters
    radians_angle = math.radians(descent_angle)  # Convert angle to radians

    # Haversine function to calculate distance between lat/long points
    def haversine_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    altitudes = []
    cumulative_distances = []  # Start from 0 distance
    distance_covered = 0
    total_distance = sum(haversine_distance(waypoints[i], waypoints[i + 1]) for i in range(len(waypoints) - 1))
    initial_descent_distance = final_descent_start_altitude / math.tan(radians_angle)
    total_descent_distance = initial_descent_distance + final_descent_distance
    cruising_distance = total_distance - total_descent_distance

    for i in range(len(waypoints) - 1):
        current_distance = haversine_distance(waypoints[i], waypoints[i + 1])
        distance_covered += current_distance
        cumulative_distances.append(distance_covered)

        if distance_covered <= cruising_distance:
            altitudes.append(cruising_altitude)
        else:
            remaining_distance = distance_covered - cruising_distance
            # here we need to add a point that is colinear between the two points but at the right distance
            descent_altitude = max(cruising_altitude - remaining_distance * math.tan(radians_angle), 0)
            altitudes.append(descent_altitude)

    return cumulative_distances, altitudes


def find_collinear_point(x1, y1, x2, y2, d):
    # Compute the vector components from (x1, y1) to (x2, y2)
    dx = x2 - x1
    dy = y2 - y1

    # Calculate the length of the vector
    length = math.sqrt(dx ** 2 + dy ** 2)

    # Normalize the vector to make it a unit vector
    unit_dx = dx / length
    unit_dy = dy / length

    # Compute the new point by extending the unit vector by distance d
    x3 = x1 + unit_dx * d
    y3 = y1 + unit_dy * d

    return x3, y3


def plot_flight_path(cumulative_distances, altitudes):
    # Calculate the total distance of the flight path
    total_distance = cumulative_distances[-1]

    # Find the index where the last 1000 meters start
    start_index = next(i for i, dist in enumerate(cumulative_distances) if dist >= total_distance - 1000)

    # Extract the data for the last 1000 meters
    final_segment_distances = cumulative_distances[start_index:]
    final_segment_altitudes = altitudes[start_index:]

    # Adjust distances to start from 0 at the beginning of the last 1000 meters
    adjusted_distances = [dist - final_segment_distances[0] for dist in final_segment_distances]

    # Plotting the altitude profile for the last 1000 meters
    plt.figure(figsize=(10, 5))
    plt.plot(adjusted_distances, final_segment_altitudes, marker='o', linestyle='-', color='b')
    plt.title('Final 1000 Meters Altitude Profile')
    plt.xlabel('Distance (m) from -1000 meters to End')
    plt.ylabel('Altitude (m)')
    plt.grid(True)
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


def test_paths():
    # Example usage with start and end coordinates:
    points_horizontal_centered = old_generate_paths(startx=15, starty=20, endx=100, endy=50,
                                                amplitude=10, direction='horizontal')
    points_vertical_centered = old_generate_paths(startx=15, starty=20, endx=100, endy=50,
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


def test_latlon():
    delta_lat, delta_lon = feet_to_latlon(5280, 39.9546186)  # 5280 feet at 45 degrees latitude
    print(f"Change in Latitude: {delta_lat} degrees")
    print(f"Change in Longitude: {delta_lon} degrees")
