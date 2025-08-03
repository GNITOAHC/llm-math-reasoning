def parse_nsp_data(input_data):
    lines = [line.strip() for line in input_data.split('\n') if line.strip()]
    parsed_data = {
        'metadata': {},
        'nsp_data_info': {'shift_names': []},
        'shift_info': [],
        'shift_table': [],
        'block_constraints': {'off_block': {}, 'work_block': {}},
        'forbidden_sequences': {'length2': [], 'length3': []}
    }
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#'):
            line = line.strip('#').strip()  # Remove leading '#' and whitespace
            line = '# ' + line.strip()  # Re-add '#' for consistency
        
        # Parse Length of the schedule
        if line.startswith('# Length of the schedule'):
            i += 1
            parsed_data['metadata']['ScheduleLength'] = int(lines[i])
        
        # Parse Number of Employees
        elif line.startswith('# Number of Employees'):
            i += 1
            parsed_data['metadata']['NumberOfEmployees'] = int(lines[i])
        
        # Parse Number of Shifts
        elif line.startswith('# Number of Shifts'):
            i += 1
            parsed_data['nsp_data_info']['NumberOfShifts'] = int(lines[i])
            parsed_data['nsp_data_info']['Type'] = 'NSP, Nurse Scheduling Problem'
        
        # Parse Temporal Requirements Matrix
        elif line.startswith('# Temporal Requirements Matrix'):
            i += 1
            shift_requirements = []
            while i < len(lines) and not lines[i].startswith('#'):
                shift_requirements.append(list(map(int, lines[i].split())))
                i += 1
            for day, reqs in enumerate(shift_requirements):
                parsed_data['shift_table'].append({day: reqs})
            continue  # Skip increment since we already moved i
        
        # Parse Shift Info
        elif line.startswith('# ShiftName, Start, Length, Name, MinlengthOfBlocks, MaxLengthOfBlocks'):
            i += 1
            parsed_data['nsp_data_info']['shift_names'] = []  # Initialize shift names
            while i < len(lines) and not lines[i].startswith('#'):
                parts = lines[i].split()
                if len(parts) >= 5:  # Ensure valid shift info line
                    name, start, duration, min_block, max_block = parts[:5]
                    parsed_data['shift_info'].append({
                        'name': name,
                        'start': int(start),
                        'duration': int(duration),
                        'min_block_length': int(min_block),
                        'max_block_length': int(max_block)
                    })
                    if name not in parsed_data['nsp_data_info']['shift_names']:
                        parsed_data['nsp_data_info']['shift_names'].append(name)
                i += 1
            continue
        
        # Parse Minimum and maximum length of days-off blocks
        elif line.startswith('# Minimum and maximum length of days-off blocks'):
            i += 1
            off_block = list(map(int, lines[i].split()))
            parsed_data['block_constraints']['off_block'] = {
                'min': off_block[0],
                'max': off_block[1]
            }
        
        # Parse Minimum and maximum length of work blocks
        elif line.startswith('# Minimum and maximum length of work blocks'):
            i += 1
            work_block = list(map(int, lines[i].split()))
            parsed_data['block_constraints']['work_block'] = {
                'min': work_block[0],
                'max': work_block[1]
            }
        
        # Parse Number of not allowed shift sequences
        elif line.startswith('# Number of not allowed shift sequences'):
            i += 1
            seq_counts = list(map(int, lines[i].split()))
            i += 1
            # Parse forbidden sequences
            if i < len(lines) and lines[i].startswith('# Not allowed shift sequences'):
                i += 1
                for j in range(seq_counts[0]):  # Number of length-2 sequences
                    if i < len(lines):
                        parsed_data['forbidden_sequences']['length2'].append(lines[i])
                        i += 1
                # Handle length-3 sequences (none in this case, but for completeness)
                for j in range(seq_counts[1]):
                    if i < len(lines):
                        parsed_data['forbidden_sequences']['length3'].append(lines[i])
                        i += 1
            continue
        
        i += 1
    
    # Set metadata name
    parsed_data['metadata']['Name'] = 'NurseSchedulingWeek1'
    
    return parsed_data

