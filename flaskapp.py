import sqlite3

from flask import Flask, request, g, render_template, send_file

DATABASE = '/var/www/html/flaskapp/natlpark.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    print(query)
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    print("commited")
    get_db().commit()

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    print(request.form)
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        username = str(request.form['username'])
        password = str(request.form['password'])
        result = execute_query("""SELECT firstname,lastname,email,count  FROM natlpark WHERE username  = (?) AND password = (?)""", (username, password, ))
        if result:
            for row in result:
                return responsePage(row[0], row[1], row[2], row[3])
        else:
            message = 'Invalid Credentials !'
    elif request.method == 'POST':
        message = 'Please enter Credentials'
    return render_template('login.html', message = message)

@app.route('/registration', methods =['POST', 'GET'])
def registration():
    #resp = request.post(url, headers=headers)

    print(request.form)
    message = ''
    if request.method == 'POST' and str(request.form.get('username')) !="" and str(request.form.get('password')) !="" and str(request.form.get('firstname')) !="" and str(request.form.get('lastname')) !="" and str(request.form.get('email')) !="":
        username = str(request.form.get('username'))
        print(username)
        password = str(request.form.get('password'))
        print(password)
        firstname = str(request.form.get('firstname'))
        print(firstname)
        lastname = str(request.form.get('lastname'))
        print(lastname)
        email = str(request.form.get('email'))
        print(email)
        uploaded_file = request.files['textfile']
        print(str(uploaded_file))
        if not uploaded_file:
            filename = "null"
            print("inside word count")
            word_count = int(0)
        else :
            filename = uploaded_file.filename
            word_count = getNumberOfWords(uploaded_file)
        result = execute_query("""SELECT *  FROM natlpark WHERE username  = (?)""", (username, ))
        if result:
            message = 'User has already registered!'
        else:
            result1 = execute_query("""INSERT INTO natlpark (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, word_count, ))
            commit()
            result2 = execute_query("""SELECT firstname,lastname,email,count  FROM natlpark WHERE username  = (?) AND password = (?)""", (username, password, ))
            if result2:
                for row in result2:
                    return responsePage(row[0], row[1], row[2], row[3])
    elif request.method == 'POST':
        message = 'Some of the fields are missing!'
    return render_template('reg.html', message = message)

@app.route("/download")
def download():
    path = "Limerick.txt"
    return render_template('download.html', send_file(path, as_attachment=True))

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return int(len(words))

def responsePage(firstname, lastname, email, count):
    return """ First Name :  """ + str(firstname) + """ <br> Last Name : """ + str(lastname) + """ <br> Email : """ + str(email) + """ <br> Word Count : """ + str(count) + """ <br><br> <a href="/download" >Download</a><br><br><a href="/">Log out</a> """

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT * FROM natlpark""")
    return '<br>'.join(str(row) for row in rows)

if __name__ == '__main__':
  app.run(debug=True)
