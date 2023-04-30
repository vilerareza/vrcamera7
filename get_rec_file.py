import argparse


if __name__ == '__main__':

    # Argument handler
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type = str, required = True)

    # Parsing
    args = parser.parse_args()
    # Source
    input_path = args.input
    # Output directory
    out_dir = args.out_dir
    # Make it if does not exist
    os.makedirs(out_dir, exist_ok=True)