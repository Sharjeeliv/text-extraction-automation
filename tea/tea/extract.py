# Text Extraction Tool, By: Sharjeel Mustafa

# First Party
import argparse
import os
import re
import concurrent.futures
from collections import Counter
from typing import List
from multiprocessing import Manager
from os.path import join as pjoin

# Third Party
import pandas as pd

# Local
from utils import time_execution, convert_to_series, metrics
from tests import overlap_similarity
from parse import get_files
from params import PATH, DEFAULT, DELIM


# *********************
# VARIABLE DECLARATIONS
# *********************
TITLE, SCORE = 0, 1
# Main and fine-grained regex patterns
R_TITLE = r"^\s*\w(?:\w*[ (&,\'\’\w)-]++|(?<=\(\w))+(?:\(\w*\))?[:;]?$"
R_TITLE_FRAGMENT = r"^\s*\w(?:\w*[ (&,\'\’\w)-]++|(?<=\(\w))+(?:\(\w*\))?:"
R_NO_NUM = r"^\D.*\D$"
R_SENTENCE = r"^(\w+\s\w+\s\w+\s?)((\w+|-)\s?)*"
RM_PAGE = r"<PAGE>"
# Global Control Variables
LOG_MODE = False

# *********************
#  EXTRACTIONS FUNCTIONS
# *********************
def extract_titles(file_path: str, delimiter: str = '\n'):
    # Input validation and Guard Clause
    text, sec_html = get_text(file_path)
    text = re.sub(RM_PAGE, "", text)
    if text is None: return
    input_path = pjoin(PATH['METRICS'], 'title_keywords.json')
    keyword_dataset =  pd.read_json(input_path)

    # Slices Document into "coarse titles"
    titles, idx, raws = [], [], []
    delim = delimiter if sec_html else "\n\n"
    for i, line in enumerate(text.split(delim)):
        raw = line
        if not sec_html:
            line = re.sub(r'[\n\t\r]', ' ', line)
            line = re.sub(r'\s+', ' ', line)
        title = get_title(line, keyword_dataset)
        if title is None: continue
        titles.append(title)
        idx.append(i)
        raws.append(raw)


    # Extracts "fine-grain titles" from "coarse titles" (can be used to determine end titles too)
    candidate_titles, titles, idx = extract_candidiates(titles, idx, keyword_dataset)
    if LOG_MODE:
        output = f"File: {os.path.basename(file_path)}\n"
        output += "\n\033[93;1mCANDIDATE TITLE SCORES\033[0m\n"
        output += "\n".join(f"{score[0]} \t {title}" for title, score in candidate_titles)
        print(output)
        
    return candidate_titles, titles, raws


def extract_candidiates(titles: List[str], idx: List[int], dataset: pd.DataFrame, default_order: bool=False) -> List[str]:
    MED_W_FREQ, scores = 1, {}
    for title, block in zip(titles, idx):
        # Count words in the title
        words = Counter(word.strip().lower() for word in title.split(DELIM["WORD"]) 
                        if word.strip().lower() in dataset and word not in {'-', '.'})
        val = 0 # Use dataset to compute scores
        for word, count in words.items(): 
            val += dataset[word][MED_W_FREQ] * count
        scores.update({title: [round(val, 2), block]})
    # with open(f'{general["ROOT"]}data/{out_file}.json', 'w') as f: json.dump(scores, f)
    if default_order: return [(title, score) for title, score in scores.items()]

    # Sort and take top titles (we already take the top scored titles)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
    top_titles = [(title, score) for title, score in sorted_scores[:DEFAULT["N_TOP_TITLES"]]]
    return top_titles, titles, idx


def extract_section(file_path: str, start_title: str, titles: List[str], raws: List[str], unit: str='line', line_length: int = 100) -> str:
    text, sec_html = get_text(file_path)
    if not sec_html:
        i = titles.index(start_title)
        start_title = raws[i]
    
    start_index = text.find(start_title)
    text = text[start_index:]

    if unit == 'line':
        end_index = line_length * DEFAULT["MAX_SECT_SIZE"]
        return text[:end_index]
    
    elif unit == 'sentence':
        sentence_count, end_index = 0, 0
        for sentence in text.split(DELIM["SENTENCE"]):
            if re.match(R_SENTENCE, sentence): 
                sentence_count += 1
                end_index += len(sentence) + 1
            if sentence_count == DEFAULT["MAX_SECT_SIZE"]: break
        return text[:end_index]
    
    return None


# *********************
# HELPER FUNCTIONS
# *********************
def get_text(file_path: str) -> str:
    if file_path.endswith('.txt'): 
        txt = open(file_path, 'r').read()
        sec_html = True if "SEC_HTML" in txt[:100] else False
        txt = txt[DEFAULT["TOC_SKIP_CHARS"]:]
        i = txt.find("GRAPHIC")
        if i != -1: txt = txt[:i]
        return txt, sec_html

