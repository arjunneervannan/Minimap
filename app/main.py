import customtkinter
import tkinter
from tkintermapview import TkinterMapView
import sys
sys.path.append('.')

from backend.path_generation import *
from backend.waypoint_export import *
from connection.connection_utils import *

customtkinter.set_default_color_theme("green")


class App(customtkinter.CTk):

    APP_NAME = "MiniMap Ground Control Station"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.drone = None
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

        self.frame_left.grid_rowconfigure(3, weight=1)
        
        self.app_name = customtkinter.CTkLabel(self.frame_left, text="MiniMap", anchor="w")
        self.app_name.grid(row=0, column=0, padx=(20, 20), pady=(20, 0))
        
        self.home_button = customtkinter.CTkButton(self.frame_left, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.set_marker_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.drone_config_button = customtkinter.CTkButton(self.frame_left, corner_radius=0, height=40, border_spacing=10, text="Drone Config",
                                                           fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                           anchor="w", command=self.clear_markers_and_paths)
        self.drone_config_button.grid(row=2, column=0, sticky="ew")

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Connect to Drone",
                                                command=self.connect_to_drone)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=4, column=0)

        self.switch = customtkinter.CTkSwitch(master=self.frame_left,
                                              text=f"Draw Rectangle Mode",
                                              variable=self.switch_var,
                                              command=self.switch_event)
        self.switch.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Generate All Paths",
                                                command=self.generate_paths_for_rectangles)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=6, column=0)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Export All Paths",
                                                command=self.export_paths_to_file)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=7, column=0)

        # self.button_2 = customtkinter.CTkButton(master=self.frame_left,
        #                                         text="Drone Setup",
        #                                         command=self.clear_marker_event)
        # self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)
        
        # self.button_3 = customtkinter.CTkButton(master=self.frame_left,
        #                                         text="Plan Mission",
        #                                         command=self.clear_marker_event)
        # self.button_3.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)

        # self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tile Server:", anchor="w")
        # self.map_label.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))

        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google Satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=8, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=0)
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=0, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        # self.entry = customtkinter.CTkEntry(master=self.frame_right,
        #                                     placeholder_text="type address")
        # self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        # self.entry.bind("<Return>", self.search_event)

        # self.button_5 = customtkinter.CTkButton(master=self.frame_right,
        #                                         text="Search",
        #                                         width=90,
        #                                         command=self.search_event)
        # self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        
        self.map_widget.add_right_click_menu_command(label="Add Custom Waypoint",
                                        command=self.add_marker_event,
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
        
        self.map_widget.set_position(39.952, -75.192) # EQuad
        self.map_widget.set_zoom(15)
        self.map_option_menu.set("Google Satellite")
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.appearance_mode_optionemenu.set("Light")

        self.bind("<Button-1>", self.on_first_click)  # First click event
        self.bind("<ButtonRelease-1>", self.on_second_click)  # Second click event (right-click)
        self.bind('<Key>', self.rebind())
        if self.drone:
            print("self drone is connected")
            drone_message = self.drone.the_connection.recv_match(blocking=True)
            if drone_message:
                print(drone_message)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_marker_event(self):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

    # connecting to drone
    def connect_to_drone(self):
        if not self.drone:
            self.drone = drone()
            print("connecting")
            if self.drone.is_connected:
                print("connected")
                self.drone.setup_gps_stream()

    # set markers and custom paths
    def add_marker_event(self, coord):
        self.marker_list.append(self.map_widget.set_marker(coord[0], coord[1], text=f"waypoint {len(self.marker_list)+1}"))
        
    def add_path_event(self):
        coordinates = []
        for marker in self.marker_list:
            if not marker.deleted:
                coordinates.append(marker.position)
        coordinates.append(coordinates[0])
        self.path_list.append(self.map_widget.set_path(coordinates, width=3))

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

    # code below is for drawing rectangles / disabling map
    def switch_event(self):
        if self.switch_var.get() == 1:
            self.temporarily_unbind()
        else:
            self.rebind()
            self.rectangle_list.append(self.map_widget.set_polygon(rectangle_coords, border_width=3, fill_color=None))
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
        return [(x1, y1),  (x2, y1), (x2, y2), (x1, y2)]

    # generating paths and exporting them to a file

    def generate_paths_for_rectangles(self):
        turning_radius_ft = 400
        for rectangle in self.rectangle_list:
            if not rectangle.deleted:
                (startx, starty) = rectangle.position_list[0]
                (endx, endy) = rectangle.position_list[2]
                delta_lat, delta_lon = feet_to_latlon(turning_radius_ft, startx)
                horizontal_path = generate_paths(endx, starty, startx, endy, delta_lon, direction='horizontal')
                vertical_path = generate_paths(endx, starty, startx, endy, delta_lat, direction='vertical')
                self.path_list.append(self.map_widget.set_path(horizontal_path, width=0.5, color="green"))
                self.path_list.append(self.map_widget.set_path(vertical_path, width=0.5, color="red"))

    def export_paths_to_file(self):
        num = 1
        for path in self.path_list:
            if not path.deleted:
                file_name = f"path_{num}.waypoints"
                generate_waypoints(path.position_list, file_name)
                num += 1


if __name__ == "__main__":
    app = App()
    app.start()
