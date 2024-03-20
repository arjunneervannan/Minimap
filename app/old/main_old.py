import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkintermapview
import sv_ttk

def on_canvas_click(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y

def on_canvas_drag(event):
    global start_x, start_y
    current_x, current_y = event.x, event.y
    # Delete any existing rectangle before drawing a new one
    canvas.delete("rectangle")
    canvas.create_rectangle(start_x, start_y, current_x, current_y, outline="blue", tags="rectangle")

def on_canvas_release(event):
    # Finalize the rectangle
    canvas.delete("rectangle")
    canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="blue", tags="rectangle")

def reset_canvas():
    canvas.delete("all")

def play_action():
    messagebox.showinfo("Play", "Play button clicked!")

def video_action():
    messagebox.showinfo("Video", "Video button clicked!")

if __name__ == '__main__':
    root = tk.Tk()
    
    root.tk.call('source', 'app/forest-light.tcl')
    ttk.Style().theme_use('forest-light')
    
    root.title("MiniMap Ground Control Station")
    root.state('zoomed')
    
    # For Linux or macOS, you might need to uncomment the following lines:
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    print(width, height)
    
    root.geometry(f"{width}x{height}+0+0")

    # Create a navigation panel on the left side using the custom style
    nav_panel_width = 200
    nav_panel = ttk.Frame(root, width=nav_panel_width, style="Custom.TFrame")
    nav_panel.pack(side="left", fill="y")
    
    # Create a canvas for the map area
    canvas = tk.Canvas(root, bg="gray")
    canvas.pack(fill="both", expand=True, side="top")

    # Create a floating bar at the bottom
    floating_bar_height = 50
    floating_bar = ttk.Frame(root, height=50)
    floating_bar.pack(fill="x", side="bottom")

    # Create an inner frame to hold the buttons and center them
    button_frame = ttk.Frame(floating_bar)
    button_frame.pack(expand=True)

    # Buttons for the floating bar within the inner frame
    play_button = ttk.Button(button_frame, text="Play", command=play_action)
    video_button = ttk.Button(button_frame, text="Video", command=video_action)
    reset_button = ttk.Button(button_frame, text="Reset", command=reset_canvas)

    play_button.pack(side="left", padx=10, pady=5)
    video_button.pack(side="left", padx=10, pady=5)
    reset_button.pack(side="left", padx=10, pady=5)
    
    map_widget = tkintermapview.TkinterMapView(root, width=width-nav_panel_width, 
                                               height=900, corner_radius=0)
    map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Bind mouse events to the canvas
    canvas.bind("<Button-1>", on_canvas_click)
    canvas.bind("<B1-Motion>", on_canvas_drag)
    canvas.bind("<ButtonRelease-1>", on_canvas_release)

    # Variables to store the initial position of the rectangle
    start_x, start_y = None, None

    root.mainloop()
