import config
import subprocess
import time
import logging


def convert_pdf_to_html(input_file, output_file, page, zoom_ratio = 2):
    cmd = ["pdf2htmlEX", "--zoom", str(zoom_ratio), "--decompose-ligature", "1",
               "--embed-javascript", "0", "--data-dir", config.PDF2HTMLEX_ASSETS_URL, "-f",
               str(page), "-l",
               str(page), input_file, output_file]

    logging.debug("A task received %s" % (cmd))

    pro = subprocess.Popen(cmd, cwd=config.WORKPLACE_DIR)
    wait_count = 0
    r = None
    finished = False
    while wait_count <= int(config.TASK_TIMEOUT / config.TICKING_ACCURARCY):
        wait_count += 1
        time.sleep(config.TICKING_ACCURARCY)
        r = pro.poll()
        if r is not None:
            finished = True
            break

    if not finished:
        pro.terminate()


    if r != 0:
        logging.error("Task failed, filename %s" % input_file)
        return -1
    else:
        return 0
