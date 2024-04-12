import math


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


def meters_to_lat_lon_change(meters, latitude):
    # Earth's radius in meters
    earth_radius = 6371000

    # Calculate the change in latitude
    delta_latitude = (meters / earth_radius) * (180 / math.pi)

    # Calculate the change in longitude
    delta_longitude = (meters / (earth_radius * math.cos(math.radians(latitude)))) * (180 / math.pi)

    return delta_latitude, delta_longitude


def angle_of_descent(point1, point2):
    # Calculate horizontal (ground) distance between the points
    x1, y1, alt1 = point1[0], point1[1], point1[2]
    x2, y2, alt2 = point2[0], point2[1], point2[2]
    dx = x2 - x1
    dy = y2 - y1
    horizontal_distance = math.sqrt(dx ** 2 + dy ** 2)

    # Calculate the vertical (altitude) difference
    vertical_difference = alt2 - alt1

    # Calculate the angle of descent using arctangent of vertical/horizontal
    angle_rad = math.atan2(vertical_difference, horizontal_distance)

    # Convert the angle from radians to degrees
    angle_deg = math.degrees(angle_rad)

    return angle_deg


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


def find_collinear_point(x1, y1, x2, y2, d):
    # Compute the vector components from (x1, y1) to (x2, y2)
    dx = x2 - x1
    dy = y2 - y1

    # Calculate the length of the vector
    length = haversine_distance((x1, y1), (x2, y2))

    # Normalize the vector to make it a unit vector
    unit_dx = dx / length
    unit_dy = dy / length

    # Compute the new point by extending the unit vector by distance d
    x3 = x1 + unit_dx * d
    y3 = y1 + unit_dy * d

    return x3, y3