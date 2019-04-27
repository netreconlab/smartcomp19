from __future__ import division #this is only neccesary for python 2
import sim as sim
import math

class Bus:
    import itertools
    #newid = itertools.count().next
    class_counter = 0

    def __init__(self, initial_location, velocity, route = None):
        self.id = 'B' + str(Bus.class_counter)
        self.route = route
        self.velocity = velocity
        self.initial_location = initial_location
        self.location = None
        self.trip_time = None

        Bus.class_counter += 1

    def __str__(self):
        return "id: {0}, route: {1}, velocity: {2}, trip_time: {3}, initial_location: {4} "\
            .format(self.id, self.route.id, self.velocity, round(self.trip_time,2), self.initial_location)


    def set_trip_time(self):
        self.trip_time = abs( self.route.circ / (self.velocity/60/60) )

    def set_route(self, Route):
        self.route = Route
        self.set_trip_time()


    def get_location(self, time):
        # new_loc formula is based on my model
        time = time if time != None else sim.timestep

        sign = abs(self.velocity) / self.velocity
        vel = abs(self.velocity)
        displacement = ( vel * (time/60/60) ) % self.route.circ # in kilometers
        displacement = displacement * sign
        new_loc = self.initial_location + ((displacement/self.route.circ) * 2*math.pi)

        if new_loc < 0:
            new_loc = 2*math.pi + new_loc
        else:
            new_loc = new_loc % (2*math.pi)

        self.location = new_loc

        #print('yyyy',  new_loc)
        return self.location


class Message:
    class_counter = 0

    def __init__(self, size, time_created, source):
        self.id = 'M' + str(Message.class_counter)
        self.size = size
        self.time_created = time_created
        self.time_delivered = None
        self.delivered = False
        self.source = source

        Message.class_counter += 1



class Gateway:
    class_counter = 0

    def __init__(self, route, bus_stop):
        self.id = 'G' + str(Gateway.class_counter)
        self.route = route
        self.location = bus_stop.location
        self.bus_stop = bus_stop

        Gateway.class_counter += 1

    def set_route(self, Route):
        self.route = Route

    def __str__(self):
        return "id: {0}, route: {1}, location: {2}, bus_stop: {3} " \
            .format(self.id, self.route.id, self.location, self.bus_stop.id)




class Busstop:
    class_counter = 0

    def __init__(self, route, location):
        self.id = 'BS' + str(Busstop.class_counter)

        self.routes = [route]
        self.location = location
        #prob of bus stopping

        Busstop.class_counter += 1




class Pedestrian:
    class_counter = 0

    def __init__(self, ridership_rate, start_time):
        self.id = 'P' + str(Pedestrian.class_counter)
        self.ridership_rate = ridership_rate
        self.start_time = start_time
        self.associated_routes = None
        self.associated_busstops = None

        Pedestrian.class_counter += 1


    def get_random_busstops(self, routes, qty):
        from numpy.random import choice
        ass_routes = []
        ass_busstops = []
        for q in range(qty):
            r = choice(routes)
            ass_routes.append(r)
            ass_busstops.append(choice(r.bus_stops))

        return ass_routes, ass_busstops


    def assign_busstops(self, routes):
        self.associated_routes, self.associated_busstops = self.get_random_busstops(routes=routes, qty=5)


    def get_delay(self, time):
        return (self.start_time + time) % self.ridership_rate # all in secs