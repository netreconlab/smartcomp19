from route import Route
from components import *
from probabilities import *
import math, random
from sensor import *
import numpy as np

np.random.seed(sim.seed)

ped_arrival_rate_range = []
ped_bus_arrival_rate_range = []
msg_ttl_range = []

routes = []
busstops = []
buses = []
gateways = []
pedestrians = []
ons_sensors = []
ofs_sensors = []
sensors = []
no_of_buses = 0
no_of_ons_sensors = 0
no_of_gateways = 0
no_of_ofs = 0


def generate_routes(no_of_routes):
    global no_of_buses, routes, no_of_ons_sensors, no_of_gateways, no_of_ons_sensors

    #generates random values from normal dist within a range
    circ = trunc_normal_dist(mean=sim.route_circ_mean_sd[0], sd=sim.route_circ_mean_sd[1], low=10, upp=40, n=no_of_routes)


    bus_per_route_distribution = random_int(sim.bus_per_route[0], sim.bus_per_route[1], no_of_routes)
    no_of_buses = sum(bus_per_route_distribution)

    if (sim.ons_per_route[0] == sim.ons_per_route[1] == 0):
        sim.no_of_ons = [0] * no_of_routes
    else:
        sim.no_of_ons = random_int(sim.ons_per_route[0], sim.ons_per_route[1], no_of_routes)


    ons_per_route_distribution = random_int(sim.ons_per_route[0], sim.ons_per_route[1], no_of_routes)
    sim.no_of_ons = sum(ons_per_route_distribution)

    gw_per_route_distribution = random_int(sim.gw_per_route[0], sim.gw_per_route[1], no_of_routes)
    no_of_gateways = sum(gw_per_route_distribution)

    #add new routes
    for i in range(no_of_routes):
        r = Route(circ=circ[i], no_of_buses = bus_per_route_distribution[i], \
                            no_of_gw= gw_per_route_distribution[i], no_of_ons=ons_per_route_distribution[i])
        routes.append(r)




def generate_buses(routes):
    global buses

    init_loc = uniform_dist(low=0, high=(2 * math.pi), n = no_of_buses)

    velocity = uniform_dist(sim.min_bus_velo, sim.max_bus_velo, no_of_buses)


    for i in range(no_of_buses):
        # alternate the direction of busses
        bus_direction = -1 if i%2 == 0 else 1
        buses.append(Bus(initial_location = init_loc[i], velocity = bus_direction * velocity[i]))

    count =0
    for r in routes:
        for c in range(r.no_of_buses):
           # print ('yes')
            r.add_bus(buses[count])
            buses[count].set_route(r)
            count += 1



def generate_sensors(routes):
    global sensors, ons_sensors, ons_sensors, no_of_ofs

    generate_ons_sensors(routes)

    #no_of_ofs = int ((1 / (1 - sim.pct_ofs_sensors)) * (sim.pct_ofs_sensors * no_of_ons_sensors))
    no_of_ofs = sim.no_of_ofs
    #print

    generate_ofs_sensors(routes)

    sensors = ons_sensors + ofs_sensors


def generate_ons_sensors(routes):
    global ons_sensors

    data_size = [None] * sim.no_of_ons
    #ped_arrival_rate = normal_dist(mean=sim.ped_arrival_mean_sd_dist[0], sd=sim.ped_arrival_mean_sd_dist[1]) #per hour
    msg_gen_rate = random_int(low = 10* 60, high= 2 * 60 * 60, size=sim.no_of_ons) # 10mins to 12 hours
    start_time = random_int(low = 0, high=60 * 60, size=sim.no_of_ons) # 0 to 1 hour
    msg_ttl = [None] * sim.no_of_ons
    # TODO:: change location
    location = uniform_dist(low=0, high=(2  * math.pi), n = sim.no_of_ons)
    no_of_routes = random_int(low=sim.routes_per_ons[0], high=sim.routes_per_ons[1], size=sim.no_of_ons)



    for i in range(sim.no_of_ons):

        s = OnStreetSensor(data_size[i], msg_gen_rate[i], start_time[i], msg_ttl[i], location[i], no_of_routes=no_of_routes[i])
        ons_sensors.append(s)

    count = 0

    for r in routes:
        for c in range(r.no_of_ons):
             r.add_sensors(ons_sensors[count])
             ons_sensors[count].set_route(r)
             count += 1

    for s in ons_sensors:
        size = s.no_of_routes - 1
        while size > 0 and len(routes) > size:
            r =  np.random.choice(routes, size=1)[0]

            if r not in s.routes:
                r.add_sensors(s)
                s.set_route(r)
                size -= 1

    # for r in routes:
    #     for c in range(r.no_of_ons):
    #         r.add_sensors(ons_sensors[count])
    #         ons_sensors[count].set_route(r)
    #         count += 1
    #




