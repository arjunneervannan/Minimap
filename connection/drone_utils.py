import math

from pymavlink import mavutil


class missionItem:
    def __init__(self, i, current, x, y, z):
        self.seq = i
        self.frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT  # Use Global Latitude and Longitude for position data
        self.command = mavutil.mavlink.MAV_CMD_NAV_WAYPOINT  # Move to the waypoint
        self.current = current
        self.autocontinue = 0
        self.param1 = 0.0 # hold time
        self.param2 = 10.0 # Acceptance radius
        self.param3 = 0.0 # pass radius
        self.param4 = math.nan # not using
        self.param5 = x # lat
        self.param6 = y # lon
        self.param7 = z # altitude
        self.mission_type = 0  # The MAV_MISSION_TYPE value for MAV_MISSION_TYPE_MISSION


def heartbeat(connection):
    while connection.target_system == 0:
        print("-- Checking heartbeat")
        connection.wait_heartbeat()
        print("connected successfully")
        return True


def convert_positions_to_mission_items(profile):
    mission_items = []

    i = 0

    home_waypoint = missionItem(i, 0, profile[0][0], profile[0][1], 1)
    # home_waypoint.command = mavutil.mavlink.MAV_CMD_DO_SET_HOME
    mission_items.append(home_waypoint)

    i += 1

    takeoff = missionItem(i, 0, 0, 0, profile[0][2] / 2)
    takeoff.param1 = 15
    takeoff.command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
    mission_items.append(takeoff)

    i += 1

    for j, position in enumerate(profile):
        if j == len(profile) - 1:
            landing = missionItem(i, 0, profile[-1][0], profile[-1][1], 1)
            landing.command = mavutil.mavlink.MAV_CMD_NAV_LAND
            landing.param1 = 0
            mission_items.append(landing)
        elif j == 0:
            continue
        else:
            mission_items.append(missionItem(i, 0, position[0], position[1], position[2]))
        i += 1

    return mission_items