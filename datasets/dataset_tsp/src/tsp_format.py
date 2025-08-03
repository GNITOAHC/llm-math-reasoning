def format_Tsp_type(tsp_type):
    # TSP Problem Types
    if tsp_type == None:
        return ""
    if tsp_type == 'TSP':
        return 'Traveling salesman problem (TSP)'
    if tsp_type == 'TSP (M.~Hofmeister)':
        return 'Traveling salesman problem (TSP) instance by M. Hofmeister'
    
    raise ValueError(f"Unknown, Tsp_type: {tsp_type}")
    return tsp_type

def format_Node_coord_type(tsp_type):
    # Node coordinate types
    if tsp_type == None:
        return ""
    if tsp_type == 'NO_COORDS':
        return 'No Coordinates: The nodes are not assigned geometric positions.'

def format_Edge_weight_format(tsp_type):
    # Edge-weighted format
    if tsp_type == None:
        return ""
    if tsp_type == 'FULL_MATRIX':
        return 'Full symmetric matrix of distances is given.'
    if tsp_type == 'FUNCTION':
        return 'Distances are computed by a known function.'
    if tsp_type == 'LOWER_DIAG_ROW':
        return 'Lower triangular matrix with diagonal row of distances is given.'
    if tsp_type == 'UPPER_DIAG_ROW':
        return 'Upper triangular matrix with diagonal row of distances is given.'
    if tsp_type == 'UPPER_ROW':
        return 'Upper triangular matrix without diagonal row of distances is given.'
    
    raise ValueError(f"Unknown, Edge_weight_format: {tsp_type}")
    return tsp_type

def format_Edge_weight_type(tsp_type):
    # Edge-weighted types
    if tsp_type == None:
        return ""
    if tsp_type == 'EUC_2D':
        return 'Euclidean distance in 2D'
    if tsp_type == 'GEO':
        return 'Geographical distance based on latitude and longitude'
    if tsp_type == 'ATT':
        return 'Pseudo-Euclidean distance used in some ATT instances'
    if tsp_type == 'EXPLICIT':
        return 'Distances are explicitly given in a matrix'
    if tsp_type == 'CEIL_2D':
        return 'Ceiling of Euclidean distance in 2D'
    
    raise ValueError(f"Unknown, Edge_weight_format: {tsp_type}")
    return tsp_type

def format_Display_data_type(tsp_type):
    # Display datatypes
    if tsp_type == None:
        return ""
    if tsp_type == 'NO_DISPLAY':
        return 'No display data is given'
    if tsp_type == 'TWOD_DISPLAY':
        return 'Display data includes 2D coordinates positions'
    if tsp_type == 'COORD_DISPLAY':
        return 'Display uses the same coordinates as the node coordinates (NODE_COORD_TYPE)'
    
    raise ValueError(f"Unknown, Display_data_type: {tsp_type}")
    return tsp_type
