import redis
from rq import Queue
from flask import Flask, jsonify, send_from_directory, g, abort, request
import string_utils
import htmlizer
from requests_utils import get_remote_file
from werkzeug.utils import secure_filename
from flask_expects_json import expects_json
import time
import os
import config
from flask_limiter import Limiter
RATELIMIT_STORAGE_URL = config.REDIS_URL
redis_instance = redis.from_url(config.REDIS_URL)
queue = Queue('htmlizer', connection=redis_instance)
app = Flask(__name__)
app.config.from_object(__name__)



def get_token_from_header():
    s_token = request.headers.get('S-TOKEN', "00000000000000000000000000000000")
    ALLOWED_TOKEN = ['12345678123456781234567812345678'] #Just a test
    if isinstance(s_token, str) and s_token in ALLOWED_TOKEN:
        return s_token
    return "00000000000000000000000000000000"


limiter = Limiter(
    app,
    key_func=get_token_from_header,
)

htmlizer_schema = {
    'type': 'object',
    'properties': {
        'url': {'type': 'string'},
        'page': {'type': 'string'},
        'zoom_ratio': {'type': 'string'},
        'modified_time': {'type': 'integer'}
    },
    'required': ['url']
}


@app.route('/htmlizer', methods=['POST'])
@limiter.limit("60/minute")
@expects_json(htmlizer_schema)
def htmlizer_endpoint():
    remote_url = g.data['url']
    page = "1" if not 'page' in g.data else g.data['page']
    zoom_ratio = "1" if not 'zoom_ratio' in g.data else g.data['zoom_ratio']
    modified_time = 0 if not 'modified_time' in g.data else g.data['modified_time']

    if remote_url == "" or not remote_url.startswith("http"):
        return jsonify({"result": "failed", "code": "-05", "reason": "invalid url detected!"}), 500

    save_filename = os.path.join(config.WORKPLACE_DIR, string_utils.hash_filename(remote_url) + ".pdf")
    output_filename = string_utils.gen_random_string(16) + ".html"
    need_download = True
    last_save_time =  redis_instance.get(save_filename)
    if modified_time != 0 and last_save_time is not None and int(last_save_time) == modified_time:
        if os.path.exists(os.path.join(config.WORKPLACE_DIR, save_filename)):
            need_download = False

    if need_download:
        if not get_remote_file(remote_url, save_filename):
            return jsonify({"result": "failed", "code": "-06", "reason": "Unable to fetch remote file, either it is too large or unreachable!"}), 500
        redis_instance.set(save_filename, modified_time)


    job = queue.enqueue_call(htmlizer.convert_pdf_to_html, args=(save_filename, output_filename, page, zoom_ratio,),
                             timeout=config.TASK_TIMEOUT)

    wait_count = 0
    while job.result is None:
        time.sleep(config.TICKING_ACCURARCY)
        wait_count += 1
        if wait_count > config.TASK_TIMEOUT/config.TICKING_ACCURARCY:
            break

    if job.result is None:
        return jsonify({"result": "failed", "code": "-03", "reason": "task timeout"}), 500
    elif job.result == -1:
        return jsonify({"result": "failed", "code": "-04", "reason": "malformed pdf detected"}), 500
    else:
        return jsonify({"result": "okay", "code": "00", "url": output_filename})


@app.route('/<path:path>')
def serve_html(path):
    if path.endswith(".html"):
        return send_from_directory(config.WORKPLACE_DIR, secure_filename(path))
    return abort(404)


@app.route('/')
def hello_world():
    return jsonify({"result": "okay", "code": "00", "queue": len(queue)})



if __name__ == '__main__':
    app.run()
