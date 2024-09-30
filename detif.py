import re
import sys
import argparse

def find_if_statements(line_number, file_path, debug=False):
    if_pattern = re.compile(r'^\s*<pl>\s*if\s*\((.*?)\)\s*(?:\{)?')
    else_pattern = re.compile(r'^\s*<pl>\s*}\s*else\s*(?:\{)?')
    elsif_pattern = re.compile(r'^\s*<pl>\s*}\s*elsif\s*\((.*?)\)\s*(?:\{)?')
    for_pattern = re.compile(r'^\s*<pl>\s*for\s*\(\$(.*?)=.*?\)\s*(?:\{)?')
    closing_brace_pattern = re.compile(r'^\s*<pl>\s*}\s*$')
    
    with open(file_path, 'r') as f:
        code_lines = f.readlines()

    condition_stack = []
    brace_stack = []
    nesting_depth = 0
    current_conditions = []

    for i, line in enumerate(code_lines, 1):
        line = line.strip()
        if debug:
            print(f"Processing line {i}: '{line}'")  # Debug print to show the line being processed
        
        if if_match := if_pattern.match(line):
            condition = if_match.group(1)
            condition_stack.append(condition)
            nesting_depth += 1
            brace_stack.append(nesting_depth)
            current_conditions = condition_stack.copy()
            if debug:
                print(f"Line {i}: IF condition '{condition}' found. Pushing to condition_stack: {condition_stack}")
                print(f"Line {i}: Pushing to brace_stack: {brace_stack}")
        elif else_pattern.match(line):
            if debug:
                print(f"Line {i}: ELSE block found.")  # Debug print to show ELSE block match
            if brace_stack:
                if condition_stack:
                    last_condition = condition_stack.pop()
                    condition_stack.append(f'NOT ({last_condition})')
                    current_conditions = condition_stack.copy()
                    if debug:
                        print(f"Line {i}: Pushing complement of last IF condition to condition_stack: {condition_stack}")
                        print(f"Line {i}: Updated current_conditions: {current_conditions}")
        elif elsif_match := elsif_pattern.match(line):
            condition = elsif_match.group(1)
            if debug:
                print(f"Line {i}: ELSIF condition '{condition}' found.")  # Debug print to show ELSIF block match
            if brace_stack:
                if condition_stack:
                    last_condition = condition_stack.pop()
                    condition_stack.append(f'NOT ({last_condition})')
                    condition_stack.append(condition)
                    current_conditions = condition_stack.copy()
                    if debug:
                        print(f"Line {i}: Pushing complement of last IF condition and new ELSIF condition to condition_stack: {condition_stack}")
                        print(f"Line {i}: Updated current_conditions: {current_conditions}")
        elif for_match := for_pattern.match(line):
            index_variable = for_match.group(1)
            condition_stack.append(f'FOR(${index_variable})')
            nesting_depth += 1
            brace_stack.append(nesting_depth)
            if debug:
                print(f"Line {i}: FOR loop with index variable '${index_variable}' found. Pushing 'FOR(${index_variable})' to condition_stack: {condition_stack}")
                print(f"Line {i}: Pushing to brace_stack: {brace_stack}")
        elif closing_brace_pattern.match(line):
            if debug:
                print(f"Line {i}: Closing brace found.")  # Debug print to show closing brace match
            if brace_stack:
                brace_stack.pop()
                nesting_depth -= 1
                if debug:
                    print(f"Line {i}: Popping from brace_stack: {brace_stack}")
                if condition_stack:
                    popped_condition = condition_stack.pop()
                    if debug:
                        print(f"Line {i}: Popping from condition_stack: {popped_condition}")
                current_conditions = condition_stack.copy()
                if debug:
                    print(f"Line {i}: Updated current_conditions: {current_conditions}")
                if nesting_depth == 0 and not (else_pattern.match(line) or elsif_pattern.match(line)):
                    condition_stack.clear()
                    if debug:
                        print(f"Line {i}: Final closing brace encountered. Clearing condition_stack.")
        
        if i == line_number:
            if current_conditions:
                return f"Line {line_number} is executed when: {' AND '.join(current_conditions)}"
            else:
                return f"Line {line_number} is not under any conditional block."

    return f"Line {line_number} is not under any conditional block."

def test_all_lines(file_path, debug=False):
    with open(file_path, 'r') as f:
        total_lines = len(f.readlines())
    for line_number in range(1, total_lines + 1):
        result = find_if_statements(line_number, file_path, debug)
        print(f"Line {line_number}: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file to find conditional statements.")
    parser.add_argument("file_path", help="Path to the file to be processed")
    parser.add_argument("line_number", nargs="?", type=int, help="Specific line number to process")
    parser.add_argument("-debug", action="store_true", help="Enable debug messages")

    args = parser.parse_args()

    if args.line_number:
        print(find_if_statements(args.line_number, args.file_path, args.debug))
    else:
        test_all_lines(args.file_path, args.debug)