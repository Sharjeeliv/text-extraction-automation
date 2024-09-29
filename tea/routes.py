from flask import Blueprint, render_template, request, send_from_directory, url_for, flash
from .tea.params import PATH
from .tea.main import extract_text
import os
import zipfile
import time

main = Blueprint('main', __name__)

@main.route("/info", methods=['GET', 'POST'])
def info():
    return render_template('info.html')

@main.route("/", methods=['GET', 'POST'])
def tea():
    # Retrieve user inputs
    texts   = request.files.getlist('texts[]')
    labels  = request.files.getlist('labels[]')
    word    = request.form.get('label_word')
    exts    = request.form.get('extensions')
    exts    = exts.split(' ') if exts else []
    submit  = request.form.get('submit')


    print(len(texts), len(labels), word, exts)
    # Guard Clauses
    if submit is None:                                  return render_template('interface.html')
    if not validated_inputs(texts, labels, word, exts): return render_template('interface.html')

    # Generate unique user paths
    unique_id = str(time.time()).replace('.', '')
    texts_path = get_unique_user_path(PATH['TEXTS'], unique_id)
    labels_path = get_unique_user_path(PATH['LABELS'], unique_id)
    result_path = get_unique_user_path(PATH['RESULTS'], unique_id)
    metric_path = get_unique_user_path(PATH['METRICS'], unique_id)

    print(f"Unique ID: {unique_id}")
    print(f"Texts Path: {texts_path}")
    print(f"Labels Path: {labels_path}")
    print(f"Results Path: {result_path}")
    print(f"Metrics Path: {metric_path}")

    # Saves labels to avoid multiple uploads
    save_files(labels, labels_path, exts)
    results = []
    for i in range(0, len(texts), 100):
        chunk = texts[i:i+100]
        print(f"Chunk: {i} - {i+100}")
        # Save texts in chunks since it can be large
        save_files(chunk, texts_path, exts)
        extract_text(unique_id, word, ext=exts, log=False, test=True)

        # Save result files names
        results.extend([f"{f.filename.split('.')[0]}_{word}.txt" for f in chunk])
        delete_files(texts, texts_path)
    
    # Delete remaining files
    print(len(results))
    delete_files(results, result_path)
    delete_files(labels, labels_path)
    delete_files(['roi_dataset.csv', 'title_keywords.json'], metric_path)
    delete_folder(texts_path)
    delete_folder(labels_path)
    delete_folder(metric_path)
    delete_folder(result_path)

    flash("Completed", 'success')

    return render_template('interface.html')

@main.route("/download/<filename>")
def download(filename):
    return send_from_directory(PATH['RESULTS'], filename, as_attachment=True)

# *********************
# HELPER FUNCTIONS
# *********************
def validated_inputs(texts, labels, word, exts):
    if len(texts) == 0:
        flash("Please provide a texts folder", 'danger')
        return False
    if len(labels) == 0:
        flash("Please provide a labels folder", 'danger')
        return False
    if len(exts) == 0:
        flash("Please provide at least one allowed extension", 'danger')
        return False
    if not word:
        flash("Please provide the label suffix word", 'warning')
        return False
    return True

def get_unique_user_path(base_path, unique_id: str):
    # Generate a unique folder name for each user session
    user_path = os.path.join(base_path, unique_id)
    os.makedirs(user_path, exist_ok=True)
    return user_path

def zip_file():
    zipf = zipfile.ZipFile('results.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(PATH['RESULTS']):
        for file in files: zipf.write(os.path.join(root, file), file)
    zipf.close()
    return url_for('main.download', filename='results.zip')

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