import pyglet
from pyglet import shapes
from math import sin, cos

def create_drones(N, batch):
    drones = []
    for i in range(N):
        drone = shapes.Circle(x=0, y=0, radius=50, color=(50, 225, 30), batch=batch)
        drones.append(drone)
