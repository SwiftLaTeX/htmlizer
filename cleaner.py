import os, time, config

while True:
    time.sleep(3600)
    now = time.time()
    cutoff = now - (config.FILE_STORAGE_TIME)
    files = os.listdir(config.WORKPLACE_DIR)
    for xfile in files:
        targetF = os.path.join(config.WORKPLACE_DIR, xfile)
        if os.path.isfile(targetF):
            t = os.stat(targetF)
            c = t.st_ctime
            if c < cutoff:
                os.unlink(targetF)
                print("Removing %s" % targetF)