import heapq
from itertools import permutations
from queue import PriorityQueue


class Agent():
    def __init__(self, coin_distance):
        self.coin_distance = coin_distance
    
    def getPath(self, coin_distance):
        pass


class Aki(Agent):
    def __init__(self, coin_distance):
        super().__init__(coin_distance)
    
    def getPath(self, coin_distance):
        path = greedy_dfs(coin_distance)

        return path
    

class Jocke(Agent):
    def __init__(self, coin_distance):
        super().__init__(coin_distance)
    
    def getPath(self, coin_distance):
        path = brute_force(coin_distance)

        return path
    
class Uki(Agent):
    def __init__(self, coin_distance):
        super().__init__(coin_distance)
    
    def getPath(self, coin_distance):
        path = branch_and_bound(coin_distance)

        return path
    
class Micko(Agent):
    def __init__(self, coin_distance):
        super().__init__(coin_distance)
    
    def getPath(self, coin_distance):
        path = a_star(coin_distance)

        return path
    
#Aki - dfs
def dfs(coin_distance, node, visited, path):
    path.append(node)
    visited[node] = True

    if all(visited):
        path.append(path[0])
        return path

    min_distance = float('inf')
    next_node = -1
    for i in range(len(coin_distance)):
        if not visited[i] and coin_distance[node][i] != 0 and coin_distance[node][i] < min_distance:
            min_distance = coin_distance[node][i]
            next_node = i

    if next_node != -1:
        new_path = dfs(coin_distance, next_node, visited, path)
        if all(visited):
            return new_path

    return path

def greedy_dfs(coin_distance):
    start = 0
    visited = [False] * len(coin_distance)
    path = dfs(coin_distance, start, visited, [])
    return path


#Jocke - brute force
def brute_force(coin_distance):
        paths = []
        min_path_cost = float('inf')
        min_path = []
        perm_set = [i for i in range(1, len(coin_distance))]
        perm_arr = permutations(perm_set)
        # Add zeros to the start and end of the path and then calcuate the path
        for permutation in perm_arr:
            paths.append([0] + list(permutation) + [0])
        for path in paths:
            currSum = 0
            for i in range(len(path) - 1):
                currSum += coin_distance[path[i]][path[i + 1]]
            if currSum < min_path_cost:
                min_path_cost = currSum
                min_path = path
        return min_path

#Uki - branch and bound
def calculate_lower_bound(coin_distance, path):
    lb = sum(coin_distance[path[i]][path[i + 1]] for i in range(len(path) - 1))
    outgoing_links = [coin_distance[path[-1]][i] for i in range(len(coin_distance)) if i not in path]
    if outgoing_links:
        lb += min(outgoing_links)
    return lb

def branch_and_bound(coin_distance):
    num_nodes = len(coin_distance)
    best_cost = float('inf')
    best_path = None

    pq = PriorityQueue()
    pq.put((0, [0]))

    while not pq.empty():
        curr_cost, curr_path = pq.get()

        if len(curr_path) == num_nodes:
            curr_cost += coin_distance[curr_path[-1]][0]
            if curr_cost < best_cost:
                best_cost = curr_cost
                best_path = curr_path + [0]

        else:
            for i in range(num_nodes):
                if i not in curr_path:
                    new_path = curr_path + [i]
                    new_cost = curr_cost + coin_distance[curr_path[-1]][i]
                    lb = calculate_lower_bound(coin_distance, new_path)
                    if lb < best_cost:
                        pq.put((lb, new_path))

    return best_path

#TODO Micko a star
def a_star(coin_distance):
    n = len(coin_distance)  # Broj čvorova
    first_node = (0, n, 0, [0], 0)  # Početni čvor
    list_of_nodes = [first_node]
    heapq.heapify(list_of_nodes)

    while list_of_nodes:
        current = heapq.heappop(list_of_nodes)

        if len(current[3]) == (n + 1):  # Našli smo putanju sa ciljnim čvorom
            return current[3]

        if len(current[3]) == n:  # Ako je putanja posetila sve čvorove osim ciljnog, treba se vratiti
            remaining = [0]
        else:
            remaining = [i for i in range(1, n) if i not in current[3]]

        expand_and_calculate(remaining, list_of_nodes, current, coin_distance, n)

def expand_and_calculate(remaining, list_of_nodes, current, coin_distance, n):
    scaled_matrix = scale_matrix(current, n, coin_distance)
    
    if not scaled_matrix:
        heuristic = 0
    else:
        heuristic = prims_algorithm(scaled_matrix)

    for i in remaining:
        heapq.heappush(list_of_nodes, (current[4] + coin_distance[current[2]][i] + heuristic, (current[1] - 1), i, current[3] + [i], current[4] + coin_distance[current[2]][i]))

def scale_matrix(current, n, coin_distance):
    selected = [i for i in range(1, n) if i not in current[3]]
    
    if not selected:
        return []

    selected.append(0)
    selected.sort()

    new_list = [[coin_distance[i][j] for j in selected] for i in selected]
    
    return new_list

def prims_algorithm(scaled_matrix):
    inf = float('inf')
    n = len(scaled_matrix)
    selected_node = [0] * n
    no_edge = 0
    selected_node[0] = True
    sum_all = 0

    while no_edge < n - 1:
        minimum = inf
        a = 0
        b = 0

        for m in range(n):
            if selected_node[m]:
                for i in range(n):
                    if (not selected_node[i]) and scaled_matrix[m][i]:
                        if minimum > scaled_matrix[m][i]:
                            minimum = scaled_matrix[m][i]
                            a = m
                            b = i

        sum_all += scaled_matrix[a][b]
        selected_node[b] = True
        no_edge += 1

    return sum_all