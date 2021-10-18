import traci


def log_vehicles_route(route_list):

    vehicles_list = traci.vehicle.getIDList()

    current_road = ''

    for vehicle in vehicles_list:

        if vehicle in route_list.keys():
            current_road = traci.vehicle.getRoadID(vehicle)

            if current_road != route_list[vehicle][-1] and current_road[0] != ':':
                route_list[vehicle].append(current_road)

        else:
            current_road = traci.vehicle.getRoadID(vehicle)

            if current_road[0] == ':':
                continue

            else:
                route_list[vehicle] = [current_road,]

    return route_list

def log_densidade_speed(time):
    vehicles = traci.vehicle.getIDList()
    density = len(vehicles)
    speed = []

    output = open('output/average_speed_DSP.txt', 'a')

    for v in vehicles:
        lane_pos = traci.vehicle.getLanePosition(v)
        edge = traci.vehicle.getRoadID(v)
        if edge.startswith(":"): continue
        position = traci.vehicle.getPosition(v)        
        route = traci.vehicle.getRoute(v)
        index = route.index(edge)
        if index > 0:
            distance = 500 * (index - 1) + lane_pos
        else:
            distance = lane_pos

        traveltime = traci.vehicle.getAdaptedTraveltime(v, time, edge)
        speed.append(float(distance)/float(time))
    
    output.write(str(np.amin(speed) * 3.6) + '\t' + str(np.average(speed) * 3.6) + '\t' + str(np.amax(speed) * 3.6) + '\t' + str(density)+'\n')

def log_pareto_set(PD, destination, max_safety, weight_shortest_path, vehicle):

    pareto_file = open('Pareto/'+vehicle+ '.txt', 'w')
    pareto_file.write(str(max_safety) + '\n')
    pareto_file.write(str(weight_shortest_path) + '\n')

    for safety in range(1, max_safety+1):
        pareto_file.write(str(PD[(destination, safety)]) + ' ') 

    pareto_file.close()

def log_route(route_log, route_list, replication):
    route_file = open(str(route_log) + '_' + str(replication) + '.txt', 'w')

    for vehicle in route_list.keys():

        route_file.write(str(vehicle) + '\t')

        for road in route_list[vehicle]:
            route_file.write(str(road) + '\t')

        route_file.write('\n')

    route_file.close()