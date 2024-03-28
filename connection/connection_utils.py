from __future__ import print_function
from pymavlink import mavutil
from argparse import ArgumentParser
import socket
import math

# Class for formatting the Mission Item.
class mission_item:
    def __init__(self, i, current, x, y, z):
        self.seq = i
        self.frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT  # Use Global Latitude and Longitude for position data
        self.command = mavutil.mavlink.MAV_CMD_NAV_WAYPOINT  # Move to the waypoint
        self.current = current
        self.autocontinue = 0
        self.param1 = 0.0
        self.param2 = 2.0
        self.param3 = 20.0
        self.param4 = math.nan
        self.param5 = x
        self.param6 = y
        self.param7 = z
        self.mission_type = 0  # The MAV_MISSION_TYPE value for MAV_MISSION_TYPE_MISSION

# Arm the Drone
def arm(the_connection):
    print("-- Arming")
    the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

    ack(the_connection, "COMMAND_ACK")

# Takeoff the Drone
def takeoff(the_connection):
    print("-- Takeoff initiated")
    the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, math.nan, 0, 0, 10)

    ack(the_connection, "COMMAND_ACK")

# Upload the mission items to the drone
def upload_mission(the_connection, mission_items):
    n = len(mission_items)
    print("-- Sending Message out")
    the_connection.mav.mission_count_send(the_connection.target_system, the_connection.target_component, n, 0)

    ack(the_connection, "MISSION_REQUEST")

    for waypoint in mission_items:
        print("-- Creating a waypoint")
        the_connection.mav.mission_item_send(the_connection.target_system, # Target Syust
                                             the_connection.target_component, # Target Component
                                             waypoint.seq, # Sequence
                                             waypoint.frame, # Frame
                                             waypoint.command, # Command
                                             waypoint.current, # Current
                                             waypoint.autocontinue, # Autocontinue
                                             waypoint.param1, # Hold Time
                                             waypoint.param2, # Accept Radius -  how close the drone gets to the waypoint
                                             waypoint.param3, # Pass Radius - trajectory that the drone will take passing the waypoint
                                             waypoint.param4, # Yaw - rotation of the drone, angle that the drone will be when it reaches viewpoint. set to NaN
                                             waypoint.param5, # Local X - Lattitude
                                             waypoint.param6, # Local Y - Longitude
                                             waypoint.param7, # Local Z - Altitude
                                             waypoint.mission_type) # Mission Type
    if waypoint != mission_items[n-1]:
        ack(the_connection, "MISSION_REQUEST")

    ack(the_connection, "MISSION_ACK")

def set_return(the_connection):
    print("--Set Return to Launch")
    the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0)
    ack(the_connection, "COMMAND_ACK")

def start_mission(the_connection):
    print("-- Mission Start")
    the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component,
                                        mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)

    ack(the_connection, "COMMAND_ACK")

# Acknowledgement from the Drone
def ack(the_connection, keyword):
    print("-- Message Read " + str(the_connection.recv_match(type=keyword, blocking=True)))

# Main Function
if __name__ == "__main__":
    print("-- Program Started")
    # the_connection = mavutil.mavlink_connection('udp:localhost:14540')
    the_connection = mavutil.mavlink_connection('COM6',baud=57600)

    while(the_connection.target_system == 0):
        print("-- Checking heartbeat")
        the_connection.wait_heartbeat()
        print("-- Heartbeat from system (system " + str(the_connection.target_system) + ") (component " + str(the_connection.target_component) + ")")

    mission_waypoints = []
    mission_waypoints.append(mission_item(0, 0, 42.44312627231835, -83.99860183785319, 10))  # Above takeoff point
    mission_waypoints.append(mission_item(1, 0, 42.44323746936555, -83.99613245948624, 10))  # Above Destination Point
    mission_waypoints.append(mission_item(2, 0, 42.44327423746765, -83.99613245948624, 5))   # Destination Point

    upload_mission(the_connection, mission_waypoints)

    # arm(the_connection)

    # takeoff(the_connection)

    # start_mission(the_connection)

    # for mission_item in mission_waypoints:
    #     print("Message Read = " + str(the_connection.recv_match(type="MISSION_ITEM_REACHED", condition="MISSION_ITEM_REACHED.seq == {0}".format(mission_item.seq), blocking=True)))

    # set_return(the_connection)

# # Start a connection listening on a UDP port
# the_connection = mavutil.mavlink_connection('COM6',baud=57600)

# # Wait for the first heartbeat
# #   This sets the system and component ID of remote system for the link
# print("waiting for heartbeat")
# the_connection.wait_heartbeat()
# print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

# # Once connected, use 'the_connection' to get and send messages