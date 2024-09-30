# First-party Imports
import re
import os

# Local Imports
from .params import PATH

R_SENTENCE = r"^(\w+\s\w+\s\w+\s?)((\w+|-)\s?)*"
TESTING = False

# *********************
# HELPER FUNCTIONS
# *********************
def get_text(file1: str, file2: str):
    try:
        text1 = open(file1, 'r').read()
        text2 = open(file2, 'r').read()
    except FileNotFoundError as e:
        print(f"ERROR - File not found: {e}")
        return -1
    return text1, text2

# *********************
# MAIN SIMILARITY METHOD
# *********************
def tokenize(text: str, unit: str=None):
    if unit == 'line':
        text = re.sub(r'[\n\t\r]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        chunks, n = [], 100
        for i in range(0, len(text), n):
            chunk = text[i:i+n]
            chunks.append(chunk)
        return chunks
    elif unit == 'sentence':
        text = re.sub(r'[\n\t\r]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        sentences = [sentence.strip() for sentence in text.split('.')]  # Strip each sentence
        return sentences
    return text.lower().split(' ')

def overlap_similarity(label: str, pred: str):
    
    ltext, ptext = get_text(label, pred)
    lwords = tokenize(ltext, "sentence")
    pwords = tokenize(ptext, "sentence")

    if TESTING:
        with open(f"{PATH['ROOT'] / 'data' / 'label.txt'}", 'w') as f:
            for w in lwords: f.write(w+'\n')
                
        with open(f"{PATH['ROOT'] / 'data' / 'pred.txt'}", 'w') as f:
            for w in pwords: f.write(w+'\n')

    lwords, pwords = set(lwords), set(pwords)
    intersection = len(lwords.intersection(pwords))
    return intersection / len(lwords)

# *********************
# ADDITIONAL METHODS
# *********************
def print_excess(label: str, pred: str):
        
        ltext, ptext = get_text(label, pred)
        lwords = tokenize(ltext, "sentence")
        pwords = tokenize(ptext, "sentence")
    
        for i, w in enumerate(pwords): 
            if w not in lwords[-3:-1]: continue
            print(f"End: {i:5}\tExcess: {len(pwords) - i:5}")
            break

def print_tokenization(lwords):
    print(f"Words-l: {len(lwords)}")
    for n, i in enumerate(lwords): print(f"{n:3}: {i[:64]}...")

if __name__ == "__main__":
    TESTING = True

    id = "0000891804-17-000679"
    label = f"/Users/sharjeelmustafa/Desktop/RA24_Testing/labels/{id}_Extracted.txt"
    pred = f"/Users/sharjeelmustafa/Documents/Academic/University/Research/SEM_8_Azi/text_analysis/tea/data/results/{id}_Extracted.txt"
    if not os.path.exists(label) or not os.path.exists(pred):
        print("ERROR - File not found")
        exit(-1)
    score = round(overlap_similarity(label, pred),2)
    print(score)