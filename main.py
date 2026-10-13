import heapq


edges = [
    (0, 1, 4),
    (0, 2, 8),
    (1, 2, 1),
    (2, 0, 3),
    (2, 3, 2),
    (3, 4, 2),
    (4, 5, 3),
    (5, 3, 1),
    (5, 6, 4),
    (6, 7, 2),
]


def build_graphs(vertex_count, edge_list):
    directed = {v: [] for v in range(vertex_count)}

    undirected_neighbors = {v: set() for v in range(vertex_count)}

    for u, v, weight in edge_list:
        directed[u].append((v, weight))
        undirected_neighbors[u].add(v)
        undirected_neighbors[v].add(u)


    undirected = {
        v: sorted(neighbors)
        for v, neighbors in undirected_neighbors.items()
    }
    return directed, undirected


def dfs(graph, vertex, visited, order):
    visited.add(vertex)
    order.append(vertex)

    for neighbor in graph[vertex]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited, order)


def connected_components(graph):
    visited = set()
    components = []

    for vertex in graph:
        if vertex not in visited:
            component = []
            dfs(graph, vertex, visited, component)
            components.append(component)

    return components


def print_graph(title, graph):
    print(title)
    for vertex, neighbors in graph.items():
        print(f"  {vertex}: {neighbors}")


def task_1():
    print("\nЗадание 1. Представление графа и базовый обход:")
    directed, undirected = build_graphs(8, edges)
    print_graph("Ориентированный граф G (сосед, вес):", directed)
    print_graph("\nНеориентированная проекция Gu:", undirected)

    order = []
    dfs(undirected, 0, set(), order)
    print("\nПорядок DFS из вершины 0:", order)

    components = connected_components(undirected)
    print("\nКомпоненты исходного Gu:", components)
    print("Количество компонент:", len(components))


    modified = {v: neighbors.copy() for v, neighbors in undirected.items()}

    modified[5].remove(6)
    modified[6].remove(5)

    modified_components = connected_components(modified)
    print("\nПосле удаления ребра {5, 6}:", modified_components)
    print("Количество компонент:", len(modified_components))
    print(f"Число компонент изменилось: {len(components)} - {len(modified_components)}")


def kosaraju(graph):
    visited = set()
    finish_order = []

    def dfs_finish(vertex):
        visited.add(vertex)
        for neighbor, _weight in graph[vertex]:
            if neighbor not in visited:
                dfs_finish(neighbor)

        finish_order.append(vertex)


    for vertex in graph:
        if vertex not in visited:
            dfs_finish(vertex)


    transposed = {vertex: [] for vertex in graph}
    for vertex, neighbors in graph.items():
        for neighbor, _weight in neighbors:
            transposed[neighbor].append(vertex)

    visited = set()
    components = []
    for vertex in reversed(finish_order):
        if vertex not in visited:
            component = []
            dfs(transposed, vertex, visited, component)
            components.append(component)

    return components


def task_2():
    directed, _undirected = build_graphs(8, edges)
    components = kosaraju(directed)
    print("\nЗадание 2. Компоненты сильной связности:")
    for number, component in enumerate(components, start=1):
        print(f"Компонента {number}: {sorted(component)}")
    print("Количество компонент:", len(components))
    return components


def find_bridges_and_articulation_points(graph):
    tin = {vertex: -1 for vertex in graph}
    low = {vertex: -1 for vertex in graph}
    bridges = []
    articulation_points = set()
    timer = 0

    def dfs_low(vertex, parent=None):
        nonlocal timer
        tin[vertex] = low[vertex] = timer
        timer += 1
        children = 0

        for neighbor in graph[vertex]:

            if neighbor == parent:
                continue
            if tin[neighbor] != -1:

                low[vertex] = min(low[vertex], tin[neighbor])
            else:
                dfs_low(neighbor, vertex)
                children += 1

                low[vertex] = min(low[vertex], low[neighbor])

                if low[neighbor] > tin[vertex]:
                    bridges.append(tuple(sorted((vertex, neighbor))))
                if parent is not None and low[neighbor] >= tin[vertex]:
                    articulation_points.add(vertex)


        if parent is None and children > 1:
            articulation_points.add(vertex)

    for vertex in graph:
        if tin[vertex] == -1:
            dfs_low(vertex)

    return sorted(bridges), sorted(articulation_points), tin, low


