# A simplified and more logical parse layer
# Designed for extension to other file types
import os
from typing import List
from concurrent.futures import ProcessPoolExecutor
import re

# HTML Parsing
from lxml.html import fromstring

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager

from params import PATH, DEFAULT
from utils import time_execution


# *********************
# SETUP & DEFAULTS
# *********************
options = Options()
options.add_argument('--headless=new')


# *********************
# HTML-PARSE FUNCTIONS
# *********************
def parse_html(file_path: str):
    driver_cache_manager = DriverCacheManager(root_dir=PATH['DRIVER'])
    service = Service(ChromeDriverManager(cache_manager=driver_cache_manager).install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(f'file://{file_path}')
        extracted_text = driver.find_element(By.TAG_NAME, 'body').text
    finally:
        driver.close()
        return extracted_text


def is_html(file_path: str):
    # Check file extension
    _, file_extesion = os.path.splitext(file_path)
    if file_extesion in ('.htm', '.html'): return True
    with open(file_path, 'r') as f:
        text = f.read(DEFAULT["N_TOP_HTML_CHARS"]).lower()
        return '<html>' in text

def fix_html_extension(file_path: str):
    path = os.path.dirname(file_path)
    file = os.path.basename(file_path)
    name = get_filename(file_path)
    old_path = os.path.join(path, file)
    new_path = os.path.join(path, f"{name}.htm")
    try: os.rename(old_path, new_path)
    except FileNotFoundError:   print(f"\nERROR - Failure Renaming\n{old_path} to\n{new_path}")
    return new_path

# *********************
# PARSE FUNCTIONS
# *********************
def parse(file_path: str):
    try:
        text = "None"
        print(f"Processing {get_filename(file_path)}")
        # Guard Clause: Parsed file already exists
        tmp_path = os.path.join(PATH['TEXTS'], f"{get_filename(file_path)}.txt")
        if os.path.exists(tmp_path): return file_path

        # Expand with other file types
        if file_path.endswith('.htm'): text = parse_html(file_path)
        if file_path.endswith('.txt'): text = open(file_path, 'r').read()

        # Create a corresponding text file and dump content
        name = get_filename(file_path)
        path = os.path.join(PATH['TEXTS'], f"{name}.txt")
        with open(path, 'w') as f: f.write(text)
        return file_path
    
    except Exception as e:
        print(f"ERROR - processing failure {file_path}: {e}")
        return -1


def parse_executor(file_paths: List[str]):
    with ProcessPoolExecutor() as executor: 
        results = executor.map(parse, file_paths)
    results = [i for i in results if i != -1]
    redos = set(file_paths) - set(results)
    return redos


def parse_files(file_paths: List[str]):
    files = file_paths
    # while files:
    redos = parse_executor(files)
    files = list(redos)
    print(f"Redoing {len(redos)} files")
    print(f"Processed {len(file_paths)-len(redos)} files")

    
# *********************
# HELPER FUNCTIONS
# *********************
def get_files(path: str, exclude=[], ext=[]) -> List[str]:
    files = []
    for file in os.listdir(path):
        if len(exclude)!= 0 and any(i in file for i in exclude):    continue
        if not os.path.isfile(os.path.join(path, file)):            continue
        if len(ext)!= 0 and not any(file.endswith(i) for i in ext): continue
        files.append(file)
    return files

def prepare_files(files: List[str], path: str) -> List[str]:
    prepared_files = []
    for file in files:
        file_path = os.path.join(path, file)
        # Expand with other file types
        if is_html(file_path): file_path = fix_html_extension(file_path)
        prepared_files.append(file_path)
    return prepared_files

def get_filename(path: str):
    file = os.path.basename(path)
    name, _ = os.path.splitext(file)
    return name


# *********************
# MAIN FUNCTIONS
# *********************
@time_execution
def parse_entry(path:str, exclude=[], ext=[]):
    files = get_files(path, exclude=exclude, ext=ext)
    print(f"Files: {len(files)}")
    # Fix ext, concats full paths
    file_paths = prepare_files(files, path) 
    parse_files(file_paths)

if __name__ == "__main__":
    # path = "/Users/sharjeelmustafa/Documents/02_Work/01_Research/SEM_8_Azi/text_analysis/data/texts"
    # test = "/Users/sharjeelmustafa/Documents/02_Work/01_Research/SEM_8_Azi/text_analysis/data/test"
    # test = "/Users/sharjeelmustafa/Documents/02_Work/01_Research/SEM_8_Azi/text_analysis/test/test_3"
    test = "/Users/sharjeelmustafa/Documents/02_Work/01_Research/SEM_8_Azi/text_analysis/test/Mahmood - Manual Attempt/Done"
    parse_entry(path=test, exclude=["Extracted"], ext=[".txt", ".htm", ".html"])
    