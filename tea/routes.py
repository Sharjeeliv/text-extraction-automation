# First Party
import os
import zipfile
import time

# Third Party
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import jsonify, send_from_directory, after_this_request
import redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

# local
from .tea.params import PATH
from .tasks import text_extraction, delete_files, delete_folder


# *********************
# SETUP & CONFIG
# *********************
main = Blueprint('main', __name__)
r = redis.Redis(host='redis')
q = Queue(connection=r, default_timeout=3600)

# *********************
# GENERIC ROUTES
# *********************
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

    # Guard Clauses
    print(len(texts), len(labels), word, exts)
    if submit is None:                                  return render_template('interface.html')
    if not validated_inputs(texts, labels, word, exts): return render_template('interface.html')

    # Saves Files & Generates Unique ID
    unique_id = str(time.time()).replace('.', '')
    texts_path = get_unique_user_path(PATH['TEXTS'], unique_id)
    labels_path = get_unique_user_path(PATH['LABELS'], unique_id)
    result_path = get_unique_user_path(PATH['RESULTS'], unique_id)
    metric_path = get_unique_user_path(PATH['METRICS'], unique_id)

    save_files(labels, labels_path, exts)
    save_files(texts, texts_path, exts)

    job = q.enqueue(text_extraction, unique_id, texts_path, labels_path, result_path, metric_path, word, exts)
    return redirect(url_for('main.progress', job_id=job.get_id()))
    # return redirect(url_for('main.download', filename=zipfile, unique_id=unique_id))


# *********************
# PROGRESS ROUTES
# *********************
@main.route('/progress/<job_id>')
def progress(job_id):
    print("Activated progress", job_id)
    return render_template('progress.html', job_id=job_id)

@main.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    print("Activated jobstatus", job_id)
    try: job = Job.fetch(job_id, connection=r)
    except NoSuchJobError: return jsonify({'status': 'unknown'})
     
    if job.is_finished:
        # Assuming job.result contains the URL to the PDF
        return jsonify({'status': 'finished', 'result': job.result})
    elif job.is_queued:
        return jsonify({'status': 'queued'})
    elif job.is_started:
        progress = job.meta.get('progress', 0)
        return jsonify({'status': 'started', 'progress': progress})
    elif job.is_failed:
        return jsonify({'status': 'failed'})
    else:
        return jsonify({'status': 'unknown'})

@main.route("/download/<filename>")
def download(filename):
    unique_id = filename.split('-')[0]
    result_path = os.path.join(PATH['RESULTS'], unique_id)
    # Delete files after download
    @after_this_request
    def delete_result(response):
        try:
            delete_files([filename], result_path)
            delete_folder(result_path)
        except Exception as error:
            print("Error removing or closing downloaded file", error)
        return response

    return send_from_directory(result_path, filename, as_attachment=True)

@main.route('/cancel-job/<job_id>', methods=['POST'])
def cancel_job(job_id):
    job = Job.fetch(job_id, connection=r)
    job.cancel()
    return jsonify({'status': 'canceled'})


# # *********************
# # HELPER FUNCTIONS
# # *********************

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
    total_size = sum(f.content_length for f in texts + labels)
    if total_size > 512_000_000:
        flash("Total file size exceeds 512MB, must be smaller", 'danger')
        return False
    return True

def get_unique_user_path(base_path, unique_id: str):
    # Generate a unique folder name for each user session
    user_path = os.path.join(base_path, unique_id)
    os.makedirs(user_path, exist_ok=True)
    return user_path

# def zip_file(path, unique_id):
#     zip_filename = f"{unique_id}-results.zip"
#     zip_path = os.path.join(path, zip_filename)
#     zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
#     for root, _, files in os.walk(path):
#         for file in files:
#             if file == zip_filename: continue
#             zipf.write(os.path.join(root, file), file)
#     zipf.close()
#     # url_for('main.download', filename=f'{id}-results.zip', unique_id=id)
#     return zip_filename

def save_files(files, path, exts):
    if files is None: return -1
    for file in files:
        if os.path.splitext(file.filename)[1] not in exts: continue
        full_path = os.path.join(path, file.filename)
        open(full_path, 'w').write(file.read().decode('utf-8'))
    return 0

# def delete_files(files, path):
#     for file in files:
#         file_name = file if isinstance(file, str) else file.filename
#         file_path = os.path.join(path, file_name)
#         if os.path.exists(file_path):
#             os.remove(os.path.join(path, file_name))
#         txt_file = os.path.splitext(file_path)[0] + '.txt'
#         if os.path.exists(txt_file): os.remove(txt_file)
#     return 0

# def delete_folder(path):
#     if os.path.isdir(path): os.rmdir(path)
#     return 0