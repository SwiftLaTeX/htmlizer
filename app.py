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
from flask_cors import cross_origin
RATELIMIT_STORAGE_URL = config.REDIS_URL
redis_instance = redis.from_url(config.REDIS_URL)
queue = Queue('htmlizer', connection=redis_instance)
app = Flask(__name__)
app.config.from_object(__name__)

def share_key_func():
    return "guest"


limiter = Limiter(
    app,
    key_func=share_key_func,
)

@limiter.request_filter
def verify_token():
    s_token = request.headers.get('S-TOKEN', "00000000000000000000000000000000")
    if isinstance(s_token, str) and s_token == config.APIKEY:
        return True
    return False


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
@limiter.limit("30/minute")
@expects_json(htmlizer_schema)
def htmlizer_endpoint():
    remote_url = g.data['url']
    page = "1" if not 'page' in g.data else g.data['page']
    zoom_ratio = "1" if not 'zoom_ratio' in g.data else g.data['zoom_ratio']
    modified_time = 0 if not 'modified_time' in g.data else g.data['modified_time']

    if remote_url == "" or not remote_url.startswith("http"):
        return jsonify({"result": "failed", "code": "-05", "reason": "invalid url detected!"}), 500

    cache_key = remote_url
    random_str = string_utils.gen_random_string(16)

    if modified_time != 0: #We could check whether there is cache result
        last_save_time_byte = redis_instance.get(cache_key + ".time")
        last_save_name_byte = redis_instance.get(cache_key + ".name")
        print("Checking %s result %s %s" % (cache_key, last_save_name_byte, last_save_name_byte))
        if last_save_time_byte is not None and last_save_name_byte is not None \
                and int(last_save_time_byte) == modified_time:
            last_save_name_str = last_save_name_byte.decode('utf-8')
            last_output_name_str = "%s%s.html" % (last_save_name_str, page)
            if os.path.exists(os.path.join(config.WORKPLACE_DIR, last_output_name_str)):
                return jsonify({"result": "okay", "code": "01", "url": last_output_name_str})
            else:
                random_str = last_save_name_str #//We can still reuse it!

    #random_str = string_utils.gen_random_string(16)
    save_filename = os.path.join(config.WORKPLACE_DIR, random_str + ".pdf")
    output_filename = "%s%s.html" % (random_str, page)


    if not get_remote_file(remote_url, save_filename):
        return jsonify({"result": "failed", "code": "-06", "reason": "Unable to fetch remote file, either it is too large or unreachable!"}), 500


    job = queue.enqueue_call(htmlizer.convert_pdf_to_html, args=(save_filename, output_filename, page, zoom_ratio,),
                             timeout=config.TASK_TIMEOUT)

    wait_count = 0
    while job.result is None:
        time.sleep(config.TICKING_ACCURARCY)
        wait_count += 1
        if wait_count > config.TASK_TIMEOUT/config.TICKING_ACCURARCY:
            break

    redis_instance.set(cache_key + ".time", modified_time)
    redis_instance.set(cache_key + ".name", random_str)

    if job.result is None:
        return jsonify({"result": "failed", "code": "-03", "reason": "task timeout"}), 500
    elif job.result == -1:
        return jsonify({"result": "failed", "code": "-04", "reason": "malformed pdf detected"}), 500
    else:
        return jsonify({"result": "okay", "code": "00", "url": output_filename})


@app.route('/<path:path>')
@cross_origin()
def serve_html(path):
    if path.endswith(".html"):
        return send_from_directory(config.WORKPLACE_DIR, secure_filename(path))
    return abort(404)


@app.route('/font/<string:fontname>')
@cross_origin()
def serve_font(fontname):
    if "+" in fontname:
        fontname = fontname.split("+")[1]
    fontname = fontname.lower()
    files = os.listdir(config.FONT_DIR)
    for f in files:
        if fontname == f.lower():
            return send_from_directory(config.FONT_DIR, f)
    return send_from_directory(config.FONT_DIR, "default.ttf")


@app.route('/')
def hello_world():
    return jsonify({"result": "okay", "code": "00", "queue": len(queue)})



if __name__ == '__main__':
    app.run()
