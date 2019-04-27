import math, random
import sim as sim
from components import *
from sensor import *
import generators as gen
from probabilities import *
import numpy as np



def busstop_to_bus_delay(carrier, time = None):
    # carrier can either be a busstop or sensor
    # returns a dict
    t_bs = {}
    for route in carrier.routes:
        for bus in route.buses:
            g_x = carrier.location - bus.get_location(time)
            #print(g_x)

            if g_x / bus.velocity >= 0:
                dist_bs = abs(g_x)

            else:
                dist_bs = ((2*math.pi) + abs(g_x) ) % (2*math.pi)

            #print(dist_bs)
            # TODO:: modify to work with multiple routes
            delay = ( (dist_bs / (2*math.pi)) * carrier.routes[0].circ ) / abs(bus.velocity / 60 / 60)
            #print(delay)

            # store delays
            t_bs[bus.id] = (delay, bus_to_gateway_delay(carrier, bus))

    return t_bs



def bus_to_gateway_delay(carrier, bus):
    # carrier can either be a busstop or sensor
    result = {}

    for gw in bus.route.gateways:
        h_x = gw.location - carrier.location

        if h_x / bus.velocity >= 0:
            dist_bg = abs(h_x)
        else:
            dist_bg = ((2 * math.pi) + abs(h_x)) % (2 * math.pi)

        delay = ((dist_bg / (2 * math.pi)) * bus.route.circ) / abs(bus.velocity / 60 / 60)

        #print(h_x)

        result[gw.id] = delay

    return result


def get_min_busstop_to_gateway_latency(sensor, result):
    import sys
    minimum = sys.float_info.max
    tbs_tbg = (None, None)

    for i, x in result.items():
        for j, y in x[1].items():
            if x[0]+y < minimum:
                minimum = x[0]+y
                tbs_tbg = (x[0],y)

    sensor.msg_tbs.append(tbs_tbg[0])
    sensor.msg_tbg.append(tbs_tbg[1])

    #print(tbs_tbg)

    return minimum



def get_ped_arrival_rate():
    rate = trunc_normal_dist(sim.ped_arrival_mean_sd[0], sim.ped_arrival_mean_sd[1], 0, 5, n=1)[0]
    #rate is per hour, convert to per sec
    return rate/(60*60)




def get_ons_delay(sensor):
    result = busstop_to_bus_delay(sensor)
    minimum = get_min_busstop_to_gateway_latency(sensor, result)

    return result, minimum


def get_ofs_delay(sensor):

    # arrival rate, how many ped riders pass the sensor per second
    t_sp = 1 / get_ped_arrival_rate()  # converts arrival rate to per sec

    # pick pedestrian at random
    index1 = random_int(0, len(gen.pedestrians)-1)
    ped = gen.pedestrians[index1]
    index2 = random_int(0, len(ped.associated_busstops) - 1)
    busstop = ped.associated_busstops[index2]
    route = ped.associated_routes[index2]



    # in situations where the pedestrian delivers the code directly
    prob_of_direct = sim.pct_ped_to_gw/100
    direct = np.random.choice([True, False], 1, p=[prob_of_direct, 1-prob_of_direct])[0]

    if direct:

        sensor.msg_tbs.append(None)
        sensor.msg_tbg.append(None)

        t_pg = trunc_normal_dist(sim.ped_direct_delivery_mean_sd[0], sim.ped_direct_delivery_mean_sd[1], 0.1*60*60, 24*60*60, n=1)[0]

        result = t_sp + t_pg

        sensor.msg_tsp.append(t_sp)
        sensor.msg_tpbs.append(t_pg)

        #print(t_pg)

        minimum = result

    else:
        future_time1 = t_sp + sim.timestep
        t_pbs = ped.get_delay(time = future_time1)

        future_time2 = sim.timestep + t_sp + t_pbs
        t_bsg = busstop_to_bus_delay(carrier=busstop, time = future_time2)  # t_sb + t_bg

        result = t_sp, t_pbs, t_bsg
        #print(busstop.location)

        minimum = t_sp + t_pbs + get_min_busstop_to_gateway_latency(sensor, t_bsg)

        # get_min_busstop_to_gateway_latency(t_bsg) appends msg_tbs and msg_tbg
        sensor.msg_tsp.append(t_sp)
        sensor.msg_tpbs.append(t_pbs)

        if (minimum == None):
            print('yess')

    # print ('time:', sim.timestep, 'sensor:', sensor.id, 'route:', sensor.route.id, 'min_delay:',round(minimum,2), sep='\t')
    return result, minimum


