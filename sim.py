# sim.py

no_of_seeds = 5
seed = None
duration = 48 * 60 * 60
timestep = None
#rider_freq = [5, 3, 1, 0]   #[5-7, 3-4, 2-1] per week [0.68, 0.21, 0.11]
#rider_freq_distribution = [0.68, 0.21, 0.10, 0.01]
no_of_routes = 32
no_of_pedestrians = 2000
no_of_ofs = 100
pct_ofs_sensors = 0.1
b_s_mean_sd_dist = [1, 0.5]
no_of_bs_per_route_mean_sd = [72, 52]
ped_arrival_mean_sd = [2, 0.5] # mean 2 every hour

bus_per_route = [1, 2]
ons_per_route = [2, 8]
gw_per_route = [1, 2]

## Bus service averages 12.1 miles per hour. or 19.47 km/hr.
min_bus_velo, max_bus_velo = 17.47, 21.47
# 4.11 feet per sec for older people, 4.95 feet per second for younger.  4.5 km/hr and 5.43 km/hr
#ped_velocity_range = [4.5, 5.43]
route_circ_mean_sd = [15, 7] # in kilometer
pct_ped_to_gw = gw_per_route[1]/no_of_bs_per_route_mean_sd[0] # in percentage
ped_direct_delivery_mean_sd = [2*60*60, 30*60] #  2 every hour
routes_per_ons = [1,1]
