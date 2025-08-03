# parse the ./dataset_tsp/all_tsp/a280.opt.tour file
import tsplib95
import json

from src.tsp_format import (
    format_Tsp_type,
    format_Node_coord_type,
    format_Edge_weight_format,
    format_Edge_weight_type,
    format_Display_data_type
)

from src.cood_format import (
    parse_NodeCoord_to_AdjacencyMatrix,
    parse_UpperRow_to_AdjacencyMatrix,
    parse_LowerDiagRow_to_AdjacencyMatrix,
    parse_UpperDiagRow_to_AdjacencyMatrix
)

def get_all_tsp_files():
    import os
    path = "dataset_tsp/all_tsp"
    files = []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".tsp"):
                files.append(root + "/" + filename)
    return files

ALL_TSP_FILES = get_all_tsp_files()

from pprint import pprint
        
def main():
    # mkdir of dataset_tsp/parsed_output/small/
    import os
    if not os.path.exists("dataset_tsp/parsed_output/small/"):
        os.makedirs("dataset_tsp/parsed_output/small/")
    if not os.path.exists("dataset_tsp/parsed_output/medium/"):
        os.makedirs("dataset_tsp/parsed_output/medium/")
    if not os.path.exists("dataset_tsp/parsed_output/large/"):
        os.makedirs("dataset_tsp/parsed_output/large/")
    if not os.path.exists("dataset_tsp/parsed_output/very_large/"):
        os.makedirs("dataset_tsp/parsed_output/very_large/")
    
    # Load the TSP instance from the file
    for i, tsp_file in enumerate(ALL_TSP_FILES):
        tsp = tsplib95.load(tsp_file)
        
        if "ignore" in tsp_file:
            continue
        
        tsp_data = tsp.as_keyword_dict()
        tsp_data["id"] = i
        
        output_dir = "dataset_tsp/parsed_output/small/"
        if tsp.dimension > 100:
            output_dir = "dataset_tsp/parsed_output/medium/"
        if tsp.dimension > 1000:
            output_dir = "dataset_tsp/parsed_output/large/"
        if tsp.dimension > 5000:
            output_dir = "dataset_tsp/parsed_output/very_large/"
        print(tsp_file)
        
        # Save to a file or print
        with open( output_dir + f"q{i}_{tsp_data['NAME']}.txt", "w") as f:
            f.write("[METADATA]\n")
            f.write("Name: " + tsp.name + "\n")
            f.write("Dimension: " + str(tsp.dimension) + "\n")
            
            f.write("\n[TSP_DATA_INFO]\n")
            f.write(f"Type: {tsp.type}, {format_Tsp_type(tsp_type=tsp.type)} \n")
            f.write(f"Node coordinate type: {tsp.node_coord_type}, {format_Node_coord_type(tsp_type=tsp.node_coord_type)} \n")
            f.write(f"Edge weight type: {tsp.edge_weight_type}, {format_Edge_weight_type(tsp_type=tsp.edge_weight_type)} \n")
            f.write(f"Edge weight format: {tsp.edge_weight_format}, {format_Edge_weight_format(tsp_type=tsp.edge_weight_format)} \n")
            f.write(f"Display data type: {tsp.display_data_type}, {format_Display_data_type(tsp_type=tsp.display_data_type)} \n")
            
            if tsp.dimension > 5000:
                print(f"Very large TSP, write only node coordinates: {tsp_file}")
                f.write("\n[NODE_COORDINATES]\n")
                for i, coord in tsp.node_coords.items():
                    f.write(f"{i+1}: {tuple(coord)}\n")
                continue
            
            # Function to format TSP data for LLM readability
            if tsp.edge_weight_type in [
                "EUC_2D", "GEO", "ATT", "CEIL_2D"
            ]:
                print("NodeCoord to Adjacency Matrix: ", tsp.edge_weight_type)
                adjacency_matrix = parse_NodeCoord_to_AdjacencyMatrix(tsp_data)
                f.write("\n[ADJACENCY_MATRIX]\n")
                for i, row in enumerate(adjacency_matrix):
                    f.write(f"{i+1}: [" + ", ".join(map(str, row)) + "]\n")
            
            if tsp.edge_weight_format == "UPPER_ROW":
                print("UpperRow to Adjacency Matrix: ", tsp.edge_weight_format)
                adjacency_matrix = parse_UpperRow_to_AdjacencyMatrix(tsp_data)
                f.write("\n[ADJACENCY_MATRIX]\n")
                for i, row in enumerate(adjacency_matrix):
                    f.write(f"{i+1}: [" + ", ".join(map(str, row)) + "]\n")
            
            if tsp.edge_weight_format == "FULL_MATRIX":
                print("FullMatrix to Adjacency Matrix: ", tsp.edge_weight_format)
                f.write("\n[ADJACENCY_MATRIX]\n")
                for i in range(tsp.dimension):
                    row = tsp.edge_weights[i]
                    f.write(f"{i+1}: [" + ", ".join(map(str, row)) + "]\n")
            
            if tsp.edge_weight_format == "LOWER_DIAG_ROW":
                print("LowerDiagRow to Adjacency Matrix: ", tsp.edge_weight_format)
                adjacency_matrix = parse_LowerDiagRow_to_AdjacencyMatrix(tsp_data)
                f.write("\n[ADJACENCY_MATRIX]\n")
                for i, row in enumerate(adjacency_matrix):
                    f.write(f"{i+1}: [" + ", ".join(map(str, row)) + "]\n")
            
            if tsp.edge_weight_format == "UPPER_DIAG_ROW":
                print("UpperDiagRow to Adjacency Matrix: ", tsp.edge_weight_format)
                adjacency_matrix = parse_UpperDiagRow_to_AdjacencyMatrix(tsp_data)
                f.write("\n[ADJACENCY_MATRIX]\n")
                for i, row in enumerate(adjacency_matrix):
                    f.write(f"{i+1}: [" + ", ".join(map(str, row)) + "]\n")
            
            print()
        # break
    
if __name__ == "__main__":
    main()