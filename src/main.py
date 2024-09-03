import argparse
import os

from extract import extraction_entry, test
from analysis import analysis_entry
from params import PATH
from parse import parse_entry

# *********************
# HELPER FUNCTIONS
# *********************
def get_args():
    parser = argparse.ArgumentParser(description='Text Extractor Tool')
    parser.add_argument('-t', '--texts', type=str, help="Path to directory containing files")
    parser.add_argument('-e', '--exclude', nargs='+', default=[], help="List of files to exclude")
    parser.add_argument('-x', '--ext', nargs='+', default=[], help="List of file extensions to include")
    parser.add_argument('-l', '--labels', type=str, help="Path to directory containing labels")
    parser.add_argument('-s', '--label_suffix', type=str, default='', help="Label file suffixes")
    
    parser.add_argument('--analyze', action='store_true', help="Rerun analysis layer")
    parser.add_argument('--log', action='store_true', help="Activate log print statements")
    parser.add_argument('--test', action='store_true', help="Activate test functions")
    return parser.parse_args()

def init_paths(args):
    PATH["LABELS"] = args.labels


def print_info():
    print("Text Extractor Automation")
    print("Will use built-in folders for storing, root is at: ", PATH["ROOT"])
    print("Assumptions: Each file has a unique name")

# *********************
# MAIN FUNCTION
# *********************
def main():
    print_info()
    args = get_args()
    init_paths(args)
    metrics_empty = not any(f in os.listdir(PATH["METRICS"]) for 
                            f in ("roi_dataset.csv", "title_keywords.json"))

    # The parse function automatically runs if needed. It stores the parsed files in 
    # the texts directory and reuses them for extraction. If no files are present
    # it will parse all the files in the input directory.

    # The extraction layer will always run, it requires the analysis layer to be run 
    # before. It stores results in directory unless user forces reanalysis.

    parse_entry(args.texts, exclude=args.exclude, ext=args.ext)
    if args.analyze or metrics_empty: analysis_entry()
    extraction_entry(args)


if __name__ == '__main__':
    # test("0000891092-12-005749.txt")
    main()
    