def task_3():
    _directed, undirected = build_graphs(8, edges)
    bridges, points, tin, low = find_bridges_and_articulation_points(undirected)
    print("\nЗадание 3. Мосты и точки сочленения:")
    print("Мосты:", bridges)
    print("Точки сочленения:", points)
    print("\nВершина | tin | low")
    for vertex in undirected:
        print(f"{vertex:7} | {tin[vertex]:3} | {low[vertex]:3}")


    u, v = bridges[0]
    modified = {vertex: neighbors.copy() for vertex, neighbors in undirected.items()}
    modified[u].remove(v)
    modified[v].remove(u)
    before = connected_components(undirected)
    after = connected_components(modified)
    print(f"\nУдалён мост {{{u}, {v}}}.")
    print("Компоненты после удаления:", after)
    print(f"Число компонент изменилось: {len(before)} → {len(after)}")


def build_condensation(graph, components):
    component_of = {}
    for number, component in enumerate(components, start=1):
        for vertex in component:
            component_of[vertex] = number

    neighbors = {number: set() for number in range(1, len(components) + 1)}
    for vertex, outgoing in graph.items():
        for neighbor, _weight in outgoing:
            source = component_of[vertex]
            target = component_of[neighbor]

            if source != target:
                neighbors[source].add(target)

    condensation = {number: sorted(targets) for number, targets in neighbors.items()}
    return condensation, component_of


def topological_sort(graph):

    state = {vertex: 0 for vertex in graph}
    finish_order = []

    def dfs_topological(vertex):
        state[vertex] = 1
        for neighbor in graph[vertex]:
            if state[neighbor] == 1:
                return False
            if state[neighbor] == 0:
                if not dfs_topological(neighbor):
                    return False
        state[vertex] = 2
        finish_order.append(vertex)
        return True

    for vertex in graph:
        if state[vertex] == 0:
            if not dfs_topological(vertex):
                return None

    return list(reversed(finish_order))


def task_4(components):
    directed, _undirected = build_graphs(8, edges)
    condensation, component_of = build_condensation(directed, components)
    print("\nЗадание 4. Граф конденсации, топологическая сортировка и цикл:")
    for number, component in enumerate(components, start=1):
        print(f"Компонента {number}: {sorted(component)}")
    print_graph("Список смежности конденсации:", condensation)
    order = topological_sort(condensation)
    print("Топологический порядок компонент:", order)

    modified = {number: neighbors.copy() for number, neighbors in condensation.items()}
    source = component_of[7]
    target = component_of[3]
    modified[source].append(target)
    print(f"\nВ копию добавлено ребро: компонента {source} - компонента {target}")
    print_graph("Изменённый граф конденсации:", modified)
    if topological_sort(modified) is None:
        print("Обнаружен цикл. Топологическая сортировка невозможна.")


def dijkstra(graph, start):
    distance = {vertex: float("inf") for vertex in graph}
    parent = {vertex: None for vertex in graph}
    distance[start] = 0
    heap = [(0, start)]

    while heap:
        current_distance, vertex = heapq.heappop(heap)

        if current_distance != distance[vertex]:
            continue

        for neighbor, weight in graph[vertex]:
            new_distance = current_distance + weight

            if new_distance < distance[neighbor]:
                distance[neighbor] = new_distance
                parent[neighbor] = vertex
                heapq.heappush(heap, (new_distance, neighbor))

    return distance, parent


