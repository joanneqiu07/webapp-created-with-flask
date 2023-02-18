from flask import Flask
from flask import render_template, g, request
import sqlite3

app = Flask(__name__)


def get_message_db():
    '''
    Get or create a database of messages
    '''

    # Check whether there is a database called message_db in the g attribute of the app
    try:
        return g.message_db
    except: # If not, then connect to the database
        g.message_db = sqlite3.connect("messages_db.sqlite") 
        
        # Check whether a table called messages exists in message_db, 
        # and create it if not
        cmd = \
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                handle TEXT NOT NULL)
            """
        cursor = g.message_db.cursor()
        cursor.execute(cmd)
        return g.message_db


def insert_message(request):
    '''
    Inserts a user message into the database of messages.
    '''

    # Extract the message and the handle from request
    message = request.form['message']
    handle = request.form['handle']

    # Extract the id
    db = get_message_db()
    cursor = db.cursor()
    count = cursor.execute("SELECT * FROM messages")
    id_ = len(cursor.fetchall()) + 1
        
    # Insert the message
    cursor.execute("INSERT INTO messages VALUES(?, ?, ?)" , (id_, message, handle))
    db.commit()
    db.close()

    return message, handle


def random_messages(n):
    '''
    Return a collection of n random messages from the message_db
    '''
    db = get_message_db()
    cursor = db.cursor()

    cmd = \
    f"""
    SELECT * FROM messages ORDER BY RANDOM() LIMIT {n}
    """

    cursor.execute(cmd)
    result = cursor.fetchall()
    db.close()

    return result


@app.route('/', methods=['POST', 'GET'])
def submit():
    '''
    Renders submit.html
    '''
    # if it's the first time entering the page, render submit.html
    # otherwise, insert message to the database and render submit.html
    if request.method == 'GET': 
        return render_template('submit.html')
    else:
        msg, handle = insert_message(request=request) 
        return render_template('submit.html', thanks=True)


@app.route('/view/')
def view(): 
    '''
    Renders view.html and displays the messages
    '''
    msg = random_messages(3)
    return render_template('view.html', messages=msg)
