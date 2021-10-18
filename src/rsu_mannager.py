import networkx
import numpy as np
import pyproj
import os, sys
import xml.etree.ElementTree as ET

RSU_FILE = "../scenario/Grid-5x5/RSU_positions.txt"
NETWORK_FILE = "../scenario/Grid-5x5/cologne.net.xml"


if 'SUMO_HOME' in os.environ:
     tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
     sys.path.append(tools)
     from sumolib import checkBinary
else:   
     sys.exit("please declare environment variable 'SUMO_HOME'")

import sumolib
import traci


def get_rsu_positions_list():

	rsu_file = open(RSU_FILE, 'r')

	rsu_coordinates_list = {}

	for rsu in rsu_file:
		rsu = rsu.strip().split(' ')
		rsu_coordinates_list[rsu[0]] = {}
		rsu_coordinates_list[rsu[0]]['x'] = float(rsu[1])
		rsu_coordinates_list[rsu[0]]['y'] = float(rsu[2])


	return rsu_coordinates_list

def mapping_latlon2xy(rsu_coordinates_list, net):

	rsu_xy = {}

	for rsu in rsu_coordinates_list.keys():
		id = rsu_coordinates_list[rsu]
		lat = rsu_coordinates_list[rsu][0]
		lon = rsu_coordinates_list[rsu][1]
		x, y = net.convertLonLat2XY(lon, lat)

		rsu_coordinates_list[id] = (x,y)

	return rsu_coordinates_list


def get_edges_within_rsu_coverage(rsu_list, net, radius, G):

	for rsu in rsu_list.keys():
		x = rsu_list[rsu]['x']
		y = rsu_list[rsu]['y']

		edges = net.getNeighboringEdges(x, y, r=radius)

		vertices = []

		for edge in edges:
			edge = ET.fromstring(str(edge[0]))
			vertices.append(edge.get('id'))
			# vertices.append(edge.get('to'))

		rsu_list[rsu]['subgraph'] = G.subgraph(vertices)
		rsu_list[rsu]['edges'] = vertices

	return rsu_list

def get_rsu_covering(current_edge, rsu_list):

	rsu_covering = []

	for rsu in rsu_list.keys():

		if current_edge in rsu_list[rsu]['edges']:
			# rsu_covering.append(rsu)
			return rsu

# def main():

# 	net = sumolib.net.readNet(NETWORK_FILE)
# 	rsu_list = get_rsu_positions_list()

# 	rsu_list = get_edges_within_rsu_coverage(rsu_list, net)


# if __name__ == "__main__":
#     main()  