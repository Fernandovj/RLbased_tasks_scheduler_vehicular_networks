import ql_agent
import server_utilization
import substrate_graph
import networkx as nx
from networkx.readwrite import json_graph
from scipy.spatial import distance
import random

action_space = [0,1,2,3,4]
#action_space = [0] #cloud only


n_actions = len(action_space)
#n_states = 11**5
n_states = 21**5

end_sim_time = 600

arrival_rates = [0.9,0.8,0.5,0.3,0.7]
service_rates = [1,1,1,1,1]

radio = 900 #coverage radio of RSUs


def get_reward(node,vehicle_location,utilizations,tre):
    '''
    tr: response time
    tre: max time to execute rerouting task again
    tproc: processing time
    tprop: propagation time
    '''

    tprop = get_propagation_time(node,vehicle_location)
    tproc = get_processing_time(node, utilizations[node])
    tr = tprop + tproc
    reward = float(tr/tre)
    # reward = 1/float(tr/tre)
    
    return reward, tr


def get_propagation_time(node, vehicle_location):
    '''
    - node is the selected action, i.e., the src node
    - dist_v_rsu: the distance from the vehicle to closer RSU
    - dist_between_nodes: distance between src node and dst node (RSU covering the vehicle)
    - of_speed: Optic Fiber speed (see ref http://www.iteejournal.org/Download_jun18_pdf_4.pdf)    
    (see ref https://github.com/sommer/veins/blob/master/src/veins/base/connectionManager/ChannelAccess.cc )
    
    '''
    radio_speed = substrate_graph.radio_speed
    of_speed = substrate_graph.optic_fiber_speed

    myRSU = get_closer_RSU(vehicle_location)
    dist_v_rsu = distance.euclidean(vehicle_location,myRSU["location"])

    if myRSU["id"] == node:
        tprop = dist_v_rsu/radio_speed
    else:
        # dist_rsu: the distance of the to RSU of coverage in backbone
        dist_between_nodes = get_distance_to_RSU(node, myRSU["id"])
        dist_from_cloud_to_node = get_distance_to_RSU(0, node)
        tprop1 = dist_v_rsu/radio_speed
        # tprop2 = dist_between_nodes/of_speed
        tprop2 = dist_between_nodes+dist_from_cloud_to_node/of_speed
        tprop = tprop1 + tprop2 
    return tprop

def get_processing_time(node,utilization):
    '''
    arrival_rate: arrivals occur at a rate according to a Poisson process 
    service_time: have an exponential distribution with rate parameter service_time in the M/M/1 queue, where 1/service_rate is the mean service time
    tproc: total wait time, includes queueing and processing
    '''
    arrival_rate = arrival_rates[node]
    service_rate = service_rates[node]
    tproc = utilization/(service_rate-arrival_rate) + 1/service_rate 

    #tproc = 1/(service_time - arrival_rate)
    return tproc


#def apply_action(action,current_vehile_loc,next_vehicle_loc,utilizations,tre):
#    reward = get_reward(action,current_vehile_loc,utilizations,tre)
#    next_state = get_state(next_vehicle_loc)


def get_state(vehicle_loc):
    utilizations = get_nodes_utilizations()
    distances = get_nodes_distances(vehicle_loc)
    state_ = build_state(utilizations,distances)
    state = translateStateToIndex(state_)
    return state, utilizations, distances, state_

def get_nodes_utilizations(): 
    #utilization in cloud:
    utilization_list = []
    #utl_cloud = server_utilization.simulate(1/arrival_rates[0],1/service_rates[0],end_sim_time,1)
    #utilization_list.append(round(utl_cloud))

    #utilization in edge nodes:
    for i in range(len(arrival_rates)):
        utilization = server_utilization.simulate(1/arrival_rates[i],1/service_rates[i],end_sim_time,1)
        utilization_list.append(round(utilization))
    #print(utilization_list)
    return utilization_list

def get_nodes_distances(vehicle_loc): #distances from the vehicle to each node (cloud and edge nodes)
    distances = {}
    #nodes_locations = get_nodes_locations() #get location of edge nodes and cloud
    myRSUs = get_my_RSUs(vehicle_loc) #get RSU covering the vehicle location
    nodes = substrate_graph.substrate["graph"]["nodes"]
    
    for dst in nodes: #get shortest path distance
        if dst["id"] in myRSUs:

            distances[dst["id"]] = distance.euclidean(vehicle_loc,dst["location"])
            #print(distances)
        else:
            shortest_distance = 0

            for src in myRSUs:
                # distance includes access and core network:
                distance_to_RSU = distance.euclidean(vehicle_loc,nodes[src]["location"]) + get_distance_to_RSU(src,dst["id"])
    
                if distance_to_RSU < shortest_distance or shortest_distance == 0:
                    shortest_distance = distance_to_RSU
            
            distances[dst["id"]] = shortest_distance
               
        #dist =
        #distances[]
    #print(distance_list)
    return distances

