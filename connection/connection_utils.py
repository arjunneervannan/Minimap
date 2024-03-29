from __future__ import print_function
from click import File
from numpy import block
from pymavlink import mavutil
from argparse import ArgumentParser
import socket
import math


# Class for formatting the Mission Item.
class missionItem:
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


def heartbeat(connection):
    while connection.target_system == 0:
        print("-- Checking heartbeat")
        connection.wait_heartbeat()
        return True


# drone Class
class drone:
    def __init__(self, port='COM6', baudrate=57600, drone_id=1):
        self.port = port
        self.baudrate = baudrate
        self.the_connection = mavutil.mavlink_connection(port, baud=baudrate)
        self.is_connected = heartbeat(self.the_connection)
        self.id = drone_id

    def arm(self):
        print("-- Arming")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

        self.ack("COMMAND_ACK")

    # Takeoff the Drone
    def takeoff(self):
        print("-- Takeoff initiated")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, math.nan, 0, 0, 10)

        self.ack("COMMAND_ACK")

    # Upload the mission items to the drone
    def upload_mission(self, mission_items):
        n = len(mission_items)
        print("-- Sending Message out")
        self.the_connection.mav.mission_count_send(self.the_connection.target_system,
                                                   self.the_connection.target_component, n, 0)

        self.ack("MISSION_REQUEST")

        for waypoint in mission_items:
            print("-- Creating a waypoint")
            self.the_connection.mav.mission_item_send(self.the_connection.target_system,  # Target System
                                                      self.the_connection.target_component,  # Target Component
                                                      waypoint.seq,  # Sequence
                                                      waypoint.frame,  # Frame
                                                      waypoint.command,  # Command
                                                      waypoint.current,  # Current
                                                      waypoint.autocontinue,  # Autocontinue
                                                      waypoint.param1,  # Hold Time
                                                      waypoint.param2,
                                                      # Accept Radius -  how close the drone gets to the waypoint
                                                      waypoint.param3,
                                                      # Pass Radius - trajectory that the drone will take passing the
                                                      # waypoint
                                                      waypoint.param4,
                                                      # Yaw - rotation of the drone, angle that the drone will be
                                                      # when it reaches viewpoint. set to NaN
                                                      waypoint.param5,  # Local X - Lattitude
                                                      waypoint.param6,  # Local Y - Longitude
                                                      waypoint.param7,  # Local Z - Altitude
                                                      waypoint.mission_type)  # Mission Type
            if waypoint != mission_items[n - 1]:
                self.ack("MISSION_REQUEST")

        self.ack("MISSION_ACK")

    def set_return(self):
        print("--Set Return to Launch")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0)
        self.ack("COMMAND_ACK")

    def start_mission(self):
        print("-- Mission Start")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)

        self.ack("COMMAND_ACK")

    # Acknowledgement from the Drone
    def ack(self, keyword):
        print("-- Message Read " + str(self.the_connection.recv_match(type=keyword, blocking=True)))


# Test Functions
if __name__ == "__main__":
    print("-- Program Started")
    # the_connection = mavutil.mavlink_connection('udp:localhost:14540')
    the_connection = mavutil.mavlink_connection('COM6', baud=57600)

    while (the_connection.target_system == 0):
        print("-- Checking heartbeat")
        the_connection.wait_heartbeat()
        print("-- Heartbeat from system (system " + str(the_connection.target_system) + ") (component " + str(
            the_connection.target_component) + ")")

    message = the_connection.mav.command_long_encode(
        the_connection.target_system,  # Target system ID
        the_connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS,  # param1: Message ID to be streamed
        1000000,  # param2: Interval in microseconds
        0,  # param3 (unused)
        0,  # param4 (unused)
        0,  # param5 (unused)
        0,  # param5 (unused)
        0  # param6 (unused)
    )

    # Send the COMMAND_LONG
    the_connection.mav.send(message)

    # Wait for a response (blocking) to the MAV_CMD_SET_MESSAGE_INTERVAL command and print result
    response = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
    if response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("Battery Command accepted")
    else:
        print("Battery Command failed")

    message2 = the_connection.mav.command_long_encode(
        the_connection.target_system,  # Target system ID
        the_connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,  # param1: Message ID to be streamed
        100000,  # param2: Interval in microseconds
        0,  # param3 (unused)
        0,  # param4 (unused)
        0,  # param5 (unused)
        0,  # param5 (unused)
        0  # param6 (unused)
    )
    the_connection.mav.send(message2)

    # Wait for a response (blocking) to the MAV_CMD_SET_MESSAGE_INTERVAL command and print result
    response2 = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
    if response2 and response2.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response2.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("GPS Command accepted")
    else:
        print("GPS Command failed")

    num = 0
    f = open('./connection/log.txt', 'w')
    while True:
        message = the_connection.recv_match(blocking=True)
        if message:
            f.write(str(message) + "\n")
            num += 1
        if num > 200:
            f.close()
            break
        # gps_message = the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        # battery_message = the_connection.recv_match(type='BATTERY_STATUS', blocking=False)
        # if battery_message:
        #     print("Battery Message Read: " + str(battery_message))
        # if gps_message:
        #     print("GPS Message Read: " + str(gps_message))

    # mission_waypoints = []
    # mission_waypoints.append(mission_item(0, 0, 42.44312627231835, -83.99860183785319, 10))  # Above takeoff point
    # mission_waypoints.append(mission_item(1, 0, 42.44323746936555, -83.99613245948624, 10))  # Above Destination Point
    # mission_waypoints.append(mission_item(2, 0, 42.44327423746765, -83.99613245948624, 5))   # Destination Point

    # upload_mission(the_connection, mission_waypoints)

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
