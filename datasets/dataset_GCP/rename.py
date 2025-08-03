import os
import shutil

# replace the fourth comma into a dash start from the second row
def make_csv_separator(input_path: str, output_path: str):
    with open(input_path, "r") as file:
        lines = file.readlines()
    with open(output_path, "w") as file:
        for i, line in enumerate(lines):
            if i == 0:
                file.write(line)
            else:
                # replace the fourth comma with a dash
                parts = line.strip().split(",")
                print("parts:", parts)
                
                string = ",".join(parts[:4]) + "_" + ",".join(parts[4:])
                file.write(string + "\n")

def get_np_instances(path: str):
    # read the csv file
    with open(path, "r") as file:
        lines = file.readlines()

    # extract the first line (header)
    header = lines[0].strip().split(",")

    # get the graph coloring instances in the csv file
    gcp_instances_list = []    
    for i in range(1, len(lines)):
        line = lines[i].strip().split(",")
        # if the line is empty, skip it
        if len(line) == 0:
            continue
        # if the line is not a valid instance, skip it
        if line[0].strip() == "None" or line[0].strip() == "":
            continue
        
        file_name = line[0].strip()
        cur_ans = line[header.index("X(G)")]
        test_lower_bound = line[header.index("X_LB(G)")]
        test_upper_bound = line[header.index("X_UB(G)")]
        if file_name == "david":
            print("file_name:", file_name)
            print("cur_ans:", cur_ans)
            print("test_lower_bound:", test_lower_bound)
            print("test_upper_bound:", test_upper_bound)

        if cur_ans == "":
            cur_ans = None
        if test_lower_bound == "":
            test_lower_bound = None
        if test_upper_bound == "":
            test_upper_bound = None
        
        gcp_instances_list.append({
            "file_name": file_name,
            "cur_ans": cur_ans,
            "test_lower_bound": test_lower_bound,
            "test_upper_bound": test_upper_bound
        })
    
    return gcp_instances_list

def get_gcp_instances():
    np_h_instances = get_np_instances("./Graph Coloring Instances - NP-h.csv")
    np_m_instances = get_np_instances("./Graph Coloring Instances - NP-m.csv")
    np_s_instances = get_np_instances("./Graph Coloring Instances - NP-s.csv")
    np_u_instances = get_np_instances("./Graph Coloring Instances - NP-unknown.csv")

    return {
        "NP-H": np_h_instances,
        "NP-M": np_m_instances,
        "NP-S": np_s_instances,
        "NP-U": np_u_instances
    }

def rename_files(instances):
    base_path = "./raw_gcp/withans"
    os.makedirs(base_path, exist_ok=True)
    for category, instance_list in instances.items():
        category = category.replace("-", "_").lower()

        category_path = base_path + "/" + category + "/"
        if category not in os.listdir(base_path):
            os.makedirs(category_path, exist_ok=True)

    os.makedirs("./raw_gcp/no_ans", exist_ok=True)

    src_path = "./gcp_instances/"
    # traverse throught the source directory
    for file_name in os.listdir(src_path):
        if not file_name.endswith(".col"):
            continue
        # find the instance in the instances list
        found = False
        for category, instance_list in instances.items():
            for instance in instance_list:
                # print("file_name:", file_name)
                name = file_name.replace(".col", "")
                
                if name.lower() == instance["file_name"].lower():
                    new_dir = "./raw_gcp/withans/" + category.replace("-", "_").lower() + "/"
                    # rename the file
                    new_file_name = f"{instance['file_name']}_ans_{instance['cur_ans']}_lb_{instance['test_lower_bound']}_ub_{instance['test_upper_bound']}.col"
                    # print(f"Renaming {file_name} to {new_file_name}")
                    shutil.copy(os.path.join(src_path, file_name), os.path.join(new_dir, new_file_name))
                    found = True
                    break
        if not found:
            # copy the file to the no_ans directory
            shutil.copy(os.path.join(src_path, file_name), "./raw_gcp/no_ans/" + file_name)
            # print(f"File {file_name} not found in instances, copied to no_ans directory.")
        
if __name__ == "__main__":
    instances = get_gcp_instances()
    rename_files(instances)
    