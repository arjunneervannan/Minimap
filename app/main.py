import customtkinter
import tkinter
from networkx import is_connected
from tkintermapview import TkinterMapView
import sys
import pickle as pkl
from tkinter import messagebox
from tkinter import simpledialog

sys.path.append('.')

from connection.path_generation import *
from connection.drone_connection import *
from connection.drone_data import *

customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    APP_NAME = "MiniMap Ground Control Station"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.drone = drone()
        self.drone_data = drone_data()
        self.path_index = 0

        self.drone_speed = 20  # meters per second

        self.home = None

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        self.path_list = []
        self.rectangle_list = []
        self.switch_var = tkinter.IntVar(value=0)

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(1, weight=1)

        self.app_name = customtkinter.CTkLabel(self.frame_left, text="MiniMap", anchor="w")
        self.app_name.grid(row=0, column=0, padx=(20, 20), pady=(20, 0))

        self.disarm_drone_button = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Disarm Drone",
                                                        command=self.disarm_drone)
        self.disarm_drone_button.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)

        self.arm_drone_button = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Upload Mission",
                                                        command=self.upload_mission)
        self.arm_drone_button.grid(pady=(20, 0), padx=(20, 20), row=3, column=0)

        self.arm_drone_button = customtkinter.CTkButton(master=self.frame_left,
                                                        text="Start Mission",
                                                        command=self.arm_drone)
        self.arm_drone_button.grid(pady=(20, 0), padx=(20, 20), row=4, column=0)

        self.drone_connect_button = customtkinter.CTkButton(master=self.frame_left,
                                                            text="Connect to Drone",
                                                            command=self.connect_to_drone)
        self.drone_connect_button.grid(pady=(20, 0), padx=(20, 20), row=5, column=0)

        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text=f"Draw Rectangle Mode",
                                              variable=self.switch_var,
                                              command=self.switch_event)
        self.switch.grid(row=6, column=0, padx=(20, 20), pady=(20, 0))

        self.generate_button = customtkinter.CTkButton(master=self.frame_left,
                                                       text="Generate All Paths",
                                                       command=self.generate_paths_for_rectangles)
        self.generate_button.grid(pady=(20, 0), padx=(20, 20), row=7, column=0)

        self.export_button = customtkinter.CTkButton(master=self.frame_left,
                                                     text="Export All Paths",
                                                     command=self.export_paths_to_file)
        self.export_button.grid(pady=(20, 0), padx=(20, 20), row=8, column=0)

        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal",
                                                                                    "Google Satellite"],
                                                           command=self.change_map)
        self.map_option_menu.grid(row=9, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=10, column=0, padx=(20, 20), pady=(20, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=11, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=0)
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=0, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.map_widget.add_right_click_menu_command(label="Set Home Here",
                                                     command=self.add_home_event,
                                                     pass_coords=True)
        self.map_widget.add_right_click_menu_command(label="Remove Home",
                                                     command=self.remove_home_event,
                                                     pass_coords=False)
        self.map_widget.add_right_click_menu_command(label="Add Custom Waypoint",
                                                     command=self.add_waypoint_event,
                                                     pass_coords=True)
        self.map_widget.add_right_click_menu_command(label="Generate Flight Path",
                                                     command=self.add_path_event,
                                                     pass_coords=False)
        self.map_widget.add_right_click_menu_command(label="Clear Markers and Paths",
                                                     command=self.clear_markers_and_paths,
                                                     pass_coords=False)
        self.map_widget.add_right_click_menu_command(label="Delete All Rectangles",
                                                     command=self.clear_paths_and_rectangles,
                                                     pass_coords=False)

        self.map_widget.set_position(39.952, -75.192)  # EQuad
        self.map_widget.set_zoom(15)
        self.map_option_menu.set("Google Satellite")
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.appearance_mode_optionemenu.set("Light")

        self.bind("<Button-1>", self.on_first_click)  # First click event
        self.bind("<ButtonRelease-1>", self.on_second_click)  # Second click event (right-click)
        self.bind('<Key>', self.rebind())

        # self.drone_marker = self.map_widget.set_marker(39.952, -75.192, text=f"drone {1}")
        # self.update_gps()

    # def search_event(self, event=None):
    #     self.map_widget.set_address(self.entry.get())

    # def set_marker_event(self):
    #     current_position = self.map_widget.get_position()
    #     self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

    # connecting to drone
    def connect_to_drone(self):
        self.drone.connect()
        if self.drone.is_connected:
            tkinter.messagebox.Message(master=None, message="Drone connected succesfully", 
                                       icon=tkinter.messagebox.INFO).show()

    def upload_mission(self):
        if len(self.rectangle_list) == 0:
            messagebox.showerror("Error", "Please draw a rectangle")
            return
        
        if not self.drone.is_connected:
            messagebox.showerror("Error", "Drone is not connected")
            return

        if not self.home:
            messagebox.showerror("Error", "Please set home location")
            return

        answer = simpledialog.askinteger("Input", "Which path do you want to upload?",
                                         parent=self.frame_right)

        alt = simpledialog.askinteger("Input", "Which altitude would you like to fly at? (m)",
                                      parent=self.frame_right)

        waypoints = self.path_list[answer].position_list
        profile = simple_landing_profile(waypoints, alt, 15)
        if profile is None:
            messagebox.showerror("Error", "Profile too steep to land safely")
            return
        

        if self.drone.is_connected:
            mission_items = convert_positions_to_mission_items(profile)  # includes takeoff and landing
            if self.drone.upload_mission(mission_items):
                tkinter.messagebox.Message(master=None, message="Mission uploaded succesfully", 
                                           icon=tkinter.messagebox.INFO).show()
                for point in profile:
                    self.map_widget.set_marker(point[0], point[1], text=f"{point[2]} m")
                    print(point)
        else:
            print("Drone is not connected")

    def arm_drone(self):
        if self.drone.is_connected:
            self.drone.auto()
            if self.drone.arm():
                tkinter.messagebox.Message(master=None, message="Drone armed succesfully", 
                                           icon=tkinter.messagebox.INFO).show()
        else:
            tkinter.messagebox.Message(master=None, message="Drone is not connected", 
                                       icon=tkinter.messagebox.ERROR).show()

    def disarm_drone(self):
        if self.drone.is_connected:
            if self.drone.disarm():
                tkinter.messagebox.Message(master=None, message="Drone disarmed succesfully", 
                                           icon=tkinter.messagebox.INFO).show()
        else:
            tkinter.messagebox.Message(master=None, message="Drone is not connected", 
                                       icon=tkinter.messagebox.ERROR).show()
    
    def update_gps(self):
        if self.drone:
            pitch = 0
            # print("updating gps")
            drone_message = self.drone.the_connection.recv_match(blocking=True)
            # drone_message = self.drone.the_connection.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            if drone_message:
                # print(drone_message.get_type())
                if drone_message.get_type() == 'GLOBAL_POSITION_INT':
                    lat = drone_message.lat * 1e-7
                    lon = drone_message.lon * 1e-7
                    alt = drone_message.alt * 1e-6
                    # print(f"lat: {lat}, lon: {lon}, alt: {alt}")
                    self.drone_marker.set_position(lat, lon)
                elif drone_message.get_type() == 'ATTITUDE':
                    roll = drone_message.roll
                    pitch = drone_message.pitch
                    yaw = drone_message.yaw
                    # print(f"roll: {roll}, pitch: {pitch}, yaw: {yaw}")
                elif drone_message.get_type() == 'VFR_HUD':
                    groundspeed = drone_message.groundspeed
                    airspeed = drone_message.airspeed
                    heading = drone_message.heading
                    # print(f"groundspeed: {groundspeed}, airspeed: {airspeed}, heading: {heading}")
            # self.drone_data.print_current_state()
            # self.display_drone()
            self.after(10, self.update_gps)

    def display_drone(self):
        self.map_widget.set_marker(self.drone_data.lat, self.drone_data.lon,
                                   text=f"drone {self.drone_data.pitch}")

    # set markers and custom paths
    def add_waypoint_event(self, coord):
        self.marker_list.append(self.map_widget.set_marker(coord[0], coord[1],
                                                           text=f"waypoint {len(self.marker_list) + 1}"))

    def add_path_event(self):
        coordinates = []
        for marker in self.marker_list:
            if not marker.deleted:
                coordinates.append(marker.position)
        coordinates.append(coordinates[0])

        horiz_length = total_path_distance(coordinates)
        horiz_time = total_time(horiz_length, self.drone_speed)

        custom_path_data = path_data(index=self.path_index,
                                     length=horiz_length,
                                     time=horiz_time,
                                     area=0)

        self.path_list.append(self.map_widget.set_path(coordinates,
                                                       width=4,
                                                       color="blue",
                                                       data=custom_path_data,
                                                       command=self.on_path_click))
        self.path_index += 1

    def add_home_event(self, coord):
        if not self.home:
            self.home = self.map_widget.set_marker(coord[0], coord[1], text="Home")
        else:
            self.home.set_position(coord[0], coord[1])

    def remove_home_event(self):
        if self.home:
            self.home.delete()
            self.home = None

    def clear_markers_and_paths(self):
        for marker in self.marker_list:
            marker.delete()
        for path in self.path_list:
            path.delete()

    def clear_paths_and_rectangles(self):
        for path in self.path_list:
            path.delete()
        for rectangle in self.rectangle_list:
            rectangle.delete()

    def on_path_click(self, event):
        # print(f"path clicked {event.data}")
        new_window = tkinter.Toplevel()
        new_window.title("Path Data")
        new_window.geometry("200x200")
        data_text = f"Index: {event.data.index}\nLength: {event.data.length:.2f} meters\n" \
                    f"Time: {event.data.time:.2f} minutes\nArea: {event.data.area:.2f} km^2"
        label = tkinter.Label(new_window, text=data_text, justify=tkinter.LEFT, padx=10, pady=10)
        label.pack()

    # code below is for drawing rectangles / disabling map
    def switch_event(self):
        if self.switch_var.get() == 1:
            self.temporarily_unbind()
        else:
            self.rebind()
            self.rectangle_list.append(self.map_widget.set_polygon(
                rectangle_coords,
                border_width=4,
                outline_color="blue",
                fill_color=None))
            self.map_widget.canvas.delete("rectangle")

    def on_first_click(self, event):
        global start_x, start_y  # Save the starting point coordinates
        start_x, start_y = event.x, event.y

    def on_second_click(self, event):
        end_x, end_y = event.x, event.y  # Get the ending point coordinates
        global rectangle_coords
        if self.switch_var.get() == 1:
            rectangle_coords = self.convert_rectangle_coords(start_x, start_y, end_x, end_y)
            self.map_widget.canvas.create_rectangle(start_x, start_y, end_x, end_y, outline="black", width=3,
                                                    tags="rectangle", dash=(5, 5))

    def temporarily_unbind(self):
        self.map_widget.canvas.unbind("<B1-Motion>")
        self.map_widget.canvas.unbind("<Button-1>")
        self.map_widget.canvas.unbind("<ButtonRelease-1>")
        self.map_widget.canvas.unbind("<MouseWheel>")
        self.map_widget.canvas.unbind("<Button-4>")
        self.map_widget.canvas.unbind("<Button-5>")

    def rebind(self):
        self.map_widget.canvas.bind("<B1-Motion>", self.map_widget.mouse_move)
        self.map_widget.canvas.bind("<Button-1>", self.map_widget.mouse_click)
        self.map_widget.canvas.bind("<ButtonRelease-1>", self.map_widget.mouse_release)
        self.map_widget.canvas.bind("<MouseWheel>", self.map_widget.mouse_zoom)
        self.map_widget.canvas.bind("<Button-4>", self.map_widget.mouse_zoom)
        self.map_widget.canvas.bind("<Button-5>", self.map_widget.mouse_zoom)

    def convert_rectangle_coords(self, start_x, start_y, end_x, end_y):
        (x1, y1) = self.map_widget.convert_canvas_coords_to_decimal_coords(start_x, start_y)
        (x2, y2) = self.map_widget.convert_canvas_coords_to_decimal_coords(end_x, end_y)
        return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

    # generating paths and exporting them to a file

    def generate_paths_for_rectangles(self):
        if len(self.rectangle_list) == 0:
            messagebox.showerror("Error", "Please draw a rectangle")
            return

        if not self.home:
            messagebox.showerror("Error", "Please set home location")
            return

        turning_radius_ft = self.generate_paths_dialogbox()

        for rectangle in self.rectangle_list:
            if not rectangle.deleted:
                (startx, starty) = rectangle.position_list[0]
                (endx, endy) = rectangle.position_list[2]
                delta_lat, delta_lon = meters_to_lat_lon_change(turning_radius_ft, startx)

                home_coords = self.home.position

                horizontal_path = generate_paths(startx,
                                                 starty,
                                                 endx,
                                                 endy,
                                                 home_coords[0],
                                                 home_coords[1],
                                                 delta_lon,
                                                 direction='horizontal')
                vertical_path = generate_paths(startx,
                                               starty,
                                               endx,
                                               endy,
                                               home_coords[0],
                                               home_coords[1],
                                               delta_lat,
                                               direction='vertical')
                # self.map_widget.set_marker(horizontal_path[0][0], horizontal_path[0][1], text="start horiz")
                # self.map_widget.set_marker(vertical_path[0][0], vertical_path[0][1], text="start vert")
                #
                # self.map_widget.set_marker(horizontal_path[-1][0], horizontal_path[-1][1], text="ending horiz")
                # self.map_widget.set_marker(vertical_path[-1][0], vertical_path[-1][1], text="ending vert")

                horizontal_path.insert(0, horizontal_path[-1])
                vertical_path.insert(0, vertical_path[-1])

                horiz_length = total_path_distance(horizontal_path)
                vert_length = total_path_distance(vertical_path)
                horiz_time = total_time(horiz_length, self.drone_speed)
                vert_time = total_time(vert_length, self.drone_speed)
                area = area_coverage(startx, starty, endx, endy)

                horiz_path_data = path_data(index=self.path_index,
                                            length=horiz_length,
                                            time=horiz_time,
                                            area=area)

                self.path_index += 1

                vert_path_data = path_data(index=self.path_index,
                                           length=vert_length,
                                           time=vert_time,
                                           area=area)

                self.path_index += 1

                self.path_list.append(self.map_widget.set_path(horizontal_path,
                                                               width=2.5,
                                                               color="yellow",
                                                               command=self.on_path_click,
                                                               data=horiz_path_data))
                self.path_list.append(self.map_widget.set_path(vertical_path,
                                                               width=2.5,
                                                               color="red",
                                                               command=self.on_path_click,
                                                               data=vert_path_data))

    def generate_paths_dialogbox(self):
        answer = simpledialog.askinteger("Input", "What is your desired turning radius (m)?",
                                         parent=self.frame_right)
        return answer

    def export_paths_to_file(self):
        print("exporting paths to file")
        for i, path in enumerate(self.path_list):
            if not path.deleted:
                # self.drone.upload_mission(path.position_list)
                file_name = f"path_{i}.pkl"
                print(path.position_list)
                file_name = f'./waypoints/{file_name}'
                with open(file_name, 'wb') as f:
                    pkl.dump(path.position_list, f)
            # generate_waypoints(path.position_list, file_name)
        # num = 1
        # for path in self.path_list:
        #     if not path.deleted:
        #         file_name = f"path_{num}.waypoints"
        #         generate_waypoints(path.position_list, file_name)
        #         num += 1


if __name__ == "__main__":
    app = App()
    app.start()
