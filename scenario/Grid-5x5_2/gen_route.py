#!/usr/bin/env python
import os
from bs4 import BeautifulSoup
import random

# Relative to sumo-launchd.py directory
LAUNCHD_BASE_DIR = "."
#RANDOM_TRIP_FILE = "/usr/share/sumo/tools/trip/randomTrips.py"
#RANDOM_TRIP_FILE = "~/PhD/Environment/sumo-0.24.0/tools/randomTrips.py "
RANDOM_TRIP_FILE = "/opt/sumo-0.25.0/tools/randomTrips.py"
DADUAROUTER_FILE = "duarouter" 
NETWORK_FILE_NAME = "grid.net.xml"
TRAFFICS = (3602,)
REPLICATIONS = 1

def build_route_files():
    for traffic in TRAFFICS:
        for replication in range(REPLICATIONS):
            # create routes files
            random_trip_cmd = "python " + RANDOM_TRIP_FILE + " -n " + NETWORK_FILE_NAME + " -b 0 -e " + str(traffic) + " -s " + str(random.randint(1,99))+  " -p "+ str(0.3) +" -r " + str(traffic) + "_" + str(replication) + "_routes.rou.xml"
            print random_trip_cmd
            os.system(random_trip_cmd) 
            
            os.system("rm " + str(traffic) + "_" + str(replication) + "_routes.rou.alt.xml")
            
def build_cfg_files():
    for traffic in TRAFFICS:
        for replication in range(REPLICATIONS):
            soup = "<?xml version=\"1.0\"?>\
                        \n<configuration>\
                            \n<input>\
                                \n<net-file value=\""+ str(NETWORK_FILE_NAME) +"\" />\
                                \n<route-files value=\""+ str(traffic) + "_" + str(replication) + ".rou.xml" +"\" />\
                            \n</input>\
                            \n<time>\
                                \n<begin value=\"0\" />\
                                \n<end value=\"5000\" />\
                            \n</time>\
			\n<routing-algorithm value=\"dijkstra\" />\
			\n<time-to-teleport value=\"160\" />\
                        \n</configuration>"
            
            # net_tag = soup.find("net-file")
            # net_tag["value"] = NETWORK_FILE_NAME
	    
            
            
            # route_tag = soup.find("route-files")
            # route_tag["value"] = str(traffic) + "_" + str(replication) + ".rou.xml"                                                   
            
            f = open(str(traffic) + "_" + str(replication) + ".sumo.cfg", "w")
            f.write(soup)
            f.close()
            
def build_launchd_files():
    for traffic in TRAFFICS:
        for replication in range(REPLICATIONS):
            soup = "<?xml version=\"1.0\"?>\
                        \n<launch>\
                            \n<copy file=\""+ str(NETWORK_FILE_NAME) +"\" />\
                            \n<copy file=\""+ str(traffic) + "_" + str(replication) + ".rou.xml" + "\" />\
                            \n<copy file=\""+ str(traffic) + "_" + str(replication) + ".sumo.cfg" + "\" type=\"config\" />\
                        \n</launch>"
            
                       
            # copy_tags = soup.find_all("copy")
            # copy_tags[0]["file"] = NETWORK_FILE_NAME
            # copy_tags[1]["file"] = str(traffic) + "_" + str(replication) + ".rou.xml"
            # copy_tags[2]["file"] = str(traffic) + "_" + str(replication) + ".sumo.cfg"
                                                                                                    
            f = open(str(traffic) + "_" + str(replication) + ".launchd.xml", "w")
            f.write(soup)
            f.close()                                 
            
def remove_depart():
    for traffic in TRAFFICS:
        for replication in range(REPLICATIONS):
            file = open(str(traffic) + "_" + str(replication)+'_routes.rou.xml', 'r+')
            output = open(str(traffic) + "_" + str(replication)+'.rou.xml', 'w')

            data = file.readlines()
	        
            for item in data:
                output.write(item)
            os.system("rm " + str(traffic) + "_" + str(replication) + "_routes.rou.xml")


if __name__ == "__main__":
    build_route_files()
    build_cfg_files()
    build_launchd_files()
    remove_depart()
