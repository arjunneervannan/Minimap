from __future__ import print_function
from click import File
from numpy import block
import os
os.environ['MAVLINK20'] = ''


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
        return True


def convert_positions_to_mission_items(positions):
    mission_items = []
    curr_altitude = 60

    i = 0

    home_waypoint = missionItem(i, 0, positions[0][0], positions[0][1], 20)
    mission_items.append(home_waypoint)

    i += 1

    takeoff = missionItem(i, 0, 0, 0, curr_altitude / 2)
    takeoff.param1 = 15
    takeoff.command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
    mission_items.append(takeoff)

    i += 1

    for j, position in enumerate(positions):
        if j >= len(positions) - 5:
            curr_altitude -= 10
        mission_items.append(missionItem(i, 0, position[0], position[1], curr_altitude))
        i += 1
    
    landing = missionItem(i, 0, positions[0][0], positions[0][1], 1)
    landing.command = mavutil.mavlink.MAV_CMD_NAV_LAND
    landing.param1 = 0
    mission_items.append(landing)

    return mission_items


# drone Class
class drone:
    def __init__(self, port='COM6', baudrate=57600, drone_id=1):
        self.port = port
        self.baudrate = baudrate
        self.id = drone_id

    def connect(self):
        self.the_connection = mavutil.mavlink_connection(self.port, baud=self.baudrate)
        self.is_connected = heartbeat(self.the_connection)
    
    def arm(self):
        print("-- Arming")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                                  0, 1, 0, 0, 0, 0, 0, 0)
        
        # print("Waiting for the vehicle to arm")
        # self.the_connection.motors_armed_wait()
        # print('Armed!')

        self.ack("COMMAND_ACK")
    
    def disarm(self):
        print("-- Arming")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                                  0, 0, 0, 0, 0, 0, 0, 0)

        self.ack("COMMAND_ACK")
    
    def set_rc_channel_pwm(self, channel_id, pwm=1500):
        """ Set RC channel pwm value
        Args:
            channel_id (TYPE): Channel ID
            pwm (int, optional): Channel pwm value 1100-1900
        """
        if channel_id < 1 or channel_id > 18:
            print("Channel does not exist.")
            return

        # Mavlink 2 supports up to 18 channels:
        # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
        rc_channel_values = [65535 for _ in range(18)]
        rc_channel_values[channel_id - 1] = pwm
        self.the_connection.mav.rc_channels_override_send(
            self.the_connection.target_system,                # target_system
            self.the_connection.target_component,             # target_component
            *rc_channel_values)                  # RC channel list, in microseconds.
        self.ack("HEARTBEAT")
        
    def pre_arm_checks(self):
        print("--Running Pre-arm checks")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                self.the_connection.target_component,
                                                mavutil.mavlink.MAV_CMD_RUN_PREARM_CHECKS, 
                                                0, 0, 0, 0, 0, 0, 0, 0)
        self.ack("COMMAND_ACK")
        self.ack("SYS_STATUS")

    # Takeoff the Drone
    def takeoff(self):
        print("-- Takeoff initiated")
        self.the_connection.mav.command_long_send(self.the_connection.target_system,
                                                  self.the_connection.target_component,
                                                  mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                                                  15, 0, 0, 0, 0, 0, 0, 30)

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
                                                  mavutil.mavlink.MAV_CMD_MISSION_START,
                                                  1, 0, 0, 0, 0, 0, 0, 0)

        self.ack("COMMAND_ACK")
    
    # test bench to run various functions
    def test(self):
        print("-- Running Test Sequence")
        print("-- Sending Mission Message out")
        self.the_connection.mav.mission_count_send(self.the_connection.target_system,
                                                   self.the_connection.target_component, 4, 0)
        
        self.ack("MISSION_REQUEST")

        # self.the_connection.mav.command_long_send(self.the_connection.target_system,
        #                                     self.the_connection.target_component,
        #                                     mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        #                                     15, 0, 0, 0, 0, 0, 0, 30)
        
        # self.ack("MISSION_REQUEST")

        # self.the_connection.mav.command_long_send(self.the_connection.target_system,
        #                                           self.the_connection.target_component,
        #                                             mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        #                                             0, 30, 0, 0, 0, 0,
        #                                             39.95341460622441, -75.18878982390572, 30)

        self.the_connection.mav.mission_item_send(self.the_connection.target_system,  # Target System
                                                  self.the_connection.target_component,  # Target Component
                                                  0, # Sequence
                                                  mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # Frame
                                                  mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # Command
                                                  0, # Current
                                                  0, # Autocontinue
                                                  15, # pitch angle
                                                  30, # not using
                                                  0, # not using
                                                  0, # not using
                                                  39.95341460622441, # lat
                                                  -75.18878982390572, # lon
                                                  30, # alt,
                                                  0 # mission type
        )

        self.ack("MISSION_REQUEST")

        self.the_connection.mav.mission_item_send(self.the_connection.target_system,  # Target System
                                                  self.the_connection.target_component,  # Target Component
                                                  1, # Sequence
                                                  mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # Frame
                                                  mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # Command
                                                  0, # Current
                                                  0, # Autocontinue
                                                  15, # pitch angle
                                                  0, # not using
                                                  0, # not using
                                                  0, # not using
                                                  0, # lat - not using
                                                  0, # lon - not using
                                                  30, # alt,
                                                  0 # mission type
        )

        self.ack("MISSION_REQUEST")

        self.the_connection.mav.mission_item_send(self.the_connection.target_system,  # Target System
                                                  self.the_connection.target_component,  # Target Component
                                                  2, # Sequence
                                                  mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # Frame
                                                  mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # Command
                                                  0, # Current
                                                  0, # Autocontinue
                                                  15, # not using this
                                                  30, # acc radius
                                                  0, # pass radius
                                                  0, # param 4 - not using this
                                                  39.95341460622441, # lat
                                                  -75.18878982390572, # lon
                                                  30, # alt,
                                                  0 # mission type
        )

        self.ack("MISSION_REQUEST")

        self.the_connection.mav.mission_item_send(self.the_connection.target_system,  # Target System
                                                  self.the_connection.target_component,  # Target Component
                                                  3, # Sequence
                                                  mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, # Frame
                                                  mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,  # Command
                                                  0, # Current
                                                  0, # Autocontinue
                                                  0, # not using this
                                                  30, # acc radius
                                                  0, # pass radius
                                                  0, # param 4 - not using this
                                                  39.95423703825388, # lat
                                                  -75.18655822600533, # lon
                                                  30, # alt,
                                                  0 # mission type
        )

        self.ack("MISSION_ACK")

    def clear_mission(self):
        print("-- Clearing Mission")
        self.the_connection.mav.mission_clear_all_send(self.the_connection.target_system, 
                                                       self.the_connection.target_component)
        self.ack("MISSION_ACK")
    
    def auto(self):
        print("-- Setting to Auto Mode")
        self.the_connection.set_mode_auto()
    
    def get_flight_mode(self):
        print("-- Getting Flight Mode")

        msg = self.the_connection.recv_match(type = 'HEARTBEAT', blocking = True)
        if msg:
            mode = mavutil.mode_string_v10(msg)
            print("-- Flight Mode: " + mode)
            print("-- System Status: " + str(msg))
    
    # Acknowledgement from the Drone
    def ack(self, keyword):
        print("-- Message Read " + str(self.the_connection.recv_match(type=keyword, blocking=True)))

    def setup_gps_stream(self):
        gps_message = self.the_connection.mav.command_long_encode(
            self.the_connection.target_system,  # Target system ID
            self.the_connection.target_component,  # Target component ID
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
        self.the_connection.mav.send(gps_message)

        # Wait for a response (blocking) to the MAV_CMD_SET_MESSAGE_INTERVAL command and print result
        gps_respnse = self.the_connection.recv_match(type='COMMAND_ACK', blocking=True)
        if gps_respnse and gps_respnse.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and \
                gps_respnse.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("GPS Command accepted")
        else:
            print("GPS Command failed")


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
