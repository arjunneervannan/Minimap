class drone_data:
    def __init__(self,
                 alt=0,
                 pitch=0,
                 roll=0,
                 yaw=0,
                 groundspeed=0,
                 airspeed=0,
                 heading=0,
                 drone_id=1,
                 lat=39.952,
                 lon=-75.192):
        self.drone_id = drone_id
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.groundspeed = groundspeed
        self.airspeed = airspeed
        self.heading = heading
    
    def print_current_state(self):
        print("Latitude: ", self.lat)
        print("Longitude: ", self.lon)
        print("Altitude: ", self.alt)
        print("Pitch: ", self.pitch)
        print("Roll: ", self.roll)
        print("Yaw: ", self.yaw)
        print("Groundspeed: ", self.groundspeed)
        print("Airspeed: ", self.airspeed)
        print("Heading: ", self.heading)
