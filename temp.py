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

# Regex
rm_graphic = r"<DOCUMENT>\n?<TYPE>GRAPHIC(.*\n)*?<\/DOCUMENT>"
rm_table = r"<table(.|\n)*?</table>"
rm_extranl = r"\n{3,}"
rm_empty = r"^\s*$"
rm_spaces = r" {2,}"

# *********************
# PARSE FUNCTIONS
# *********************
def parse_html(file_path) -> str:
    file_path = rename_file_extension(file_path, '.txt')
    print(f"Processing: {file_path.split('/')[-1]}")

    output = ""
    text = open(file_path, 'r').read()

    # Preprocess the html
    text = re.sub(rm_graphic, "", text)
    text = re.sub(rm_table, "", text, flags=re.IGNORECASE)

    # HTML Parsing
    html = HTMLParser(text)
    html.unwrap_tags(['font', 'i', 'sub', 'b'])
    html = html.root.traverse()
    for node in html:
        tag = node.tag.lower()
        # Guard clause
        if tag not in {"p", "div"}: continue
        # Extract text based on tag
        if tag == "p": text = node.text()
        if tag == "div": text = node.text(deep=False)
        # Remove same paragraph breaks
        temp = text.replace("\n", " ")
        # Use unicode, e.g., \xa0 is the Unicode character for &nbsp;
        temp = temp.replace("\xa0", "\n")
        temp = temp.replace("\u2003", "  ")
        if len(temp) > 2: temp = temp.replace("\n", " ")
        output += temp.strip() + "\n"
    
    # Postprocess the output text
    output = re.sub(rm_extranl, "\n\n", output)
    output = re.sub(rm_empty, "", output, flags=re.MULTILINE)
    output = re.sub(rm_spaces, " ", output)

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
def rename_file_extension(file_path, ext):
    ext = ext if ext.startswith('.') else '.' + ext
    new_path = os.path.splitext(file_path)[0] + ext
    os.rename(file_path, new_path)
    return new_path


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
    parse_files(files, output_folder)


if __name__ == "__main__":
    input_folder = "/Users/sharjeelmustafa/Desktop/RA24_Testing/inputs"
    output_folder = "/Users/sharjeelmustafa/Desktop/RA24_Testing/outputs"
    main(input_folder, output_folder)