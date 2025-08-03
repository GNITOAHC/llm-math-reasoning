def parse_nsp_data(input_data):
    lines = [line.strip() for line in input_data.split('\n') if line.strip() and not line.strip().startswith('#')]
    parsed_data = {
        'metadata': {},
        'nsp_data_info': {'shift_names': []},
        'shift_info': [],
        'shift_requirements': [],
        'block_constraints': {'off_block': {}, 'work_block': {}},
        'forbidden_sequences': {'length2': [], 'length3': []}
    }
    
    # Parse metadata
    parsed_data['metadata']['Name'] = 'NurseSchedulingWeek1'
    parsed_data['metadata']['ScheduleLength'] = int(lines[0])
    parsed_data['metadata']['NumberOfEmployees'] = int(lines[1])
    
    # Parse NSP data info
    parsed_data['nsp_data_info']['Type'] = 'NSP, Nurse Scheduling Problem'
    parsed_data['nsp_data_info']['NumberOfShifts'] = int(lines[2])
    parsed_data['nsp_data_info']['shift_names'] = ['D', 'A', 'N']
    
    # Parse shift requirements
    # shift_requirements = [
    #     list(map(int, lines[i].split())) for i in range(3, 6)
    # ]
    for day, reqs in enumerate(shift_requirements):
        parsed_data['shift_requirements'].append({day: reqs})
    
    # Parse shift info
    for line in lines[6:9]:
        name, start, duration, min_block, max_block = line.split()
        parsed_data['shift_info'].append({
            'name': name,
            'start': int(start),
            'duration': int(duration),
            'min_block_length': int(min_block),
            'max_block_length': int(max_block)
        })
    
    # Parse block constraints
    off_block = list(map(int, lines[9].split()))
    work_block = list(map(int, lines[10].split()))
    parsed_data['block_constraints']['off_block'] = {
        'min': off_block[0],
        'max': off_block[1]
    }
    parsed_data['block_constraints']['work_block'] = {
        'min': work_block[0],
        'max': work_block[1]
    }
    
    # Parse forbidden sequences
    seq_counts = list(map(int, lines[11].split()))
    for line in lines[12:12+seq_counts[0]]:
        parsed_data['forbidden_sequences']['length2'].append(line.strip())
    
    return parsed_data

def format_output(parsed_data):
    output = []
    
    # METADATA section
    output.append('[METADATA]')
    for key, value in parsed_data['metadata'].items():
        output.append(f"{key}: {value}")
    
    # NSP_DATA_INFO section
    output.append('\n[NSP_DATA_INFO]')
    output.append(f"Type: {parsed_data['nsp_data_info']['Type']}")
    output.append(f"NumberOfShifts: {parsed_data['nsp_data_info']['NumberOfShifts']}")
    output.append(f"ShiftNames: {', '.join(parsed_data['nsp_data_info']['shift_names'])}")
    
    # SHIFT_INFO section
    output.append('\n[SHIFT_INFO]')
    output.append('# Format: Name, Start(min), Duration(min), MinBlockLength, MaxBlockLength')
    for shift in parsed_data['shift_info']:
        output.append(f"{shift['name']}, {shift['start']}, {shift['duration']}, "
                     f"{shift['min_block_length']}, {shift['max_block_length']}")
    
    # SHIFT_REQUIREMENTS section
    output.append('\n[SHIFT_REQUIREMENTS]')
    output.append('# Format: DayIndex: [D, A, N]')
    for req in parsed_data['shift_requirements']:
        for day, values in req.items():
            output.append(f"{day}: [{', '.join(map(str, values))}]")
    
    # BLOCK_CONSTRAINTS section
    output.append('\n[BLOCK_CONSTRAINTS]')
    output.append('# Format: MinOffBlockLength, MaxOffBlockLength, MinWorkBlockLength, MaxWorkBlockLength')
    output.append(f"OffBlock: {parsed_data['block_constraints']['off_block']['min']}, "
                 f"{parsed_data['block_constraints']['off_block']['max']}")
    output.append(f"WorkBlock: {parsed_data['block_constraints']['work_block']['min']}, "
                 f"{parsed_data['block_constraints']['work_block']['max']}")
    
    # FORBIDDEN_SEQUENCES section
    output.append('\n[FORBIDDEN_SEQUENCES]')
    output.append('# Format: SequenceLength=2')
    output.append('Length2:')
    for seq in parsed_data['forbidden_sequences']['length2']:
        output.append(f"  - {seq}")
    output.append('Length3:')
    output.append('  # none')
    
    return '\n'.join(output)

if __name__ == "__main__":
    import os
    
    for filename in os.listdir('workforceScheduling'):
        if not filename.endswith('.txt'):
            continue
        # Input data
        with open(f'workforceScheduling/{filename}', 'r', encoding='utf-8') as file:
            input_data = file.read()

        # Parse and format the data
        parsed = parse_nsp_data(input_data)
        formatted_output = format_output(parsed)
        # print(formatted_output)
        with open(f'parsed_output/{filename}', 'w', encoding='utf-8') as file:
            file.write(formatted_output)