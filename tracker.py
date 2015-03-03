import datetime
import sqlite3
import time
from flask import Flask, g, render_template

# Flask configuration.
class DevConfig(object):
  DATABASE = '/home/piotrf/projects/tracker/test.db'
  DEBUG = True
  SECRET_KEY = 'development key'
  USERNAME = 'admin'
  PASSWORD = 'default'

  
# Create our flask app.
app = Flask(__name__)
app.config.from_object(DevConfig)


# Timer configuration.
# List of tuples (name, time budgeted (in seconds))
TIMERS = [
  ('LANGUAGE', 16 * 60 * 60),
  ('INFRASTRUCTURE', 2 * 60 * 60),
  ('PHYSICAL', 8 * 60 * 60),
  ('EDUCATION', 2 * 60 * 60),
  ('PROJECTS', 4 * 60 * 60),
  ('MUSIC', 2 * 60 * 60),
]


# Connect to our configured sqlite3 database.
def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
  g.db = connect_db()
    
@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()


def beginning_of_week():
  """Returns beginning of this week as unix time."""
  today = datetime.date.today()
  bow = today - datetime.timedelta(today.weekday())
  bow = datetime.datetime.combine(bow, datetime.datetime.min.time())
  return int((bow - datetime.datetime.utcfromtimestamp(0)).total_seconds())

  
@app.route("/")
def index():
  now = int(time.time())
  bow = beginning_of_week()
  cur = g.db.execute('select * from timers where time > (?)', (str(bow),))
  events = dict((timer[0], []) for timer in TIMERS)
  for row in cur.fetchall():
    timestamp, name, event = row
    events[name].append((timestamp, event))
  timers = []
  for timer_name, budgeted_time in TIMERS:
    current_time = 0
    total_time = 0
    start_time = 0
    running = False
    for event in events[timer_name]:
      if event[1] == 'start':
        start_time = event[0]
      elif event[1] == 'stop':
        # We can possibly have timers that cross the beginning of week boundary.
        if start_time == 0:
          start_time = bow
        total_time += event[0] - start_time
        start_time = 0
    if start_time > 0:
      current_time = now - start_time
      total_time += current_time
      running = True
    timers.append({'name': timer_name, 
                   'current': current_time,
                   'total': total_time, 
                   'budgeted': budgeted_time,
                   'running': running,
                   'start': start_time})
  return render_template('index.html', timers=timers)


@app.route("/start/<timer_name>")
def start(timer_name):
  now = int(time.time())
  g.db.execute('insert into timers (time, name, event) values(?, ?, ?)',
               [now, timer_name, 'start'])
  g.db.commit()
  return ''


@app.route("/stop/<timer_name>")
def stop(timer_name):
  now = int(time.time())
  g.db.execute('insert into timers (time, name, event) values(?, ?, ?)',
               [now, timer_name, 'stop'])
  g.db.commit()
  return ''


if __name__ == "__main__":
  app.run()
