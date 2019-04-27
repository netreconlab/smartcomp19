from components import *
from sensor import *


class Route:
    class_counter = 0

    def __init__(self, circ, no_of_buses, no_of_gw, no_of_ons):
        self.id = 'R' + str(Route.class_counter)
        self.circ = circ
        self.buses = []
        self.gateways = []
        self.sensors = []
        self.bus_stops = []
        self.no_of_buses = no_of_buses
        self.no_of_gateways = no_of_gw
        self.no_of_ons = no_of_ons

        Route.class_counter += 1

    def __str__(self):
        return "id: {0}, circumference: {1}, ons: {2},  gateways: {3}, buses: {4}, busstops: {5}"\
            .format(self.id, self.circ, self.no_of_ons, self.no_of_gateways, self.no_of_buses, len(self.buses))

    def add_bus(self, bus):
        if isinstance(bus, Bus):
            self.buses.append(bus)
        elif type(bus) is list:
            self.buses.extend(bus)


    def add_gateways(self, gw):
        if isinstance(gw, Gateway):
            self.gateways.append(gw)
        elif type(gw) is list:
            self.gateways.extend(gw)


    def add_sensors(self, sensor):
        if isinstance(sensor, OnStreetSensor):
            self.sensors.append(sensor)
        elif type(sensor) is list:
            self.sensors.extend(sensor)


    def add_bus_stops(self, bus_stops):
        if isinstance(bus_stops, Busstop):
            self.bus_stops.append(bus_stops)
        elif type(bus_stops) is list:
            self.bus_stops.extend(bus_stops)