def get_title(section: str, dataset: pd.DataFrame) -> str | None:
    # Multiples rule are applied to filter out invalid titles
    # e.g., title length, punctuation, and structure
    section = section.strip()
    candidate_title = re.match(R_TITLE, section)
    if not candidate_title and section and section[-1] != '.':
        candidate_title = re.match(R_TITLE_FRAGMENT, section)
    # Return None if no title found
    if not candidate_title: return None
    # Title Filters
    title = candidate_title.group(0)
    if len(title.split(DELIM["WORD"])) > DEFAULT["MAX_LINE_SIZE"]: return None
    if title[-1] in {'.', ',', '-'}: return None
    candidate_title = re.match(R_NO_NUM, title.strip())

    # Remove special phrases before checking for repeated keywords
    title = section.lower()
    phrases = DEFAULT["SPECIAL_PHRASES"]
    for phrase in phrases:
        if phrase in title: title = title.replace(phrase, '')
    
    # Check for repeated keywords
    keywords = dataset.columns.values
    repeatable = DEFAULT["REPEATABLE_KEYWORDS"]
    for w in title.strip().split(DELIM["WORD"]):
        if title.count(w) == 1:         continue
        if w.lower() not in keywords:   continue
        if w.lower() not in repeatable: return None
    
    if candidate_title: return candidate_title.group(0)


# *********************
# ENTRY FUNCTIONS
# *********************
def extractor(file_path: str, test: bool=False, label: str='') -> float | None:
    try:
        candidate_titles, titles, raws = extract_titles(file_path)
        if not candidate_titles: 
            print(f"\033[91;1m{file_path.split('/')[-1]} \t ERROR\033[0m\t No candidate titles found")
            return None
    
        # Score the candidate titles and extract the best one, pick first index if tie
        _, candidate_index = max((ct[SCORE][0], -i) for i, ct in enumerate(candidate_titles))
        candidate_index = -candidate_index # Convert back to positive index

        # Extract the section of text between title and const
        ct = candidate_titles[candidate_index][TITLE]

        section = extract_section(file_path, ct, titles, raws, unit='line')

        # Write the extracted section to a file, and read test for comparison
        file = os.path.basename(file_path)[:-4]
        name = f'{file}_{label}.txt'
        label = pjoin(PATH['LABELS'], name)
        pred = pjoin(PATH['RESULTS'], name)
        open(pred, 'w').write(section)

        # if LOG_MODE:
        #     print(f"Input_File: {file}")
        #     print(f"File_Name:  {name}")
        #     print(f"Label:      {label}")
        #     print(f"Full_path:  {pred}\n")

        if not test: return
        # If the label does not exist, return
        if not os.path.exists(label): 
            print("ERROR - Label file not found")
            return

        # Compute and print similarity
        similarity = overlap_similarity(label, pred)
        score = round(similarity*100, 2)

        if score < DEFAULT["SUCCESS_THRESHOLD"]: 
            open(f"{PATH['ROOT'] / 'data' / 'fails.txt'}", 'a').write(f"{file}\t{score}\n")
        return score

    except Exception as e: 
        print(f"\033[91;1m{file[:-4]} \t ERROR\033[0m\t {e}")
        return None


# *********************
# MAIN FUNCTION
# *********************
args: argparse.Namespace

def extraction_entry(texts_path, label, exts=['.txt'], log=False, test=True):
    print("Extracting files...")
    # Setup and retrieve arguments
    global LOG_MODE
    LOG_MODE = log

    # Parse, prepare and retrieve files
    files = get_files(texts_path, label=label, exts=exts)
    # Extract, save, and compute similarity
    manager = Manager()
    result_scores = manager.list()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Errors are returned as None
        results = executor.map(extractor, files, [test]*len(files), [label]*len(files))
        result_scores.extend([r for r in results if r is not None and r != -100.00])

    # Convert to Series and compute metrics
    if not test: return
    print("Files: ", len(result_scores))
    result_scores = convert_to_series(result_scores)
    metrics(result_scores)

# *********************
# TEST FUNCTIONS
# *********************
@time_execution
def test(file: str):
    global LOG_MODE
    LOG_MODE = True

    r = extractor(file, test=True, label='Extracted')
    print(f"Score: {r}")


def test_title(title: str):
    keyword_dataset =  pd.read_json(f'{PATH['METRICS']}/agg_title_metrics.json')
    print(get_title(title, keyword_dataset))

if __name__ == "__main__":

    PATH['TEXTS'] = '/Users/sharjeelmustafa/Desktop/RA24_Testing/texts'
    PATH['LABELS'] = '/Users/sharjeelmustafa/Desktop/RA24_Testing/labels'
    name = "0000891804-11-003472"
    text_path = f"{PATH['TEXTS']}/{name}.txt"
    test(text_path)
    