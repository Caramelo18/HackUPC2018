from py2neo import Graph, NodeMatcher, RelationshipMatcher
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

def insert_error(origin, destination, message):
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    query = 'MATCH (ms:Station{{name:\'{}\'}}),(cs:Station{{name:\'{}\'}}), (ms)-[e]-(cs) SET e.error=\'{}\''.format(origin, destination, message)
    graph.run(query)

def is_station(name):
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    matcher = NodeMatcher(graph)

    return len(matcher.match('Station', name=name)) > 0

def is_contained(origin, destination, problem_origin, problem_destination):
    path = get_shortest_path(origin, destination)
    stations = [node['name'] for node in path.nodes]
    return problem_origin in stations and problem_destination in stations
