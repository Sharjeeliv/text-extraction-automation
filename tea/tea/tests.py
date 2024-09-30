import re
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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


# *********************
# TOKEN BASED METHODS
# *********************
def jaccard_similarity(label: str, pred: str):
    
    text1, text2 = get_text(label, pred)
    words1 = set(text1.lower().split(' '))
    words2 = set(text2.lower().split(' '))

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union

def sorenson_dice_similarity(label: str, pred: str):

    text1, text2 = get_text(label, pred)
    words1 = set(text1.lower().split(' '))
    words2 = set(text2.lower().split(' '))

    intersection = len(words1.intersection(words2))
    return 2 * intersection / (len(words1) + len(words2))

def cos_similarity(label: str, pred: str):
    
    text1, text2 = get_text(label, pred)
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf)[0][1]

def ngram_similarity(label: str, pred: str, n: int=3):
    
    text1, text2 = get_text(label, pred)
    ngram1 = [text1[i:i+n] for i in range(len(text1)-n+1)]
    ngram2 = [text2[i:i+n] for i in range(len(text2)-n+1)]
    
    intersection = len(set(ngram1).intersection(set(ngram2)))
    union = len(set(ngram1).union(set(ngram2)))
    return intersection / union

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