def format_output(parsed_data):
    output = []
    
    # METADATA section
    output.append('[METADATA]')
    # for key, value in parsed_data['metadata'].items():
    #     output.append(f"{key}: {value}")
    output.append(f"Name: {parsed_data['metadata']['Name']}")
    output.append(f"Type: {parsed_data['nsp_data_info']['Type']}")

    shift_names = parsed_data['nsp_data_info']['shift_names']
    # NSP_DATA_INFO section
    output.append('\n[NSP_DATA_INFO]')
    output.append(f"LengthOfSchedule: {parsed_data['metadata']['ScheduleLength']}")
    output.append(f"NumberOfEmployees: {parsed_data['metadata']['NumberOfEmployees']}")
    
    output.append(f"NumberOfShifts: {parsed_data['nsp_data_info']['NumberOfShifts']}")
    output.append(f"ShiftNames: [{', '.join(shift_names)}] ")
    
    # SHIFT_INFO section
    output.append('\n[SHIFT_INFO]')
    for shift in parsed_data['shift_info']:
        output.append(f"{shift['name']}, StartTime(min): {shift['start']}, Duration(min): {shift['duration']}, "
                      f"MinBlockLength: {shift['min_block_length']}, MaxBlockLength: {shift['max_block_length']}")

    # SHIFT_REQUIREMENTS section
    output.append('\n[SHIFT_TABLE]')
    output.append('# Employee requirements for each shift on each day')
    for req in parsed_data['shift_table']:
        for day, values in req.items():
            output.append(f"{shift_names[day]}: [{', '.join(map(str, values))}]")
    
    # BLOCK_CONSTRAINTS section
    output.append('\n[BLOCK_CONSTRAINTS]')
    output.append(f"WorkBlockLength: min {parsed_data['block_constraints']['work_block']['min']}, "
                 f"max {parsed_data['block_constraints']['work_block']['max']}")
    output.append(f"OffBlockLength: min {parsed_data['block_constraints']['off_block']['min']}, "
                 f"max {parsed_data['block_constraints']['off_block']['max']}")
    
    # FORBIDDEN_SEQUENCES section
    output.append('\n[FORBIDDEN_SEQUENCES]')
    for seq in parsed_data['forbidden_sequences']['length2']:
        output.append(f"[{', '.join(seq.split())}]")
    for seq in parsed_data['forbidden_sequences']['length3']:
        output.append(f"[{', '.join(seq.split())}]")

    return '\n'.join(output)

