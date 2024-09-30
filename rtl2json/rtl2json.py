import json
import re
import argparse

def parse_rtl(line, current_lhs, debug=False):
    if debug:
        print(f"Parsing line: {line}")
    
    lhs = current_lhs
    if '=' in line:
        lhs, rhs = line.split('=', 1)
        lhs = lhs.replace('assign', '').strip()
        rhs = rhs.strip().strip('{}').strip()
    else:
        rhs = line.strip()
    
    if debug:
        if lhs:
            print(f"LHS: {lhs}")
        print(f"RHS: {rhs}")
    
    field_name = rhs.split('[')[0].strip()
    if debug:
        print(f"Processing field: {field_name}")
    
    comment_match = re.search(r'//\s*\[(\d+):(\d+)\]', line)
    if comment_match:
        msb, lsb = comment_match.groups()
        parsed_rhs = [{
            'field': field_name,
            'msb': int(msb),
            'lsb': int(lsb)
        }]
        if debug:
            print(f"Field: {field_name}, MSB: {msb}, LSB: {lsb}")
    else:
        parsed_rhs = [{'field': field_name}]
        if debug:
            print(f"Field: {field_name}, No range found")
    
    return lhs, parsed_rhs

def rtl2json(rtl_file, debug=False):
    with open(rtl_file, 'r') as file:
        lines = file.readlines()

    data = {}
    in_debug_bus = False
    current_lhs = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "// Begin of Debug Bus":
            in_debug_bus = True
            if debug:
                print("Entering Debug Bus section")
            continue
        elif line == "// End of Debug Bus" or line.startswith("end"):
            in_debug_bus = False
            current_lhs = None
            if debug:
                print("Exiting Debug Bus section")
            continue

        if in_debug_bus:
            if line.startswith("always @* begin") or line.startswith("always_comb begin") or line.startswith("//") or line == "};":
                continue
            current_lhs, parsed_rhs = parse_rtl(line, current_lhs, debug)
            if current_lhs:
                if current_lhs not in data:
                    data[current_lhs] = []
                data[current_lhs].extend(parsed_rhs)
            else:
                data.update({item['field']: item for item in parsed_rhs})

    json_file = rtl_file.replace('.v', '.json')
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
    if debug:
        print(f"JSON output written to {json_file}")

def main():
    parser = argparse.ArgumentParser(description='Convert RTL to JSON.')
    parser.add_argument('rtl_file', type=str, help='Input RTL file')
    parser.add_argument('-debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    rtl2json(args.rtl_file, args.debug)

if __name__ == "__main__":
    main()