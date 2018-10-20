from py2neo import Graph
import os

def get_shortest_path(origin, dest):
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    query = 'MATCH (ms:Station{{name:\'{}\'}}),(cs:Station{{name:\'{}\'}}), path = shortestPath((ms)-[*]-(cs)) RETURN path'.format(origin, dest)

    return graph.run(query).data()[0]['path']

def get_error_list(path):
    error_list = []
    for edge in path:
        if edge['error']:
            info = {
                'message': edge['error'],
                'origin': edge.start_node['name'],
                'destination': edge.end_node['name']
            }
            error_list.append(info)
    
    return error_list