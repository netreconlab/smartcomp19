import sim as sim

class Sensor:
    class_counter = 0

    def __init__(self, data_size, msg_gen_rate, start_time, msg_ttl):

        self.id = 'S' + str(Sensor.class_counter)

        self.data_size = data_size
        self.msg_gen_rate = msg_gen_rate
        self.start_time = start_time
        self.msg_ttl = msg_ttl
        self.msg_generated = 0
        self.msg_latencies = []
        self.msg_tbs = []
        self.msg_tbg = []
        self.gen_times = []

        Sensor.class_counter += 1

    def generate_msg(self):
        if sim.timestep == self.msg_gen_rate == 0 or (sim.timestep !=0 and sim.timestep % self.msg_gen_rate == 0):
            return True
        else:
            return False


class OnStreetSensor(Sensor):

    def __init__(self, data_size, msg_gen_rate, start_time, msg_ttl, location, no_of_routes):

        Sensor.__init__(self, data_size, msg_gen_rate, start_time, msg_ttl)
        self.routes = []
        self.no_of_routes = no_of_routes
        self.location = location


    def set_route(self, Route):
        self.routes.append(Route)


    def get_minimum_round_trip_time(self):
        import sys
        minimum = sys.float_info.max
        for r in self.routes:
            for b in r.buses:
                minimum = min(minimum, b.trip_time)

        return minimum


    def get_total_bus_count(self):
        total = 0
        for r in self.routes:
            total += len(r.buses)

        return total



class OffStreetSensor(Sensor):

    def __init__(self, data_size, msg_gen_rate, start_time, msg_ttl, ped_arrival_rate):

        Sensor.__init__(self, data_size, msg_gen_rate, start_time, msg_ttl)

        # arrival rate, how many ped riders pass the sensor per second
        self.ped_arrival_rate = ped_arrival_rate
        self.msg_tsp = []
        self.msg_tpbs = []