def get_problem_description():
    return f"""[PROBLEM DESCRIPTION]
The desc file contains the parsed data for the Nurse Scheduling Problem (NSP).
It includes metadata, shift information, shift requirements, block constraints, and forbidden sequences.

[NSP_DATA_INFO]
# Type: NSP, Nurse Scheduling Problem
# NumberOfShifts: Total number of shift types (excluding days-off)
# ShiftNames: List of working shift names
#  e.g., [D, A, N] for Day, Afternoon, and Night shifts
#  for output [-] represents days-off shift
# LengthOfSchedule: Number of days in the schedule (e.g., 7 for a weekly schedule)
# NumberOfEmployees: Total number of nurses to be scheduled

# The output schedule matrix will be a 2D array with dimensions
#  e.g. if LengthOfSchedule is 5 and NumberOfEmployees is 3, the schedule will be a 5x3 matrix 
#   where each row represents a nurse and each column represents a day:
#   [x, x, x, x, x]
#   [x, x, x, x, x]
#   [x, x, x, x, x]
#   where 'x' is a shift name for each day (e.g., D, A, N) or '-' for days-off

[SHIFT_INFO]
# Name: The name of the shift
# ShiftName(Work) [D, A, N]: The name of the shift (D for Day, A for Afternoon, N for Night)
# ShiftName(days-off) [-]: Shift: use '-' to represent days-off shift

[SHIFT_TABLE]
# StartTime: The start time of the shift in minutes
# Duration: The duration of the shift in minutes
# BlockLength: a consecutive days on the same shift,
#  e.g., [D, D, D, D, A, N] is a block of 4 days on D, 1 day on A and 1 day on N
# MinBlockLength: The minimum length of a block of consecutive days on the same shift
# MaxBlockLength: The maximum length of a block of consecutive days on the same shift

[BLOCK_CONSTRAINTS]
# WorkBlock(D, N, A): employee's consecutive 'work days' must between MinWorkBlockLength and MaxWorkBlockLength
# OffBlock(-): employee's consecutive 'days off' must between MinOffBlockLength and MaxOffBlockLength
#  e.g., WorkBlock: (min 5, max 6), OffBlock(-): (min 3, max 4) means
#  *Invalid* Shift Table: [D, D, A, N, -, -, D, D, A], because
#   workblocks [D, D, A, N] has 4 days (less than 5) and [D, D, A] has 3 days (less than 5), offblocks [-, -] has 2 days (less than 3)
#  *Valid* Shift Table:   [D, D, A, N, D, D, -, -, -], because
#   workblocks [D, D, A, N, D, D] has 6 days (between 5 and 6) and offblocks [-, -] has 2 days (between 3 and 4)

[FORBIDDEN_SEQUENCES]
# Forbidden shift transitions (cannot be scheduled in this order):
# shift_name1 shift_name2
#  e.g., [D, A] : NOT ALLOWED for "Day shift followed by Afternoon shift"
#  e.g., [D, N] : NOT ALLOWED for "Day shift followed by Night shift"
# shift_name1 -> days-off(-) -> shift_name2
#  e.g., [D, -, A] : NOT ALLOWED for "Day shift followed by a days-off day followed by Afternoon shift"
#  e.g., [D, -, N] : NOT ALLOWED for "Day shift followed by a days-off day followed by Night shift"
"""

import re

def parsed_nsp_solution(text):
    problem_schedules = []
    current_block = []
    in_solution = False

    for line in text.strip().splitlines():
        line = line.strip()

        # Start of a new problem block
        if line.startswith("-----PROBLEM"):
            if current_block:
                problem_schedules.append(current_block)
                current_block = []
            in_solution = True
            continue
        
        # If we’re reading a solution block
        if in_solution:
            if not line:
                continue
            if re.match(r'^[A-Z\- ]+$', line):
                shifts = line.split()
                current_block.append(shifts)

    # Add last block if exists
    if current_block:
        problem_schedules.append(current_block)

    return problem_schedules

# Input data

if __name__ == "__main__":
    import os
    
    with open('./parsed_output/Description.txt', 'w', encoding='utf-8') as file:
        file.write(get_problem_description())
    
    for filename in os.listdir('workforceScheduling'):
        if not filename.endswith('.txt'):
            continue
        # Input data
        with open(f'./workforceScheduling/{filename}', 'r', encoding='utf-8') as file:
            input_data = file.read()

        # Parse and format the data
        parsed = parse_nsp_data(input_data)
        formatted_output = format_output(parsed)

        output_filename = filename.replace('.txt', '.desc.txt')
        with open(f'./parsed_output/{output_filename}', 'w', encoding='utf-8') as file:
            file.write(formatted_output)

        print("filename:", output_filename)
    
    with open("./solutions.txt", "r", encoding="utf-8") as solution_file:
        raw_text = solution_file.read()
    schedule_arrays = parsed_nsp_solution(raw_text)

    # Display result for example
    for i, schedule in enumerate(schedule_arrays, 1):
        with open(f"./parsed_output/Example{i}.ans.txt", "w", encoding="utf-8") as file:
            for r_i, row in enumerate(schedule):
                file.write(f"{r_i}: [{', '.join(row)}]\n")
