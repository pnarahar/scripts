import re
import json
import argparse
import os

def extract_vports(file_path):
    # Read the file and extract the module content using regex pattern matching
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex to match the ports
    port_pattern = re.compile(r'^\s*(input|output)\s+(wire|reg|logic)?\s*(\[\s*([\w\+\-\*\/\(\)]+)\s*:\s*([\w\+\-\*\/\(\)]+)\s*\])?\s*(\w+(\s*\[\s*[\w\+\-\*\/\(\)]+\s*:\s*[\w\+\-\*\/\(\)]+\s*\])*)', re.IGNORECASE | re.MULTILINE)
    ports = port_pattern.findall(content)

    # Create a list of dictionaries with port details
    port_list = []
    for match in ports:
        direction = match[0]
        port_type = match[1]
        msb = match[3]
        lsb = match[4]
        name = match[5]

        # Compute width
        width = '1'
        if msb and lsb:
            width = f"{msb}-{lsb}+1"

        port_list.append({
            'name': name,
            'msb': msb if msb else '0',
            'lsb': lsb if lsb else '0',
            'width': width,
            'direction': direction,
            'type': port_type.strip() if port_type else 'unknown'
        })

    # Convert the list to JSON format
    return json.dumps(port_list, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Extract port information from a Verilog module and output it in JSON format.')
    parser.add_argument('file_path', type=str, help='Path to the Verilog module file')
    parser.add_argument('-o', '--output_dir', type=str, help='Output directory for the JSON file')
    args = parser.parse_args()

    json_output = extract_vports(args.file_path)

    # Determine the output directory
    output_dir = args.output_dir if args.output_dir else os.path.dirname(args.file_path)

    # Create the output file name by replacing the extension with .json
    base_name = os.path.splitext(os.path.basename(args.file_path))[0]
    output_file = os.path.join(output_dir, base_name + '.json')

    # Write the JSON output to the file
    with open(output_file, 'w') as file:
        file.write(json_output)

    print(f"JSON output written to {output_file}")

if __name__ == "__main__":
    main()