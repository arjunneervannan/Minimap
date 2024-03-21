import pyglet
from pyglet import shapes
from math import sin, cos

window = pyglet.window.Window(width=1200, height=800, caption="Path Planning Simulator")
window.set_location(300, 100)

batch = pyglet.graphics.Batch()

# circle = shapes.Circle(x=100, y=60, radius=50, color=(50, 225, 30), batch=batch)
# square = shapes.Rectangle(x=200, y=200, width=200, height=200, color=(55, 55, 255), batch=batch)
# square.anchor_position = (-100, 100)
# star = shapes.Star(x=400, y=400, outer_radius=100, inner_radius=20, num_spikes=8, color=(255, 255, 0), batch=batch)

drones = []
for i in range(1):
    # drone = shapes.Triangle(x=600, y=400, x2=620, y2=425, x3=630, y3=410, color=(0, 255, 0), batch=batch)
    drone = shapes.Rectangle(x=600, y=400, width=50, height=10, color=(0, 255, 0), batch=batch)
    drone.anchor_position = (25, 5)
    # drone = shapes.Triangle(x=0, y=0, radius=50, color=(50, 225, 30), batch=batch)
    drones.append(drone)

@window.event
def on_draw() -> None:
    window.clear()
    batch.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    pass


value = 0
direction = 1
time_elapsed = 0
def update(dt, *args, **kwargs):
    # global value
    # global direction
    # if direction == 1:
    #     drones[0].y += 5
    # elif direction == 2:
    #     drones[0].x += 10
    
    # if drones[0].y > 750:
    #     direction = 2
    # # if kwargs.get("pattern") == "standard":
    # #     print("Standard update")
    global time_elapsed
    time_elapsed += dt

    # Spiral motion parameters
    amplitude = 50  # Amplitude of the spiral
    frequency = 2  # Frequency of the spiral
    angular_speed = 0.5  # Angular speed of rotation

    # Calculate the new position of the triangle using a spiral motion
    drones[0].x = 600 + amplitude * time_elapsed * cos(time_elapsed * frequency)
    drones[0].y = 400 + amplitude * time_elapsed * sin(time_elapsed * frequency)
    rotation = angular_speed * time_elapsed * 360  # Convert time to degrees for rotation

    # Update the position and rotation of the triangle
    # drone.position = (x, y)
    drone.rotation = rotation




pyglet.clock.schedule_interval(update, 1/60, pattern="standard")
pyglet.app.run()
