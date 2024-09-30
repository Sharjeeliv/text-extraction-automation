import argparse
import os

from .extract import extraction_entry, test
from .analysis import analysis_entry
from .params import PATH, init_paths as params_init_paths
from .parse import parse_entry
from .utils import time_execution

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
    PATH["LABELS"] = args.labels if args.labels is not None else PATH["LABELS"]
    PATH["RESULTS"] = args.output if args.output is not None else PATH["RESULTS"]
    PATH['TEXTS'] = args.texts if args.texts is not None else PATH['TEXTS']

def metrics_empty(path=PATH["METRICS"]):
    return not any(f in os.listdir(path) for 
                   f in ("roi_dataset.csv", "title_keywords.json"))

# *********************
# MAIN FUNCTION
# *********************
def main():
    # Validate directories
    params_init_paths()
    args = get_args()
    if not args.texts or not os.path.exists(args.texts):
        print("Texts directory not found!")
        return -1
    if not args.labels or not os.path.exists(args.labels):
        print("Labels directory not found!")
        return -1

    init_paths(args)
    
    metrics_empty()

    # The parse function automatically runs if needed. It stores the parsed files in 
    # the texts directory and reuses them for extraction. If no files are present
    # it will parse all the files in the input directory.

    # The extraction layer will always run, it requires the analysis layer to be run 
    # before. It stores results in directory unless user forces reanalysis.

    parse_entry(args.texts, exclude=args.exclude, ext=args.ext)
    if args.analyze or metrics_empty: analysis_entry(args.labels, args.word, ext=['.txt'])
    # extraction_entry(args)

    return 0

@time_execution
def extract_text(unique_id, label_word, mask, ext=[], analyze=False, log=False, test=False):

    params_init_paths()

    text_path = PATH['TEXTS'] / unique_id
    label_path = PATH['LABELS'] / unique_id
    output_path = PATH['RESULTS'] / unique_id
    metric_path = PATH['METRICS'] / unique_id

    if log:
        print(
            f"Text Path:    {text_path}\n"
            f"Output Path:  {output_path}\n"
            f"Label Path:   {label_path}\n"
            f"Metric Path:   {metric_path}\n"


            f"Label Word:   {label_word}\n"
            f"Extensions:   {ext}\n"
            f"Analyze:      {analyze}\n"
            f"Log:          {log}\n"
            f"Test:         {test}\n"
            f"Metrics:      {metrics_empty(metric_path)}\n"

        )
    
    parse_entry(input_path=text_path, output_path=text_path, mask=mask, label=label_word, ext=ext)
    if analyze or metrics_empty(metric_path): analysis_entry(label_path, metric_path, label_word)
    extraction_entry(text_path, metric_path, label_path, output_path, label_word, mask=mask, exts=[".txt"], log=log, test=test)

    return
    # init_paths(args)
    # parse_entry(args.texts, exclude=args.exclude, ext=args.ext)
    # if args.analyze: analysis_entry()
    # extraction_entry(args)

if __name__ == '__main__':
    text_path = "/Users/sharjeelmustafa/Desktop/RA24_Testing/texts"
    label_path = "/Users/sharjeelmustafa/Desktop/RA24_Testing/labels"
    label_word = "Extracted"
    ext = [".txt", ".htm", ".html"]
    extract_text(text_path, label_path, label_word, ext=ext, log=False, test=True)
    