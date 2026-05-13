import threading
import time
from queue import Queue
from random import random

nodes = ["0", "1", "2", "3"]
graph = {
    ("0", "1"): 1,
    ("0", "2"): 3,
    ("0", "3"): 7,
    ("1", "2"): 1,
    ("2", "3"): 2
}
inf = float("inf")

def adjacent(graph, node):
    ans = {}
    for (u, v), w in graph.items():
        if u == node:
            ans[v] = w
        if v == node:
            ans[u] = w
    return ans

def key(u, v) -> tuple[str, str]:
    return tuple(sorted([u, v]))

msg_queues = {node: Queue() for node in nodes}

def node_thread(node):
    global graph, msg_queues
    msg_queue = msg_queues[node]
    cached_adjacent = {}
    distance_vector = {(n, n): 0 for n in nodes}
    while True:
        updated = False

        # checking updates from adjacent nodes
        adj_nodes = adjacent(graph, node)
        if cached_adjacent != adj_nodes:
            cached_adjacent = adj_nodes
            for adj_node, w in adj_nodes.items():
                print(f"node {node}: updating {key(node, adj_node)} = {w} from direct connection\n", end='')
                distance_vector[key(node, adj_node)] = w
                updated = True
            for m_node in nodes:
                if m_node == node:
                    continue
                new_w = min([
                    cached_adjacent[adj_node] + distance_vector.get(key(adj_node, m_node), inf)
                    for adj_node in cached_adjacent
                ])
                if distance_vector.get(key(node, m_node), inf) != new_w:
                    print(f"node {node}: updating {key(node, m_node)} = {new_w} from an indirect connection\n", end='')
                    distance_vector[key(node, m_node)] = new_w
                    updated = True

        # checking updates from other nodes
        while msg_queue.qsize() > 0:
            src_node, data = msg_queue.get()
            print(f"node {node}: received distance vector from node {src_node}\n", end='')
            for adj_node, w in data.items():
                if adj_node != node and distance_vector.get(key(src_node, adj_node), inf) != w:
                    distance_vector[key(src_node, adj_node)] = w

            if key(node, src_node) not in distance_vector:
                continue
            for m_node in nodes:
                if m_node == node:
                    continue
                new_w = min([
                    cached_adjacent[adj_node] + distance_vector.get(key(adj_node, m_node), inf)
                    for adj_node in cached_adjacent
                ])
                if distance_vector.get(key(node, m_node), inf) != new_w:
                    print(f"node {node}: updating {key(node, m_node)} = {new_w} from an indirect connection\n", end='')
                    distance_vector[key(node, m_node)] = new_w
                    updated = True

        # send updates
        if updated:
            data = adjacent(distance_vector, node)
            print(f"node {node}: sending out distance vector {data}\n", end='')
            for adj_node in cached_adjacent:
                msg_queues[adj_node].put((node, data))
            time.sleep(random())


node_threads = [
    threading.Thread(target=node_thread, args=(node,), daemon=True) for node in nodes
]
for thread in node_threads:
    thread.start()
while True:
    u, v, w = input().split()
    print(f"setting connection {u} - {v} to weight {w}")
    graph[key(u, v)] = int(w)