def generate_ofs_sensors(routes):
    global ofs_sensors, no_of_ofs

    data_size = [None] * no_of_ofs
    msg_gen_rate = random_int(low = 10* 60, high= 2 * 60 * 60, size=no_of_ofs) # 10mins to 12 hours
    start_time = random_int(low = 0, high=60 * 60, size=no_of_ofs) # 0 to 1 hour
    msg_ttl = [None] * no_of_ofs

    for i in range(no_of_ofs):

        s = OffStreetSensor(data_size[i], msg_gen_rate[i], start_time[i], msg_ttl[i], ped_arrival_rate = None)
        ofs_sensors.append(s)





def generate_pedestrians(routes):

    points, freq_dist = get_rider_distribution()
    frequency = np.random.choice(points, size=sim.no_of_pedestrians, p=freq_dist)  # per week)
    #print(frequency)
    # convert from week to seconds
    start_time =  random_int(low = 0, high= 7 * 60 * 60 * 24, size=sim.no_of_pedestrians) # 0 to 7 days
    frequency = frequency *24 * 60 * 60 # convert to per sec rate
    #print(frequency)

    for i in range(sim.no_of_pedestrians):

        p = Pedestrian(ridership_rate=frequency[i], start_time=start_time[i])
        p.assign_busstops(routes)
        pedestrians.append(p)



def generate_gateways(routes):
    global gateways

    count = 0
    for r in routes:
        #pick k random bus stop indices
        if len(r.bus_stops) < r.no_of_gateways:
            r.no_of_gateways = len(r.bus_stops)
        bus_stops = random.sample(range(0, len(r.bus_stops)), r.no_of_gateways)
        for c in range(r.no_of_gateways):

            bs = r.bus_stops[bus_stops[c]]

            gw = Gateway(route = r, bus_stop = bs)

            gateways.append(gw)

            r.add_gateways(gw)

            gateways[count].set_route(r)

            count += 1



def generate_busstops(routes):
    global busstops

    for r in routes:
        #start = normal_dist(sim.b_s_mean_sd_dist[0], sim.b_s_mean_sd_dist[1])
        #start = random.random(sim.b_s_mean_sd_dist[0])
        total = 0
        while total < (2  * math.pi):
            b_s_kilometre = trunc_normal_dist(mean=r.circ/sim.no_of_bs_per_route_mean_sd[0], sd=r.circ/sim.no_of_bs_per_route_mean_sd[1], low=r.circ/100, upp=r.circ/10)[0]

            b_s_rad = 2 * math.pi * (b_s_kilometre / r.circ)

            total += b_s_rad
            if total >= (2  * math.pi):
                break

            #print(total)

            #TODO: confrim the code below
            b_s = Busstop(r, total)
            r.add_bus_stops(b_s)
            busstops.append(b_s)

    return routes
    


def run():
    global routes
    generate_routes(sim.no_of_routes)
    generate_busstops(routes)
    generate_buses(routes)
    generate_sensors(routes)
    generate_gateways(routes)
    generate_pedestrians(routes)

    # for r in routes:
    #     # print(x.id)
    #     print(r)
    #
    # for g in gateways:
    #     print(g)
    #
    print(len(routes), len(gateways), len(buses), len(pedestrians))
    # for b in buses:
    #     print(b)

   # return routes,busstops,buses,gateways,ons_sensors,ofs_sensors,sensors