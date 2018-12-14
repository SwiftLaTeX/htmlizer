import requests

r = requests.post('http://130.216.216.72/htmlizer', json={'url':"http://www.africau.edu/images/default/sample.pdf", "modified_time":1300})
print(r.status_code)
print(r.text)