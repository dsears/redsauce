import json
import MySQLdb

def q(s):
  return "'%s'" % MySQLdb.escape_string(str(s))

def id_from_tconst(tconst):
  return int(tconst[2:])

conf = json.loads(open('sync_imdb.conf.json').read())

db = MySQLdb.connect(host='localhost', user='redsauce', db='redsauce')
cursor = db.cursor()

# Insert or update query
sql_fmt = """
INSERT INTO `imdb`
(`id`, `primary_title`, `year`, `runtime_minutes`, `genres`, `avg_rating`, `num_votes`)
VALUES
(%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
`primary_title` = %s,
`year` = %s,
`runtime_minutes` = %s,
`genres` = %s,
`avg_rating` = %s,
`num_votes` = %s
"""

# Load in ratings
ratings = {}
with open('title.ratings.tsv') as file:
  headers = file.readline().strip().split("\t")
  for line in file:
    values = line.strip().split("\t")
    row = dict(zip(headers, values))
    row['numVotes'] = int(row['numVotes'])
    if row['numVotes'] < conf['minimumVotes']:
      continue
    id = id_from_tconst(row['tconst'])
    row['averageRating'] = int(float(row['averageRating']) * 10)
    ratings[id] = row

# Iterate titles and update the database
with open('title.basics.tsv') as file:
  headers = file.readline().strip().split("\t")
  for line in file:
    values = line.strip().split("\t")
    row = dict(zip(headers, values))
    if row['titleType'] not in conf['validTitleTypes']:
      continue
    id = id_from_tconst(row['tconst'])
    if id not in ratings:
      continue
    genres = ', '.join(row['genres'].split(','))
    rating = ratings[id]
    try:
      runtimeMinutes = int(row['runtimeMinutes'])
    except:
      runtimeMinutes = 0
    sql = sql_fmt % (q(id),
                     q(row['primaryTitle']),
                     q(row['startYear']),
                     q(runtimeMinutes),
                     q(genres),
                     q(rating['averageRating']),
                     q(rating['numVotes']),
                     q(row['primaryTitle']),
                     q(row['startYear']),
                     q(runtimeMinutes),
                     q(genres),
                     q(rating['averageRating']),
                     q(rating['numVotes'])                     
                     )
    cursor.execute(sql)

db.commit()
