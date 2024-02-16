import pyglet
from pyglet import shapes
from math import sin, cos

window = pyglet.window.Window(width=800, height=600, caption="Path Planning")
window.set_location(100, 100)

batch = pyglet.graphics.Batch()

circle = shapes.Circle(x=100, y=60, radius=50, color=(50, 225, 30), batch=batch)
square = shapes.Rectangle(x=200, y=200, width=200, height=200, color=(55, 55, 255), batch=batch)
square.anchor_position = (100, 100)
star = shapes.Star(x=400, y=400, outer_radius=100, inner_radius=20, num_spikes=8, color=(255, 255, 0), batch=batch)

@window.event
def on_draw() -> None:
    window.clear()
    batch.draw()


value = 0
def update(dt, *args, **kwargs):
    global value
    value += 0.1
    circle.radius += sin(value)
    star.outer_radius += cos(value)
    star.inner_radius += sin(value)
    square.rotation += 1
    if kwargs.get("pattern") == "standard":
        print("Standard update")


pyglet.clock.schedule_interval(update, 1/60, pattern="standard")
pyglet.app.run()
