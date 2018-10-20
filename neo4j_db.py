from py2neo import Graph, NodeMatcher, RelationshipMatcher, Schema
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

def list_lines():
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    return list(Schema(graph).relationship_types)

def list_stations_by_line(line):
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    query = 'MATCH(s:Station)-[:{}]->() RETURN s'.format(line)
    station_list = [result['s']['name'] for result in graph.run(query).data()]
    return station_list

def list_stations():
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    query = 'MATCH(s) RETURN s'
    station_list = [result['s']['name'] for result in graph.run(query).data()]
    return station_list

def list_issues():
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    query = 'MATCH (ms:Station), (cs:Station), (ms)-[e]->(cs) WHERE EXISTS(e.error) RETURN ms, e, cs'
    error_list = []
    for error in graph.run(query).data():
        info = {
            'message': error['e']['error'],
            'origin': error['ms']['name'],
            'destination': error['cs']['name']
        }
        error_list.append(info)

    return error_list