# This is a mess.

import time
import MySQLdb
import MySQLdb.cursors
import BeautifulSoup
import requests
import json
import pprint
import datetime

def q(s):
  return "'%s'" % MySQLdb.escape_string(str(s))

db = MySQLdb.connect(host='localhost', user='redsauce', db='redsauce', cursorclass=MySQLdb.cursors.DictCursor)
cursor = db.cursor()

def find_closest_date(refdate, fmt="%b %-1d"):
  date_up = datetime.date.today()
  date_down = datetime.date.today()
  sanity = 400
  while True:
    if date_down.strftime(fmt) == refdate:
      return date_down
    if date_up.strftime(fmt) == refdate:
      return date_up
    date_down -= datetime.timedelta(days=1)
    date_up += datetime.timedelta(days=1)
    sanity -= 1
    assert sanity > 0

conf = json.loads(open('rt_new_dvds.conf.json').read())

url = 'https://www.rottentomatoes.com/browse/dvd-streaming-all'
headers = {'User-Agent': conf['user_agent']}
response = requests.get(url, headers=headers)
html = response.text

text = html.split('var loadPage = (function').pop()
left = '[{"id":'
right = '}],\n'
middle = text.split(left).pop().split(right)[0]
text = (left + middle + right)[:-2]

movies = json.loads(text)
for movie in movies:

  handle = movie['url'].split('/')[2]
  
  dvd_date = find_closest_date(movie['dvdReleaseDate'])
  discovery_date = datetime.date.today()
  
  # check if we already have it
  sql = "select id from rt_dvd where handle = %s" % q(handle)
  cursor.execute(sql)
  row = cursor.fetchone()
  if row:
    print 'already got', handle
    continue
  
  # Get Rotten Tomatoes data
  url = 'https://www.rottentomatoes.com/m/%s' % handle
  print 'Sleeping 5 and then fetching', url
  time.sleep(5)
  headers = {'User-Agent': conf['user_agent']}
  response = requests.get(url, headers=headers)
  tomato_html = response.text
  soup = BeautifulSoup.BeautifulSoup(unicode(tomato_html).encode('utf-8').decode('ascii', 'ignore'))
  
  allCriticsNumbers = str(soup.find('div', {'id':'all-critics-numbers'}))

  try:
    tomato_rating = allCriticsNumbers.split('<span class="meter-value superPageFontColor"><span>')[1].split('</span>%</span>')[0]
  except:
    tomato_rating = 0

  try:
    tomato_reviews = allCriticsNumbers.split('<span class="subtle superPageFontColor">Reviews Counted: </span><span>')[1].split('</span>')[0]
  except:
    tomato_reviews = 0
  
  try:
    tomato_id = tomato_html.split('mpscall["field[rtid]"]="')[1].split('"; // unique movie/show id')[0]
  except:
    tomato_id = 0
  
  sql = "insert into rt_dvd (id, title, handle, dvd_date, discovery_date, tomato_rating, tomato_reviews) values (%s, %s, %s, %s, %s, %s, %s)"
  sql = sql % (q(tomato_id), q(movie['title']), q(handle), q(dvd_date), q(discovery_date), q(tomato_rating), q(tomato_reviews))
  cursor.execute(sql)
  db.commit()
