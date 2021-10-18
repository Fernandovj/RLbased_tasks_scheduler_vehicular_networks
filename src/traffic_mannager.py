import traci
import logging
import networkx as nx
import random
import time

import log_mannager
import rsu_mannager

import RL_utils
import baselines

def update_traffic_on_roads(graph): #, safety_file_name):

    for road in graph.nodes_iter():

        average_speed = traci.edge.getLastStepMeanSpeed(road)
        max_speed = traci.lane.getMaxSpeed(str(road) + "_0")
        dummy_speed = float(max_speed - average_speed) / float(max_speed)
        #dummy_speed = max_speed - average_speed

        for successor_road in graph.successors_iter(road):

            if road[0] != ':':
                graph.edge[road][successor_road]["weight"] = (graph.edge[road][successor_road]["weight"] + dummy_speed) / 2.0

            else: 
                graph.edge[road][successor_road]["weight"] = (graph.edge[road][successor_road]["weight"] + dummy_speed) / 2.0
                
    return graph


def reroute_vehicles(graph, rsu_list, radius, agente, tre):

    time_sum = 0
    min_time = 10
    max_time = 0
    total_routes = 0
    #print("*traci.vehicle.getIDList()",traci.vehicle.getIDList())
    #---w
    episode_reward = 0
    episode_response_time = 0
    #episode_travel_time = 0
    #---w

    vehicles_list = traci.vehicle.getIDList()
    first_state = True #---w
    for i in range(len(vehicles_list)):
    #for vehicle in traci.vehicle.getIDList():
        vehicle = traci.vehicle.getIDList()[i]
        source = traci.vehicle.getRoadID(vehicle)

        if source.startswith(":"): 
            continue
        else:
            route = traci.vehicle.getRoute(vehicle)
            destination = route[-1]

        #start = time.time()
        #logging.debug("Calculating optimal path for pair (%s, %s)" % (source, destination))
        #shortest_path = nx.dijkstra_path(graph, source, destination, "weight")
        #result_time = time.time() - start
        #print result_time
        # time_sum += result_time

        # if result_time < min_time:
        # 	min_time = result_time

        # if result_time > max_time:
        # 	max_time = result_time

        total_routes += 1

        #---w
        vehicle_loc = traci.vehicle.getPosition(vehicle)
        #print("*vehicle_loc:",vehicle_loc)
        
        if first_state: # i == 0:                
            state, utilizations, distances, state_ = RL_utils.get_state(vehicle_loc)
            print("*state",state)
            action = agente.take_action(state) #node selection
            # action = baselines.take_action("cyclic",0)
            # action = baselines.take_action("random",0)
            # action = baselines.take_action("closer",vehicle_loc)
            # action = baselines.take_action("cloud",0)

        # --- execute re-routing in selected node:
        logging.debug("Calculating optimal path for pair (%s, %s)" % (source, destination))
        shortest_path = nx.dijkstra_path(graph, source, destination, "weight")
        #traci.vehicle.setRoute(vehicle, shortest_path)
        # ---
        
        reward, response_time = RL_utils.get_reward(action,vehicle_loc,utilizations,tre)
        episode_reward += reward
        episode_response_time += response_time
        #episode_travel_time += get_travel_time(vehicle)
        
        if i != len(vehicles_list)-1: # if not end_state 
            next_vehicle_loc = traci.vehicle.getPosition(vehicles_list[i+1])
            next_state, a, b, c = RL_utils.get_state(next_vehicle_loc) # next_state
            # print("*next_state",next_state)
            next_action = agente.take_action(next_state)
            # next_action = baselines.take_action("cyclic",0)
            # next_action = baselines.take_action("random",0)
            # next_action = baselines.take_action("closer",vehicle_loc)
            # next_action = baselines.take_action("cloud",0)
            agente.updateQ(reward,state,action,next_state,next_action,False) 
        else:
            agente.updateQ(reward,state,action,None,None,True)  

        state = next_state
        action = next_action
        first_state = False    


        #---w

        # convering_rsu = rsu_mannager.get_rsu_covering(source, rsu_list)

        # if convering_rsu == None:
        #     continue

        # path_within_rsu_coverage = filtering_route(rsu_list[convering_rsu], source, route)

        # if path_within_rsu_coverage != None:

        #     if len(path_within_rsu_coverage) > 2:
        #         destination = path_within_rsu_coverage[-1]

        #         if source != destination:

        #             logging.debug("Compute paramenters scheduler")
        #             print get_scheduler_parameters(source, destination, rsu_list, route)

        #             logging.debug("Calculating optimal path for pair (%s, %s)" % (source, destination))
        #             shortest_path = nx.dijkstra_path(rsu_list[convering_rsu]['subgraph'], source, destination, "weight")
        #             alternative_path = shortest_path + route[route.index(destination) + 1:]
        #             traci.vehicle.setRoute(vehicle, alternative_path)
    #---w
    mean_reward = episode_reward/len(vehicles_list)
    mean_reponse_time = episode_response_time/len(vehicles_list)
    #mean_travel_time = episode_travel_time/len(vehicles_list)    
    #---w
    #print 'mean time: ', float(time_sum) / float(total_routes)
    #print 'max time: ', max_time
    #print 'min time: ', min_time
    return mean_reward, mean_reponse_time, #mean_travel_time #---w


def filtering_route(rsu, current_edge, route):
    
    path_within_rsu_coverage = []

    for edge in route[route.index(current_edge):]:
        if edge not in rsu['edges']:
            return path_within_rsu_coverage

        path_within_rsu_coverage.append(edge)


def get_scheduler_parameters(source, destination, rsu_list, route):

    # rsu_source = rsu_mannager.get_rsu_covering(source, rsu_list)
    rsu_fog_destination = rsu_mannager.get_rsu_covering(destination, rsu_list)
    rsu_clod_destination =rsu_mannager.get_rsu_covering(route[-1], rsu_list)

    domain = rsu_fog_destination == rsu_clod_destination
    # if domain:
    #     print destination
    #     print route[-1]
    within_route = route[route.index(source): route.index(destination) + 1]
    time_to_change_route = get_time_to_reach_congested_road(within_route)
    critical_level = get_critical_level(within_route)
    traffic_condition_destination = is_destination_congested(destination)

    return domain, time_to_change_route, critical_level, traffic_condition_destination


def get_time_to_reach_congested_road(route, threshold=0.6):

    total_time = 0

    for edge in route:
        traffic_condition = get_weight(edge)

        if traffic_condition >= threshold:
            break

        else:
            total_time += traci.edge.getTraveltime(edge)

    return total_time

def is_destination_congested(destination, threshold=0.6):

    traffic_condition = get_weight(destination)
    return traffic_condition >= threshold

def get_weight(edge):
    average_speed = traci.edge.getLastStepMeanSpeed(edge)
    max_speed = traci.lane.getMaxSpeed(str(edge) + "_0")

    return float(max_speed - average_speed) / float(max_speed)


def get_critical_level(route, threshold=0.6):

    critical_level = len(route)

    for edge in route:
        traffic_condition = get_weight(edge)

        if traffic_condition >= threshold:
            critical_level = route.index(edge)

    return critical_level


def get_travel_time(vehicle): #--new

    route = traci.vehicle.getRoute(vehicle)
    route_index = traci.vehicle.getRouteIndex(vehicle)
    travel_time = 0

    for edge in route[route_index:]:
        travel_time += traci.edge.getTraveltime(edge)

    return travel_time
