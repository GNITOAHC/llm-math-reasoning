import math

def parse_NodeCoord_to_AdjacencyMatrix(tsp_data):
    """
    將 TSPLIB 中 EDGE_WEIGHT_TYPE 為 EUC_2D 的資料轉換為 Adjacency Matrix。
    """
    dimension = tsp_data["DIMENSION"]
    coords = tsp_data["NODE_COORD_SECTION"]  # List of tuples: (id, x, y)

    # 初始化 adjacency matrix
    matrix = [[0 for _ in range(dimension)] for _ in range(dimension)]

    for i, (xi, yi) in coords.items():
        for j, (xj, yj) in coords.items():
            if i != j:
                # 計算歐氏距離
                distance = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                matrix[i-1][j-1] = round(distance, 3)
            else:
                matrix[i-1][j-1] = 0

    return matrix

def parse_UpperRow_to_AdjacencyMatrix(tsp_data):
    edge_weights = tsp_data["EDGE_WEIGHT_SECTION"]
    n = tsp_data["DIMENSION"]
    
    matrix = [[0]*n for _ in range(0, n)]
    
    for i in range(0, n-1):
        w = len(edge_weights[i])
        for j in range(0, w):
            
            dist = edge_weights[i][j]
            matrix[i][i+j+1] = dist
            matrix[i+j+1][i] = dist
    
    return matrix

def parse_LowerDiagRow_to_AdjacencyMatrix(tsp_data):
    n = tsp_data["DIMENSION"]
    weights = []
    for w in tsp_data["EDGE_WEIGHT_SECTION"]:
        weights.extend(w)
    
    index = 1
    edges = []
    edge_weights = []
    for w in weights:
        edges.append(w)
        if len(edges) == index:
            index += 1
            edge_weights.append(edges)
            edges = []
    
    # Make all weights lists into one list
    # edge_weights = [weights[i] for i in range(0, len(weights))]
    # print(edge_weights)
    
    n = tsp_data["DIMENSION"]
    
    matrix = [[0]*n for _ in range(0, n)]
    
    for i in range(1, n):
        w = len(edge_weights[i])
        for j in range(0, w):
            dist = edge_weights[i][j]
            matrix[i][j] = dist
            matrix[j][i] = dist
    
    return matrix

def parse_UpperDiagRow_to_AdjacencyMatrix(tsp_data):
    n = tsp_data["DIMENSION"]
    weights = []
    for w in tsp_data["EDGE_WEIGHT_SECTION"]:
        weights.extend(w)
    
    index = n
    edges = []
    edge_weights = []
    for w in weights:
        edges.append(w)
        if len(edges) == index:
            index -= 1
            edge_weights.append(edges)
            edges = []
    
    n = tsp_data["DIMENSION"]
    
    matrix = [[0]*n for _ in range(0, n)]
    
    # print(edge_weights[0])
    # print(edge_weights[1])
    
    for i in range(0, n-1):
        w = len(edge_weights[i])
        for j in range(0, w):
            dist = edge_weights[i][j]
            matrix[i][i+j] = dist
            matrix[i+j][i] = dist
    
    return matrix