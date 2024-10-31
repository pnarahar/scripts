import re
import json
import pandas as pd

def harmonize_field_name(field_name):
    """Standardize the field name by removing special characters and converting to uppercase."""
    return re.sub(r'[^A-Za-z0-9]', '', field_name).upper()

def parse_verilog(file_path):
    """Extract fields from Verilog file and harmonize their names."""
    queue_data = {}

    with open(file_path, 'r') as file:
        lines = file.readlines()

    field_pattern = re.compile(r"(\w+QNew\w+)\s*=\s*.*;")
    comment_pattern = re.compile(r"//\s*(.*)")

    for line in lines:
        field_match = field_pattern.search(line)
        if field_match:
            full_field = field_match.group(1)
            queue_name = re.match(r"(\w+)QNew", full_field).group(1)
            field_name = re.sub(r"\w+QNew", "", full_field)
            
            # Harmonize names
            harmonized_field = harmonize_field_name(field_name)
            harmonized_queue = harmonize_field_name(queue_name)

            comment_match = comment_pattern.search(line)
            comment = comment_match.group(1).strip() if comment_match else ""

            if harmonized_queue not in queue_data:
                queue_data[harmonized_queue] = []

            queue_data[harmonized_queue].append({
                "field": harmonized_field,
                "comment": comment
            })

    with open("queue_fields.json", "w") as json_file:
        json.dump(queue_data, json_file, indent=4)

    return queue_data

def read_queue_fields_from_excel(file_path):
    """Read fields and comments from Excel and harmonize names."""
    excel_data = pd.ExcelFile(file_path)
    queue_data = {}

    for sheet_name in excel_data.sheet_names:
        df = excel_data.parse(sheet_name)
        
        fields = []
        for _, row in df.iterrows():
            harmonized_field = harmonize_field_name(row['Field'])
            harmonized_queue = harmonize_field_name(sheet_name)

            fields.append({
                "field": harmonized_field,
                "comment": row['Comment']
            })

        queue_data[harmonized_queue] = fields

    return queue_data

def compare_data(verilog_data, excel_data):
    """Compare and harmonize data between Verilog and Excel sources."""
    combined_data = {}

    for queue_name, verilog_fields in verilog_data.items():
        combined_data[queue_name] = []
        excel_fields = {item['field']: item['comment'] for item in excel_data.get(queue_name, [])}
        
        for field in verilog_fields:
            field_name = field['field']
            verilog_comment = field['comment']
            excel_comment = excel_fields.get(field_name, "")
            combined_comment = verilog_comment or excel_comment

            combined_data[queue_name].append({
                "field": field_name,
                "comment": combined_comment
            })

    return combined_data

# Usage
verilog_data = parse_verilog("design.sv")
excel_data = read_queue_fields_from_excel("queue_fields.xlsx")
harmonized_data = compare_data(verilog_data, excel_data)

# Save harmonized data to JSON
with open("harmonized_queue_data.json", "w") as json_file:
    json.dump(harmonized_data, json_file, indent=4)

print("Harmonized data saved to 'harmonized_queue_data.json'.")