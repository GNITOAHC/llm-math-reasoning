import os
import shutil

# check how many file without extension are the same name in the directory vrp_instances and vrp_solutions
instance_list = [file.split('.')[0].lower() for file in os.listdir('./vrp_instances') if file.endswith('.dat')]
solution_list = [file.split('.')[0].lower() for file in os.listdir('./vrp_solutions') if file.endswith('.HRE')]

common_files = set(instance_list) & set(solution_list)
# print(f'Number of files without extension that are the same name in vrp_instances and vrp_solutions: {len(common_files)}')
# print(common_files)

os.makedirs('./common_vrp', exist_ok=True)

# copy common files to common_vrp directory
for file in os.listdir('./vrp_instances'):
    if file.split('.')[0].lower() in common_files:
        new_file = file.lower().split('.')[0] + "_desc.txt"
        shutil.copy(f'./vrp_instances/{file}', f'./common_vrp/{new_file}')

for file in os.listdir('./vrp_solutions'):
    if file.split('.')[0].lower() in common_files:
        new_file = file.lower().split('.')[0] + "_ans.txt"
        shutil.copy(f'./vrp_solutions/{file}', f'./common_vrp/{new_file}')

# Create a dictionary to map common file names to their full paths
common_dict = {file: {'instance': '', 'solution': ''} for file in common_files}

# copy the common files to common_dict dictionary
for file in os.listdir('./vrp_instances'):
    if file.split('.')[0].lower() in common_files:
        common_dict[file.split('.')[0].lower()]['instance'] = f'./vrp_instances/{file}'

for file in os.listdir('./vrp_solutions'):
    if file.split('.')[0].lower() in common_files:
        common_dict[file.split('.')[0].lower()]['solution'] = f'./vrp_solutions/{file}'

# from pprint import pprint
# pprint(common_dict)

def parse_vrp_to_custom_format(file_content: str) -> str:
    lines = file_content.strip().splitlines()
    metadata = {}
    coords = {}
    demands = {}
    depot_id = None

    section = None
    for line in lines:
        line = line.strip()
        if not line or line == "EOF":
            continue

        if ":" in line and not line.startswith("NODE_COORD_SECTION"):
            key, value = map(str.strip, line.split(":", 1))
            metadata[key] = value
        elif line == "NODE_COORD_SECTION":
            section = "coord"
        elif line == "DEMAND_SECTION":
            section = "demand"
        elif line == "DEPOT_SECTION":
            section = "depot"
        elif section == "coord":
            parts = line.split()
            node_id = int(parts[0])
            x, y = float(parts[1]), float(parts[2])
            coords[node_id] = (x, y)
        elif section == "demand":
            parts = line.split()
            node_id = int(parts[0])
            demand = int(parts[1])
            demands[node_id] = demand
        elif section == "depot":
            depot_id = int(line)

    # Build the formatted output
    output = []

    # METADATA
    output.append("[METADATA]")
    output.append(f"File: {metadata['NAME']}")
    output.append(f"COMMENT: {metadata.get('COMMENT', '')}")
    output.append("")

    # VRP_DATA_INFO
    output.append("[VRP_DATA_INFO]")
    output.append(f"Type: {metadata.get('TYPE', 'CVRP')} (Capacitated Vehicle Routing Problem)")
    output.append(f"Dimension: {metadata.get('DIMENSION', '')}")
    output.append(f"Distance Metric: {'Euclidean (2D)' if metadata.get('EDGE_WEIGHT_TYPE') == 'EUC_2D' else metadata.get('EDGE_WEIGHT_TYPE', '')}")
    output.append(f"Vehicle Capacity: {metadata.get('CAPACITY', '')}")
    output.append(f"Number of Vehicles: {metadata.get('VEHICLES', '')}")
    output.append("")

    # Depot
    output.append("[Depot]")
    depot_coord = coords[depot_id]
    depot_demand = demands[depot_id]
    output.append(f"Node {depot_id}: Coordinates: ({int(depot_coord[0])}, {int(depot_coord[1])}), Demand: {depot_demand}")
    output.append("")

    # Customer Nodes
    output.append("[Customer Nodes]")
    output.append("# Format: Node ID: Coordinates (x, y), Demand")
    for node_id in sorted(coords):
        if node_id == depot_id:
            continue
        x, y = coords[node_id]
        demand = demands.get(node_id, 0)
        output.append(f"{node_id}: ({int(x)}, {int(y)}), Demand: {demand}")

    return "\n".join(output)

def parse_vrp_solution_to_custom_format(file_content: str) -> str:
    lines = file_content.strip().splitlines()
    metadata = {}
    routes = []
    depot = None

    in_solution_section = False

    for line in lines:
        line = line.strip()
        if not line or line == "END":
            continue

        # Parse metadata
        if ':' in line and not line.startswith("SOLUTION_SECTION"):
            key, value = map(str.strip, line.split(":", 1))
            metadata[key] = value

        elif line.startswith("SOLUTION_SECTION"):
            in_solution_section = True
            continue

        elif line.startswith("DEPOT_SECTION"):
            in_solution_section = False
            continue

        elif not in_solution_section and line.isdigit():
            depot = int(line)

        elif in_solution_section and line[0].isdigit():
            parts = line.split()
            route_id = int(parts[0])
            total_demand = int(parts[1])
            cost = float(parts[2])
            # parts[3] = length (same as cost), parts[4] = number of customers
            customers = list(map(int, parts[5:]))
            routes.append({
                "route_id": route_id,
                "total_demand": total_demand,
                "cost": cost,
                "customers": customers
            })

    # Build formatted output
    output = []

    output.append("[METADATA]")
    output.append(f"File: {metadata.get('NAME', '')}")
    output.append("Type: HREAL (Heterogeneous Real-world VRP)")
    output.append(f"Number of Routes: {metadata.get('ROUTES', len(routes))}")
    output.append(f"Total Cost: {metadata.get('COST', '')}")
    output.append(f"Depot: Node {depot}")
    output.append("")

    output.append("[ROUTES]")
    for route in routes:
        output.append(f"Route {route['route_id']}:")
        output.append(f"Total Demand: {route['total_demand']}")
        output.append(f"Cost: {route['cost']}")
        output.append(f"Customers: {route['customers']}")
        output.append("")

    return "\n".join(output)


os.makedirs('./parsed_output/', exist_ok=True)

for file in common_files:
    instance_path = common_dict[file]['instance']
    solution_path = common_dict[file]['solution']

    with open(instance_path, 'r') as f:
        instance_content = f.read()

    with open(solution_path, 'r') as f:
        solution_content = f.read()

    parsed_instance = parse_vrp_to_custom_format(instance_content)
    parsed_solution = parse_vrp_solution_to_custom_format(solution_content)

    with open(f'./parsed_output/{file}_desc.txt', 'w') as f:
        f.write(parsed_instance)

    with open(f'./parsed_output/{file}_ans.txt', 'w') as f:
        f.write(parsed_solution)