def restore_path(parent, start, target):
    path = []
    vertex = target
    while vertex != start:
        path.append(vertex)
        vertex = parent[vertex]
    path.append(start)
    return list(reversed(path))


def task_5():
    directed, _undirected = build_graphs(8, edges)
    distance, parent = dijkstra(directed, 0)
    print("\nЗадание 5. Алгоритм Дейкстры из вершины 0:")
    print("Вершина | Расстояние | Предшественник")
    for vertex in directed:
        print(f"{vertex:7} | {distance[vertex]:10} | {parent[vertex]}")
    print("Расстояния:", [distance[vertex] for vertex in directed])
    path = restore_path(parent, 0, 7)
    print("Кратчайший маршрут из 0 в 7:", " - ".join(map(str, path)))
    print("Длина маршрута:", distance[7])
    return distance, parent


def bellman_ford(vertex_count, edge_list, start):
    distance = [float("inf")] * vertex_count
    distance[start] = 0


    for _ in range(vertex_count - 1):
        changed = False
        for u, v, weight in edge_list:
            if distance[u] != float("inf") and distance[u] + weight < distance[v]:
                distance[v] = distance[u] + weight
                changed = True

        if not changed:
            break


    has_negative_cycle = any(
        distance[u] != float("inf") and distance[u] + weight < distance[v]
        for u, v, weight in edge_list
    )
    return distance, has_negative_cycle


def task_6():
    print("\nЗадание 6. Алгоритм Беллмана–Форда из вершины 0:")

    negative_edge = [
        (u, v, -2 if (u, v) == (2, 3) else weight)
        for u, v, weight in edges
    ]
    distance, has_cycle = bellman_ford(8, negative_edge, 0)
    print("Вес ребра 2 - 3 изменён на −2.")
    if has_cycle:
        print("Обнаружен отрицательный цикл, достижимый из старта.")
    else:
        print("Достижимых отрицательных циклов нет.")
        print("Расстояния:", distance)

    negative_cycle = [
        (u, v, -4 if (u, v) == (4, 5) else weight)
        for u, v, weight in negative_edge
    ]
    _distance, has_cycle = bellman_ford(8, negative_cycle, 0)
    print("\nДополнительно вес ребра 4 - 5 изменён на −4.")
    if has_cycle:
        print("Обнаружен отрицательный цикл, достижимый из старта.")


def floyd_warshall(vertex_count, edge_list):
    distance = [[float("inf")] * vertex_count for _ in range(vertex_count)]
    for vertex in range(vertex_count):
        distance[vertex][vertex] = 0
    for u, v, weight in edge_list:
        distance[u][v] = weight


    for k in range(vertex_count):
        for i in range(vertex_count):
            for j in range(vertex_count):
                distance[i][j] = min(
                    distance[i][j], distance[i][k] + distance[k][j]
                )
    return distance


def task_7():

    matrix = floyd_warshall(8, edges)
    print("\nЗадание 7. Алгоритм Флойда–Уоршелла:")
    print("Матрица кратчайших расстояний:")
    print("Из/В " + " ".join(f"{vertex:>4}" for vertex in range(8)))
    for vertex, row in enumerate(matrix):
        values = ["inf" if value == float("inf") else str(value) for value in row]
        print(f"{vertex:>4} " + " ".join(f"{value:>4}" for value in values))

    directed, _undirected = build_graphs(8, edges)
    distance, _parent = dijkstra(directed, 0)
    dijkstra_row = [distance[vertex] for vertex in range(8)]
    print("\nСтрока 0 Флойда–Уоршелла:", matrix[0])
    print("Расстояния Дейкстры:     ", dijkstra_row)
    print("Результаты совпадают:", matrix[0] == dijkstra_row)

    return matrix


if __name__ == "__main__":
    task_1()
    components = task_2()
    task_3()
    task_4(components)
    task_5()
    task_6()
    task_7()
