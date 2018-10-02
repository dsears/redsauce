import pprint
import requests
import MySQLdb
import MySQLdb.cursors
import json
import os
import time
import sys
import BeautifulSoup

def q(s):
  return "'%s'" % MySQLdb.escape_string(str(s))

conf = json.loads(open('sync_omdb_rt.conf.json').read())
secrets_path = os.path.expanduser(conf['secrets_path'])
secrets = json.loads(open(secrets_path).read())

db = MySQLdb.connect(host='localhost', user='redsauce', db='redsauce', cursorclass=MySQLdb.cursors.DictCursor)
cursor = db.cursor()

get_next_imdb_sql = "SELECT * FROM `imdb` WHERE `processed_at` IS NULL ORDER BY `num_votes` DESC LIMIT 1"

def tconst_from_id(id):
  tconst = str(id)
  while len(tconst) < 7:
    tconst = '0%s' % tconst
  tconst = 'tt%s' % tconst
  return tconst

while True:

  cursor.execute(get_next_imdb_sql)
  imdb_row = cursor.fetchone()
  
  if not imdb_row:
    raise Exception("No more IMDB rows!")
  
  print "[%d] %d - %s" % (imdb_row['num_votes'], imdb_row['id'], imdb_row['primary_title'])
  
  tconst = tconst_from_id(imdb_row['id'])
  
  # Fetch OMDB JSON
  url = 'http://www.omdbapi.com/?i=%s&apikey=%s&tomatoes=true' % (tconst, secrets['omdb_api_key'])
  headers = {'User-Agent': conf['user_agent']}
  response = requests.get(url, headers=headers)
  assert response.status_code == 200
  omdb_json = response.json()
  assert omdb_json['Response'] == 'True'
  
  # Get Rotten Tomatoes data
  url = omdb_json['tomatoURL']
  headers = {'User-Agent': conf['user_agent']}
  response = requests.get(url, headers=headers)
  tomato_html = response.text
  soup = BeautifulSoup.BeautifulSoup(tomato_html)

  """
  jsonLdSchema = soup.find('script', {'id': 'jsonLdSchema'})
  print unicode(jsonLdSchema.text).encode('utf-8')
  jsonLdSchema = json.loads(jsonLdSchema.text)
  tomato_rating = jsonLdSchema['aggregateRating']['ratingValue']
  tomato_reviews = jsonLdSchema['aggregateRating']['reviewCount']
  """
  
  allCriticsNumbers = str(soup.find('div', {'id':'all-critics-numbers'}))
  tomato_rating = allCriticsNumbers.split('<span class="meter-value superPageFontColor"><span>')[1].split('</span>%</span>')[0]
  tomato_reviews = allCriticsNumbers.split('<span class="subtle superPageFontColor">Reviews Counted: </span><span>')[1].split('</span>')[0]
  
  tomato_id = tomato_html.split('mpscall["field[rtid]"]="')[1].split('"; // unique movie/show id')[0]
  
  # Create the meta row if it does not exist
  sql = "INSERT INTO `imdb_meta` (`id`) VALUES(%s) ON DUPLICATE KEY UPDATE `id`=`id`"
  sql = sql % q(imdb_row['id'])
  cursor.execute(sql)
  
  # Update the meta row
  sql = "UPDATE `imdb_meta` SET `omdb_json` = %s, `fetched_at` = NOW(), `tomato_id` = %s, `tomato_rating` = %s, `tomato_reviews` = %s WHERE `id` = %s LIMIT 1"
  sql = sql % (
               q(json.dumps(omdb_json)),
               q(tomato_id),
               q(tomato_rating),
               q(tomato_reviews),
               q(imdb_row['id'])
               )
  cursor.execute(sql)
  
  # Update the original IMDB row
  sql = "UPDATE `imdb` SET `processed_at` = NOW() WHERE `id` = %s LIMIT 1"
  sql = sql % (q(imdb_row['id']))
  cursor.execute(sql)
  
  # Sync the database
  db.commit()
  
  # Print a progress bar while we wait
  print '#' * conf['sleep_interval']
  for i in range(conf['sleep_interval']):
    time.sleep(1)
    sys.stdout.write('#')
  sys.stdout.write("\n")
  
  
