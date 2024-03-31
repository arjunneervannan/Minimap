from connection_utils import *
import pickle as pkl

def main():
    the_drone = drone()
    while True:
        try:
            command = input("Enter a command: ")
            if command == "arm":
                the_drone.arm()
            elif command == "connect":
                the_drone.connect()
            elif command == "clear":
                the_drone.clear_mission()
            elif command == "upload":
                file_name = "path_1.pkl"
                file_name = f'./waypoints/{file_name}'
                with open(file_name, 'rb') as f:
                    path = pkl.load(f)
                print(path)
                mission_items = convert_positions_to_mission_items(path) # includes takeoff and landing
                the_drone.upload_mission(mission_items)
            elif command == "auto":
                the_drone.auto()
            elif command == "disarm":
                the_drone.disarm()
            elif command == "mode":
                the_drone.get_flight_mode()
            elif command == "stream":
                while True:
                    try:
                        msg = the_drone.the_connection.recv_match(type="HEARTBEAT", blocking=True)
                        mode = mavutil.mode_string_v10(msg)
                        print("-- Flight Mode: " + mode)
                    except KeyboardInterrupt:
                        print("Program terminated by user")
                        break

            elif command == "prearm":
                the_drone.pre_arm_checks()
            elif command == "start":
                the_drone.start_mission()
            elif command == "test":
                the_drone.test()
            else:
                print("Invalid command")
        except KeyboardInterrupt:
            print("Program terminated by user")
            break

if __name__ == "__main__":
    main()