from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
from flask_pymongo import PyMongo
import json
from functools import wraps
import datetime
from bson.objectid import ObjectId



app = Flask(__name__)
app.config["MONGO_URI"] = "{MongoDB url}"
mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('home.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method =="POST":
        users = mongo.db.users
        user = request.form.get("username")
        candidate_pass = request.form.get("password")
        result = users.find_one()
        if result['username'] == user:
            if result['password'] == candidate_pass:
                session['logged_in'] = True
                session['username'] = request.form.get("username")
                return redirect(url_for('dashboard'))
                mongo.db.close()
            else:
                return "Wrong Password"
        else:
            return redirect(url_for('home'))

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/dashboard", methods=['GET','POST'])
@login_required
def dashboard():
    active = True
    posts = mongo.db.posts
    post=posts.find()
    return render_template('dashboard.html', posts=post, active=active)


@app.route("/CreatePost", methods=['GET', 'POST'])
@login_required
def create_post():
    if 'username' in session:
        return render_template('create_post.html')

@app.route("/PostCreated", methods=['POST'])
def post_created():
    if request.form.get('IssueID') == '' or request.form.get('TimeSpent') == '':
        flash("Fields can not be empty!")
        return redirect(url_for('create_post'))
    else:
        mongo.db.posts.insert({'IssueID' : request.form.get('IssueID'), 'TimeSpent': request.form.get('TimeSpent')})
        return redirect(url_for('dashboard'))


@app.route("/create", methods=['POST'])
def create():
    posts = mongo.db.posts

    issue_id = request.json["memo"]
    time_spent = request.json["duration"]

    post_id = posts.insert({'IssueID': issue_id, 'TimeSpent': time_spent, 'date': datetime.datetime.now()})
    new_post = posts.find_one({'_id': post_id})

    output = {'IssueID': new_post['IssueID'], 'TimeSpent': new_post['TimeSpent']}
    return jsonify({'result': output})

@app.route("/posts", methods = ['GET'])
def posts():
    output = []
    posts = mongo.db.posts
    for p in posts.find():
        output.append({'IssueID': p['IssueID'], 'TimeSpent': p['TimeSpent'], 'data': p['date']})

    return jsonify({'results': output})

@app.route("/deletePost/<id>", methods=['GET','POST'])
@login_required
def deletePost(id):
    id = str(id)
    posts = mongo.db.posts
    posts.remove({'_id': ObjectId(id)})

    return redirect(url_for('dashboard'))


if __name__== '__main__':
    app.secret_key = 'mySecret'
    app.run(debug=True)
