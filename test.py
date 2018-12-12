import requests

r = requests.post('http://127.0.0.1:5001/htmlizer', json={'url':"http://www.africau.edu/images/default/sample.pdf", "modified_time":1300})
print(r.status_code)
print(r.text)