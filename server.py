
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
import random
from datetime import date
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://pam2203:8864@34.74.171.121/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()

conn.execute(text("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);"""))
conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

conn.commit() 

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query 
  #
  cursor = g.conn.execute(text("SELECT name FROM test;"))
  g.conn.commit()

  # 2 ways to get results

  # Indexing result by column number
  names = []
  for result in cursor:
    names.append(result[0])  

  # Indexing result by column name
#  names = []
#  results = cursor.mappings().all()
#  for result in results:
#    names.append(result["name"])
#  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
@app.route('/')
def home():
  return render_template("home.html")

@app.route('/home')
def home2():
  return redirect ('/')

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/resolve')
def resolve():
  return render_template("resolve.html")

@app.route('/landlord')
def landlord():
  return render_template("landlord.html")

@app.route('/report')
def report():
  return render_template("report.html")

@app.route('/submitted')
def submitted():
  return render_template("submitted.html")

@app.route('/resolve/enter')
def resolveLL(IssueCount):
  return render_template('resolve.html', IssueList = g.count)




# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add(): 
  name = request.form['name']
  params_dict = {"name":name}
  g.conn.execute(text('INSERT INTO test(name) VALUES (:name);'), params_dict)
  g.conn.commit()
  return redirect('/')

@app.route('/report', methods=['POST'])
def issue(): 
  desc = request.form['issueDesc']
  name = request.form['userName']
  floorRaw = request.form['userFloor']
  if not isinstance(floorRaw, int):
        return render_template('report.html', fail = "Please put a number as the floor")
  if not desc or not name or not floorRaw:
    return render_template('report.html', fail = "Please fill out all fields")
  floor = int(floorRaw)
  params_dict = {"desc":desc, "name":name, "floor":floor}
  cursor = g.conn.execute(text("SELECT unit_id FROM Units WHERE tenant = (:name) AND floor = (:floor);"), params_dict)
  g.conn.commit()
  unit = []
  for result in cursor:
    unit.append(result[0])
  if not unit:
    return render_template('report.html', fail = "Your unit could not be found, please try again")
  num_id = random.randint(15,1000)
  time = str(date.today())
  params_dict = {"num_id":num_id, "time":time, "desc":desc, "unit_id":unit[0]}
  g.conn.execute(text('INSERT INTO Issues(number_id, time, description) VALUES (:num_id,:time,:desc);'), params_dict)
  g.conn.commit()
  g.conn.execute(text('INSERT INTO ResidesBy(unit_id,number_id) VALUES (:unit_id,:num_id);'), params_dict)
  g.conn.commit()
  return redirect('/submitted')
x = True

@app.route('/landlord', methods=['POST'])
def research():
  name = request.form['llName']
  if not name:
    return render_template('landlord.html', fail = "Please enter a name")
  params_dict = {"name":name}
  cursor = g.conn.execute(text("SELECT COUNT(r.Unit_ID) FROM ResidesBy r JOIN Holds h ON r.Unit_ID = h.Unit_ID JOIN Landlord l ON l.Landlord_ID = h.Landlord_ID WHERE l.name = (:name);"), params_dict)
  g.conn.commit()
  count = []
  for result in cursor:
    count.append(result[0])
  if not count:
    return render_template('landlord.html', fail = "Your entry could not be found, please try again")
  cursor = g.conn.execute(text("SELECT COUNT(r.Landlord_ID) FROM Resolves r JOIN Landlord l ON l.Landlord_ID = r.Landlord_ID WHERE l.name = (:name);"), params_dict)
  g.conn.commit()
  count4 = []
  for result in cursor:
    count4.append(result[0])
  if not count4:
    return render_template('landlord.html', fail = "Your entry could not be found, please try again")
  return render_template('landlord.html', value = "This landlord has had " + str(count[0]) + " issue(s) across their owned properties.", value2="They have resolved "+str(count4[0])+" of them.")

landlordID = 0
@app.route('/resolve', methods=['POST'])
def fix():
  global x
  if x == True:
    count=[]
    name = request.form['llName']
    if not name:
      return render_template('resolve.html', fail = "Please enter a name")
    params_dict = {"name":name}
    cursor = g.conn.execute(text("SELECT r.number_ID FROM ResidesBy r JOIN Issues i ON r.number_ID = i.number_ID JOIN Holds h ON r.Unit_ID = h.Unit_ID JOIN Landlord l ON h.Landlord_ID = l.Landlord_ID WHERE l.name = (:name);"), params_dict)
    g.conn.commit()
    for result in cursor:
      count.append(result[0])
    if not count:
      return render_template('resolve.html', fail = "Your entry could not be found, please try again")
    count2 = []
    cursor = g.conn.execute(text("SELECT i.Description FROM ResidesBy r JOIN Issues i ON r.number_ID = i.number_ID JOIN Holds h ON r.Unit_ID = h.Unit_ID JOIN Landlord l ON h.Landlord_ID = l.Landlord_ID WHERE l.name = (:name);"), params_dict)
    g.conn.commit()
    for result in cursor:
      count2.append(result[0])
    x = False
    count3=[]
    cursor = g.conn.execute(text("SELECT l.Landlord_ID FROM Landlord l WHERE l.name = (:name);"), params_dict)
    g.conn.commit()
    for result in cursor:
      count3.append(result[0])
    global landlordID
    landlordID = count3[0]
    return render_template('resolve.html', IssueList = count, ProbList = count2, postName = name)
  else:
    x = True
    idRAW = request.form['resolve']
    if not idRAW:
      return render_template('resolve.html', IssueList = count, ProbList = count2, fail = "Please enter a number")
    num_id = int(idRAW)
    params_dict = {'num_id':num_id, 'll_id':landlordID}
    g.conn.execute(text('INSERT INTO Resolves(landlord_id, number_id) VALUES (:ll_id, :num_id);'), params_dict)
    g.conn.commit()
  return redirect('/submitted')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
