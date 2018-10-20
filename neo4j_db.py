from py2neo import Graph
import os

def get_shortest_path(origin, dest):
    print(os.environ['NEO4J_URL'])
    print(os.environ['NEO4J_PORT'])
    print(os.environ['NEO4J_USERNAME'])
    print(os.environ['NEO4J_TOKEN'])
    graph = Graph(host=os.environ['NEO4J_URL'], port=os.environ['NEO4J_PORT'], user=os.environ['NEO4J_USERNAME'], password=os.environ['NEO4J_TOKEN'], secure=True)
    #query = 'MATCH (ms:Station{name:\'{}\'),(cs:Station{name:\'{}\'}), p = shortestPath((ms)-[*]-(cs)) RETURN p'.format(origin, dest)

    #return graph.run(query).data()
    return 1

print(get_shortest_path('Urquinaona', 'Drassanes'))