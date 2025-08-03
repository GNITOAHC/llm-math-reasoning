import re
from collections import defaultdict
import os

"""
Graph Coloring Problem (GCP) Parser
Input format:
c FILE: <filename>
c DESCRIPTION: <description>
p edge <node_count> <edge_count>
e <n1> <n2> [d]
e <n1> <n2> [d]

Output format:
[METADATA]
File: DSJC125.5
Description: Random graph used in the paper "Optimization by Simulated Annealing: An Experimental Evaluation..."

[GCP_DATA_INFO]
Type: GCP, Graph Coloring Problem 
Node: 125
Edge: 3891

[ADJACENCY_List]
2: [1]
3: [1]
4: [1, 2, 3]
...
"""

def parse_gcp_file(filepath):
    metadata = {}
    description_lines = []
    node_count = edge_count = None
    adj_list = defaultdict(list)

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith("c FILE:") or line.startswith("c File:"):
                metadata["File"] = line.split(":", 1)[1].strip()

            elif line.startswith("c DESCRIPTION:") or line.startswith("c Description:"):
                description_lines.append(line[1:].strip())
            elif line.startswith("c"):
                # Additional description lines
                description_lines.append(line[1:].strip())

            elif line.startswith("p edge"):
                match = re.match(r"p edge (\d+) (\d+)", line)
                if match:
                    node_count, edge_count = int(match.group(1)), int(match.group(2))

            elif line.startswith("e"):
                # e n1 n2 [d]
                parts = line.split()
                if len(parts) >= 3:
                    n1, n2 = int(parts[1]), int(parts[2])
                    # Add only the lower-numbered neighbor to higher one
                    if n2 < n1:
                        adj_list[n1].append(n2)
                    elif n1 < n2:
                        adj_list[n2].append(n1)

    # Start output
    output = []

    # [METADATA]
    output.append("[METADATA]")
    output.append(f"File: {metadata.get('File', 'Unknown')}")
    description = " ".join(description_lines).strip()
    output.append(f"Description: {description}")
    output.append("")

    # [GCP_DATA_INFO]
    output.append("[GCP_DATA_INFO]")
    output.append("Type: GCP, Graph Coloring Problem")
    output.append(f"Node: {node_count}")
    output.append(f"Edge: {edge_count}")
    output.append("")

    # [ADJACENCY_List]
    output.append("[ADJACENCY_List]")
    for i in range(1, node_count + 1):
        if i in adj_list:
            neighbors = sorted(list(set(adj_list[i])))
            output.append(f"{i}: {neighbors}")

    return "\n".join(output)

if __name__ == "__main__":
    # parsed_gcp = parse_gcp_file('raw_gcp/withans/np_h/DSJC125.5_ans_17_lb_None_ub_None.col')
    
    src_dir = 'raw_gcp/withans'
    categories = ['np_h', 'np_m', 'np_s', 'np_u']
    
    for category in categories:
        file_path = f'{src_dir}/{category}/'
        for file_name in os.listdir(file_path):
            if file_name.endswith('.col'):
                full_path = os.path.join(file_path, file_name)
                parsed_gcp = parse_gcp_file(full_path)
                
                history_ans = file_name.split('/')[-1].split('_ans_')[1].split('_')[0]
                lowerbound = file_name.split('/')[-1].split('_lb_')[1].split('_')[0]
                upperbound = file_name.split('/')[-1].split('_ub_')[1].split('_')[0].split('.')[0]
                
                answer = history_ans if history_ans != 'None' else lowerbound
                print("file:", file_name, "answer:", answer)
                fname = file_name.split('/')[-1].split('_ans_')[0]
                
                with open(f'parsed_output/{fname}.desc.txt', 'w') as f:
                    f.write(parsed_gcp)

                with open(f'parsed_output/{fname}.ans.txt', 'w') as f:
                    f.write("Answer: " + answer + "\n")
                    f.write("History Answer: " + history_ans + "\n")
                    f.write("Lower Bound: " + lowerbound + "\n")
                    f.write("Upper Bound: " + upperbound + "\n")