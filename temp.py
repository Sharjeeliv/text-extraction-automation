# First Party
import os
import time
import re

# Third Party
from selectolax.parser import HTMLParser


# *********************
# CONST & VARIABLES
# *********************
N_TOP_HTML_CHARS =  2325

# *********************
# PARSE FUNCTIONS
# *********************
def parse_html(file_path) -> str:
    with open(file_path, 'r') as f:
        text = f.read()
        output = ""
        for node in HTMLParser(text).root.traverse():
            print(node.tag)

    return output


def parse_text(file_path)-> str:
    with open(file_path, 'r') as f: text = f.read()
    return text


def parse_files(files, output_folder):
    for file in files:
        text = "None"
        if is_html(file):   text = parse_html(file)
        else:               text = parse_text(file)

        # Write to output file
        full_name = os.path.basename(file)
        file_name = os.path.splitext(full_name)[0]
        output_file = os.path.join(output_folder, f"{file_name}.txt")
        with open(output_file, 'w') as f: f.write(text)


# *********************
# HELPER FUNCTIONS
# *********************
def time_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        m, s = divmod(execution_time, 60)
        ms = (execution_time - int(execution_time)) * 1000
        print(f"\033[91;1mEXECUTION TIME: {int(m):02}:{int(s):02}.{int(ms):03}\033[0m")
        return result
    return wrapper


def is_html(path):
    with open(path, 'r') as f: 
        data = f.read(N_TOP_HTML_CHARS).lower()
        if data.find('<html>') != -1: return True
    return False


def get_files(path, exts):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(tuple(exts)):
                files.append(os.path.join(root, filename))
    return files

@time_execution
def main(input_folder, output_folder):
    files = get_files(input_folder, ['.txt', '.html', '.htm'])
    parse_files(files[:2], output_folder)


if __name__ == "__main__":
    input_folder = "/Users/sharjeelmustafa/Desktop/inputs"
    output_folder = "/Users/sharjeelmustafa/Desktop/outputs"
    main(input_folder, output_folder)