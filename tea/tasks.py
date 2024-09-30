# First Party Imports
import os
import time
import zipfile

# Third Party Imports
from rq import get_current_job

# Local Imports
from .tea.params import PATH
from .tea.main import extract_text

CHUNK_SIZE = 20

# *********************
# TASK FUNCTIONS
# *********************
def text_extraction(unique_id, texts_path, labels_path, result_path, metric_path, word, exts):

    job = get_current_job()

    text_mask = [get_name(f) for f in get_files(texts_path)]
    labels = get_files(labels_path)
    
    results = []
    total_files = len(text_mask)  # Total number of text files
    for i in range(0, len(text_mask), CHUNK_SIZE):
        chunk = text_mask[i:i+CHUNK_SIZE]
        print(f"Chunk: {i} - {i+CHUNK_SIZE}")

        job.meta['progress'] = (i + len(chunk)) / total_files * 100
        job.save_meta()

        # Extract text
        extract_text(unique_id, word, chunk, ext=exts, log=False, test=True)

        # Save result files names
        results.extend([f"{f}_{word}.txt" for f in chunk])
        delete_files(chunk, texts_path)
    
    # Zip and return download link
    zipfile = zip_file(result_path, unique_id)

    # Delete remaining files
    print("Deleting files...")
    delete_files(results, result_path)
    delete_files(labels, labels_path)
    delete_files(['roi_dataset.csv', 'title_keywords.json'], metric_path)
    
    delete_folder(texts_path)
    delete_folder(labels_path)
    delete_folder(metric_path)
    print("Deleted")

    # Final progress
    job.meta['progress'] = 100
    job.save_meta()
    return zipfile

# *********************
# HELPER FUNCTIONS
# *********************
def get_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def get_files(path):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))    
    return files

def get_unique_user_path(base_path, unique_id: str):
    # Generate a unique folder name for each user session
    user_path = os.path.join(base_path, unique_id)
    os.makedirs(user_path, exist_ok=True)
    return user_path

def zip_file(path, unique_id):
    zip_filename = f"{unique_id}-results.zip"
    zip_path = os.path.join(path, zip_filename)
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(path):
        for file in files:
            if file == zip_filename: continue
            zipf.write(os.path.join(root, file), file)
    zipf.close()
    # url_for('main.download', filename=f'{id}-results.zip', unique_id=id)
    return zip_filename

def save_files(files, path, exts):
    if files is None: return -1
    for file in files:
        if os.path.splitext(file.filename)[1] not in exts: continue
        full_path = os.path.join(path, file.filename)
        open(full_path, 'w').write(file.read().decode('utf-8'))
    return 0

def delete_files(files, path):
    for file in files:
        file_name = file if isinstance(file, str) else file.filename
        file_path = os.path.join(path, file_name)
        if os.path.exists(file_path):
            os.remove(os.path.join(path, file_name))
        txt_file = os.path.splitext(file_path)[0] + '.txt'
        if os.path.exists(txt_file): os.remove(txt_file)
    return 0

def delete_folder(path):
    if os.path.isdir(path): os.rmdir(path)
    return 0