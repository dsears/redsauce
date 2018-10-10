import datetime
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import MySQLdb
import MySQLdb.cursors

conf = json.loads(open('rt_new_dvds.conf.json').read())
secrets_path = os.path.expanduser(conf['secrets_path'])
secrets = json.loads(open(secrets_path).read())

db = MySQLdb.connect(host='localhost', user='redsauce', db='redsauce', cursorclass=MySQLdb.cursors.DictCursor)
cursor = db.cursor()

sql = """select rt_dvd.title, rt_dvd.tomato_reviews, rt_dvd.tomato_rating, imdb.id, rt_dvd.handle from rt_dvd
left join imdb_meta on (rt_dvd.id = imdb_meta.tomato_id)
left join imdb on (imdb_meta.id = imdb.id)
where discovery_date > date_sub(curdate(), interval 1 week)
order by tomato_reviews desc"""

cursor.execute(sql)

html = []
for row in cursor.fetchall():
  if row['tomato_rating'] >= 60:
    color = 'red'
  else:
    color = 'green'
  
  if row['id']:
    url = secrets['imdb_url'] % row['id']
  else:
    url = 'https://www.rottentomatoes.com/m/%s' % row['handle']
  
  html.append('<p>')
  html.append('<div><a href="%s" style="text-decoration: none; font-family: sans-serif; color: %s; font-weight: bold;">%d%% - %s</a> (%d)</div>' % (url, color, row['tomato_rating'], row['title'], row['tomato_reviews']))
  html.append('</p>')

html = "\n".join(html)

# me == my email address
# you == recipient's email address
me = secrets['sender']
you = secrets['recipient']

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "New DVD releases - %s" % datetime.datetime.now().strftime("%b %d")
msg['From'] = me
msg['To'] = you

part1 = MIMEText(html, 'html')
msg.attach(part1)
s = smtplib.SMTP('localhost')
s.sendmail(me, you, msg.as_string())
s.quit()
