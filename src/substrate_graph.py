
#Types-> 0:cloud, 1:edge/fog
#cpu: cpu occupation 0-100%
#speed: m/s

optic_fiber_speed = 205337300 #velocity factor for optic fiber in m/s
radio_speed = 299792458 #light speed in m/s

substrate = {
    "graph": {

        "nodes": [
            {"id": 0, "type": 0, "cpu": 0, "location":(2400,2400)}, #definir cloud position
            {"id": 1, "type": 1, "cpu": 0, "location":(625,1875)}, 
            {"id": 2, "type": 1, "cpu": 0, "location":(1875,1875)},
            {"id": 3, "type": 1, "cpu": 0, "location":(1875,625)},
            {"id": 4, "type": 1, "cpu": 0, "location":(625,625)}
        ], 
        "links": [
            {"source": 1, "target": 2, "length":0, "speed":optic_fiber_speed}, 
            {"source": 2, "target": 4, "length":0, "speed":optic_fiber_speed}, 
            {"source": 3, "target": 4, "length":0, "speed":optic_fiber_speed},
            {"source": 4, "target": 1, "length":0, "speed":optic_fiber_speed}, 
            {"source": 0, "target": 2, "length":0, "speed":optic_fiber_speed} # this link represents the backhaul
        ]
    }
}