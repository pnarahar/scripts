import argparse

def filter_files(sublist_path, superlist_path, output_path):
    # Read the sublist file and extract file names
    with open(sublist_path, 'r') as f:
        sub_list = f.read().strip().splitlines()
    sub_file_names = {file.split('/')[-1] for file in sub_list}

    # Read the superlist file
    with open(superlist_path, 'r') as f:
        super_list = f.read().strip().splitlines()

    # Filter the super list based on sublist file names
    filtered_super_list = [
        path for path in super_list if path.split('/')[-1] in sub_file_names
    ]

    # Write the filtered super list to the output file
    with open(output_path, 'w') as f:
        f.write('\n'.join(filtered_super_list))
    
    print(f"Filtered super list written to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter files from a super list based on a sub list.")
    parser.add_argument('sublist', help="Path to the file containing the sub list of files.")
    parser.add_argument('superlist', help="Path to the file containing the super list of files.")
    parser.add_argument('output', help="Path to the output file for the filtered super list.")
    args = parser.parse_args()

    # Call the filtering function with the provided arguments
    filter_files(args.sublist, args.superlist, args.output)
