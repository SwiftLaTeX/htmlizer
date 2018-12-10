import requests

r = requests.post('http://127.0.0.1:5000/htmlizer', json={'url':"http://www.africau.edu/images/default/sample1.pdf"})
print(r.status_code)