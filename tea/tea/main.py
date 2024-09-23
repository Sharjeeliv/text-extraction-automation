import argparse
import os

from extract import extraction_entry, test
from tea.analysis import analysis_entry
from params import PATH
from parse import parse_entry

# *********************
# HELPER FUNCTIONS
# *********************
def get_args():
    parser = argparse.ArgumentParser(description='Text Extractor Tool')
    # File Path Arguments
    parser.add_argument('-t', '--texts', type=str, help="Path to directory containing raw text files")
    parser.add_argument('-l', '--labels', type=str, help="Path to directory containing labels files")
    parser.add_argument('-o', '--output', type=str, help="Path to directory for result files")

    # Additional Arguments
    parser.add_argument('-w', '--word', type=str, help="Label word to distinguish result, raw, and label files")
    parser.add_argument('-e', '--ext', nargs='+', default=[], help="List of file extensions to include")   

    # Optional Arguments
    parser.add_argument('--analyze', action='store_true', help="Rerun analysis layer")
    parser.add_argument('--log', action='store_true', help="Activate log print statements")
    parser.add_argument('--test', action='store_true', help="Activate test functions")
    return parser.parse_args()

def init_paths(args):
    PATH["LABELS"] = args.labels
    PATH["RESULTS"] = args.output
    PATH['TEXTS'] = args.texts


# *********************
# MAIN FUNCTION
# *********************
def main():
    # Validate directories
    args = get_args()
    if not args.texts or not os.path.exists(args.texts):
        print("Texts directory not found!")
        exit()
    if not args.labels or not os.path.exists(args.labels):
        print("Labels directory not found!")
        exit()

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
    