def get_nodes_locations():
    locations = []
    nodes = substrate_graph.substrate["graph"]["nodes"]
    for node in nodes:
        locations.append(node["location"])
    #print(locations)
    return locations

def get_my_RSUs(vehicle_location): #get RSUs covering the vehicle location
    my_RSUs = []
    nodes = substrate_graph.substrate["graph"]["nodes"]

    #print("---",nodes)   
    for i in range(1,len(nodes)): #edge nodes are considered only
        #print("###:",i, vehicle_location,nodes[i]["location"])
        dist = distance.euclidean(vehicle_location,nodes[i]["location"])
        if dist <= radio:
            my_RSUs.append(nodes[i]["id"])

    return my_RSUs


def get_distance_to_RSU(src, tar):
    
    #G = nx.node_link_graph(substrate_graph.substrate["graph"]) #graph format
    G = json_graph.node_link_graph(substrate_graph.substrate["graph"])
    path = nx.shortest_path(G, source=src, target=tar)
    hop_distance = 625 #distance in meters in a hop among RSUs
    dist_rsu = (len(path)-1)*hop_distance
    #print("*",len(path))
    return dist_rsu

def translateStateToIndex(state):
    '''
    returns state index from a given state code
    '''
    #size = 11 #possible values each variable can take
    size = 21
    
    index = state[0]*(size**4) + state[1]*(size**3) + state[2]*(size**2) + state[3]*size + state[4]
    return int(index)

# def build_state(distances):
#     max_distance = 3394
#     state = []
#     for i in distances:
#         state.append(round(distances[i]/max_distance*10))
#     return state

# def build_state(utilizations):
#     max_utl = 100
#     state = []
#     for utl in utilizations:
#         state.append(round(utl/max_utl*10))
#     return state

def build_state(utilizations,distances):
    #5 variables, each one can take 21 different values [0,20]: n_states = 21**5
    #max_value = 100
    max_utl = 100
    max_distance = 3394
    state = []
    for i in range(len(utilizations)):
        state.append(int(round(utilizations[i]/max_utl*10) + round(distances[i]/max_distance*10)))

    return state

def get_closer_RSU(vehicle_location):
    closer_RSU = None
    shortest_distance = 0
    nodes = substrate_graph.substrate["graph"]["nodes"]    
    for i in range(1,len(nodes)): #edge nodes are considered only
        distance_to_RSU = distance.euclidean(vehicle_location,nodes[i]["location"])
        if distance_to_RSU < shortest_distance or shortest_distance == 0:
            shortest_distance = distance_to_RSU 
            closer_RSU = nodes[i]
    return closer_RSU

#print("closer RSU:",get_closer_RSU((0,2400)))

def reponse_time(vehicle_location,node):
    src_id = 0
    src_loc = substrate_graph.substrate["graph"]["nodes"][src_id]["location"]    
    closer_RSU = get_closer_RSU(vehicle_location) 
    response_time = 1

    return response_time


#response_time = nx.shortest_path(G,nodes[src]["location"],nodes[dst]["location"]) + distance.euclidean(nodes[dst]["location"],vehicle_loc)


# utilizations = get_nodes_utilizations()
# print("utilizations:", utilizations)
# #print("state utilizations:",build_state(utilizations))
# #print("state index:",translateStateToIndex(build_state(utilizations)))

# vehicle_loc = [500,1200] #get vehicle location from traci
# distances = get_nodes_distances(vehicle_loc)
# print("distances:",distances)
# #print("state:",build_state(distances))
# #print("state index:",translateStateToIndex(build_state(distances)))

# print("state:", build_state(utilizations,distances))
# print("state:", translateStateToIndex(build_state(utilizations,distances)))
# print("state:", translateStateToIndex([0,0,0,0,0]))
# print("state:", translateStateToIndex([20,20,20,20,20]))

#0,1,2,3,4
#state_list_ = [80+40,40+90,90+40,60+70,40+90] #max= 200

#state_list = [0.6,0.65,0.65,0.65,0.65] 
             #[] 



#state_list_ = [60+60, 50+30, 40+90, 70+60, 40+90]
#state_list = [0.6,0.65,0.65,0.65,0.65]#12


#state_list_ = [2+3, 5+1, 4+1, 3+2, 4+4]
#state_list = [6,6,5,5,8]






 