def time_step():
    for s in gen.sensors:

        # if sensor has not generated a new message, skip
        if not s.generate_msg():
            continue


        # calculate the latency (tbs and tbg)
        elif isinstance(s, OnStreetSensor):
            result, minimum = get_ons_delay(s)
            s.msg_generated += 1
            s.msg_latencies.append(minimum)
            s.gen_times.append(sim.timestep)


        elif isinstance(s, OffStreetSensor):
            result, minimum = get_ofs_delay(s)
            #print(minimum)
            s.msg_generated += 1
            s.gen_times.append(sim.timestep)
            s.msg_latencies.append(minimum)



def show_result():

    print('\nStreet-side sensors')
    for s in gen.sensors:
        if isinstance(s, OnStreetSensor):
            #print(s.msg_latencies)
            print('sensor {0}, route:{1}, location {6}, msg_count:{2}, mean-latency:{3}, min-latency:{4}, max-latency:{5}' \
                  .format(s.id, [r.id for r in s.routes], s.msg_generated, round(np.mean(s.msg_latencies), 2), round(min(s.msg_latencies), 2), round(max(s.msg_latencies), 2), s.location), sep='\t')

    print('\nOff-street sensors')
    for s in gen.sensors:
        if isinstance(s, OffStreetSensor):
            #print(s.msg_latencies)
            print('sensor {0}, msg_count:{1}, mean-latency:{2}, min-latency:{3}, max-latency:{4}'\
                  .format(s.id,  s.msg_generated, round(np.mean(s.msg_latencies),2), round(min(s.msg_latencies),2), round(max(s.msg_latencies),2)), sep='\t')
            #print(s.msg_latencies)

    pass



def store_results():
    import json
    from collections import defaultdict
    final_result = defaultdict(list)

    final_result['sim_time'] = sim.duration

    for s in gen.sensors:
        if isinstance(s, OnStreetSensor):

            data = {
                'minimum_roundtrip_time':s.get_minimum_round_trip_time(),
                'no_of_buses': s.get_total_bus_count(),
                'no_of_routes': len(s.routes),
                'all_latencies': s.msg_latencies,
                'all_tbs_latencies': s.msg_tbs,
                'all_tbg_latencies': s.msg_tbg,
                'all_gen_times': s.gen_times,
                'delivered_latencies': [],
                'delivered_gen_times': [],
                'delivered_tbs_latencies':[],
                'delivered_tbg_latencies': []

            }

            for i in range(len(s.msg_latencies)):
                if s.gen_times[i] + s.msg_latencies[i] < sim.duration:
                    data['delivered_latencies'].append(s.msg_latencies[i])
                    data['delivered_gen_times'].append(s.gen_times[i])

                    data['delivered_tbs_latencies'].append(s.msg_tbs[i])
                    data['delivered_tbg_latencies'].append(s.msg_tbg[i])

            data['delivery_rate'] = len(data['delivered_latencies']) / len(data['all_gen_times'])

            final_result['ons'].append(data)


        if isinstance(s, OffStreetSensor):
            data = {
                'all_latencies': s.msg_latencies,
                'all_gen_times': s.gen_times,
                'delivered_latencies': [],
                'delivered_gen_times': [],
                'delivered_tsp_latencies': [],
                'delivered_tpbs_latencies': [],
                'delivered_tbs_latencies': [],
                'delivered_tbg_latencies': []
            }

            for i in range(len(s.msg_latencies)):
                if s.gen_times[i] + s.msg_latencies[i] < sim.duration:

                    data['delivered_latencies'].append(s.msg_latencies[i])
                    data['delivered_gen_times'].append(s.gen_times[i])

                    data['delivered_tsp_latencies'].append(s.msg_tsp[i])
                    data['delivered_tpbs_latencies'].append(s.msg_tpbs[i])
                    data['delivered_tbs_latencies'].append(s.msg_tbs[i])
                    data['delivered_tbg_latencies'].append(s.msg_tbg[i])


            data['delivery_rate'] = len(data['delivered_latencies']) / len(data['all_gen_times'])

            final_result['ofs'].append(data)



    with open('results/data_{0}.txt'.format(sim.seed), 'w') as outfile:
        json.dump(final_result, outfile, indent=True)



if __name__ == '__main__':

    import importlib

    for i in range(sim.no_of_seeds):

        importlib.reload(gen)

        sim.seed = i

        np.random.seed(sim.seed)
        random.seed(sim.seed)

        gen.run()

        for time in range(sim.duration):
            sim.timestep = time
            time_step()

            if (time/60) % 60 == 0:
                #print(time/60/60, 'hours')
                pass

        store_results()
    #show_result()