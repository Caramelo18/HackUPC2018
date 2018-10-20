import yaml
import os
from py2neo import Graph, Node, Relationship

graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)

with open("stations.yml", 'r') as stream:
    stations = {}
    lines = yaml.load(stream)
    for line in lines:
        for station in lines[line]:
            if station not in stations:
                stations[station] = [line]
            else:
                stations[station].append(line)

    print(stations)

    tx = graph.begin()

    station_nodes = {}

    for station in stations:
        node = Node("Station", name=station, station_list=stations[station])
        station_nodes[station] = node
        tx.create(node)


    for line in lines:
        station_list = lines[line]

        for i in range(len(station_list) - 1):
            curr_s = station_list[i]
            next_s = station_list[i + 1]

            curr_node = station_nodes[curr_s]
            next_node = station_nodes[next_s]
            
            connection = Relationship(curr_node, line, next_node)

            tx.create(connection)
    
    tx.commit()

