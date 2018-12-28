import requests
import time
start = time.time()
r = requests.post('http://130.216.216.72/htmlizer', json={'url':"http://gahp.net/wp-content/uploads/2017/09/sample.pdf", "modified_time":13000})
print(r.status_code)
print(r.text)
stop = time.time()
print(stop - start)