import requests
import json
import pprint

conf = json.loads(open('rt_new_dvds.conf.json').read())

html = open('dvd-streaming-all').read()
text = html.split('var loadPage = (function').pop()
left = '[{"id":'
right = '}],\n'
middle = text.split(left).pop().split(right)[0]
text = (left + middle + right)[:-2]

movies = json.loads(text)
for movie in movies:
  print movie['url']
