import re

def extract_signals_from_sourcelist(verilog_file):
    signals = []
    inside_sourcelist = False
    sourcelist_content = ""

    # Open the Verilog file for reading
    with open(verilog_file, 'r') as file:
        for line in file:
            # Check if we are entering the SourceList port
            if '.SourceList(' in line:
                inside_sourcelist = True
                sourcelist_content += line.strip()  # Start collecting the SourceList content

            # If we are inside the SourceList, continue collecting lines
            elif inside_sourcelist:
                sourcelist_content += line.strip()

                # Check if this line contains the closing parenthesis ')'
                if ')' in line:
                    inside_sourcelist = False  # We have reached the end of the SourceList

                    # Now we can extract signals from the complete SourceList content
                    signals.extend(extract_signals_from_string(sourcelist_content))
                    sourcelist_content = ""  # Reset for the next SourceList instance (if any)

    return signals

def extract_signals_from_string(source_list):
    # Regex pattern to extract signal names, making the bit-width optional
    regex_pattern = r'{[^,]+,[^,]+,([a-zA-Z_][a-zA-Z0-9_]*(?:\[\d+:\d+\])?)}'

    # Find all signals inside the SourceList string
    signals = re.findall(regex_pattern, source_list)

    # Remove the bit-width suffix (if present) and strip trailing parts after the last underscore
    signal_names = [strip_trailing_underscore_parts(signal.split('[')[0]) for signal in signals]

    # Append unique IDs to each signal name
    return append_unique_ids(signal_names)

def strip_trailing_underscore_parts(signal):
    # Remove everything after the last underscore in the signal name
    return signal.rsplit('_', 1)[0]

def append_unique_ids(signal_names):
    # Create a list with unique incrementing IDs appended to each signal
    return [f"{signal}_{i+1}" for i, signal in enumerate(signal_names)]


# Example Usage
verilog_file = 'path_to_verilog_file.v'
extracted_signals = extract_signals_from_sourcelist(verilog_file)

# Print the extracted signals with unique IDs
print(extracted_signals)
