import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import gettempdir
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from flask_jsglue import JSGlue
from helpers import *


# configure application
app = Flask(__name__)
JSGlue(app)


# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finalproject.db")


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/onload", methods = ["GET"])
@login_required
def onload():
    """Sets completedness of tasks/goals to false onload to keep in sync with checkboxes"""
    if request.method == "GET":
        set_false_onload("tasks", session["user_id"])
        set_false_onload("goals", session["user_id"])
  
        return redirect(url_for("index"))

@app.route("/update", methods=["GET"])
@login_required
def update():
    """Updates Complete column in SQL to allow completed tasks/goals to be removed"""
    if request.method == "GET":
        # get parameters from JSON request
        id = request.args.get("id")
        completedness = request.args.get("checked")
        table = request.args.get("table")
        # update goals/tasks completedness
        update_completedness(table, completedness, id)
        return redirect("https://ide50-jason-ren.cs50.io/")
        

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    """ displays current to-dos, deletes completed to-dos"""
     # if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        # get tasks of current user and pass to template
        cur_user_tasks = select_task(session["user_id"])
        return render_template("tasks.html", tasks = cur_user_tasks)
        
    # else if user reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        # delete completed tasks
        delete_task(session["user_id"])
        return redirect(url_for("tasks"))
    
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    # forget any user_id
    session.clear()

    # if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")
    
    # if user reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = select_user(request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("register.html")
        
    # else if user reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        # get user info from form
        form_username = request.form.get("username")
        form_password = request.form.get("password")
        
        # ensure username was submitted
        if not form_username:
            return apology("must provide username")
            
        # ensure password was submitted and verified
        if not form_password or form_password != request.form.get("password_verify"):
            return apology ("must provide matching passwords")
        
        # insert info into users table and store to test if the username was already taken
        username_test = insert_user(form_username, pwd_context.encrypt(form_password))
     
        if username_test == None:
            return apology("Username Taken")
            
        # redirect to main page
        return redirect(url_for("login"))
   
        
@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("index"))
    
    
@app.route("/create_task", methods=["GET", "POST"])
@login_required
def create_task():
    """Create To-do."""
    # if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("create_task.html")
        
    # else if user reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        
        # insert task into tasks table
        insert_task(session["user_id"], request.form.get("what"), request.form.get("when"), request.form.get("where"), request.form.get("how"))
    
        # redirect to view user tasks
        return redirect(url_for("tasks"))
  
        
@app.route("/create_goal", methods=["GET", "POST"])
@login_required
def create_goal():
    """Create Goal."""
     # if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("create_goal.html")
    
    # else if user reached route via POST (as by submitting a form via POST)    
    elif request.method == "POST":
        
        # insert goal into goals table
        insert_goal(session["user_id"], request.form.get("goal"))
        
        # get if-then plans from form
        obs1 = request.form.get("obs1")
        res1 = request.form.get("res1")
        obs2 = request.form.get("obs2")
        res2 = request.form.get("res2")
      
        # get id of goal just inserted
        cur_goal_id = select_goal(session["user_id"], request.form.get("goal"))[0]["id"]
        
        # insert if-then plans into ii table if they exist
        if obs1 and res1:
            insert_ii(cur_goal_id, obs1, res1)
        if obs2 and res2:
            insert_ii(cur_goal_id, obs2, res2)
            
        # redirect to view user goals
        return redirect(url_for("goals"))
   
        
@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    """displays current goals and deletes completed goals, goals linked with implementation intentions"""
    # if user reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        # get current user goals and accompanying ii and pass to template
        cur_user_goals = select_goals_with_ii(session["user_id"])
        return render_template("goals.html", goals = cur_user_goals)
        
    # else if user reached route via POST (as by submitting a form via POST)      
    elif request.method == "POST":
        # delete completed goals and accompanying ii
        delete_goals_with_ii(session["user_id"])
        return redirect(url_for("goals"))
        
        
@app.route("/", methods=["GET"])
def index():
    """display main page"""
    if request.method == "GET":
        return render_template("index1.html")
        
        
@app.route("/effectiveness", methods=["GET"])
def effectiveness():
    """display effectiveness page"""
    if request.method == "GET":
        return render_template("effectiveness.html")

        
@app.route("/easy", methods=["GET"])
def easy():
    """display how to use page"""
    if request.method == "GET":
        return render_template("easy.html")
 
        
@app.route("/benefits", methods=["GET"])
def benefits():
    """display longterm benfits page"""
    if request.method == "GET":
        return render_template("benefits.html")


@app.route("/todo_questions", methods=["GET"])
def todo_questions():
    """displays create to-do questions page"""
    if request.method == "GET":
        return render_template("todo_questions.html")
 
        
@app.route("/goal_questions", methods=["GET"])
def goal_questions():
    """displays create goal questions page"""
    if request.method == "GET":
        return render_template("goal_questions.html")



# SQL FUNCTIONS

# sets all items of specified table of the current user false
def set_false_onload(table, u_id):
    db.execute("UPDATE :table SET Completed = 'false' WHERE u_id = :u_id", table = table, u_id = u_id)
    
# updates completedness of specified table of specified item 
def update_completedness(table, completedness, id):
    db.execute("UPDATE :table SET Completed = :completedness WHERE id = :id", table = table, completedness = completedness, id = id)
    
# returns user with specified username
def select_user(username):
    return db.execute("SELECT * FROM users WHERE username = :username", username = username)

# returns tasks of current user
def select_task(u_id):
    return db.execute("SELECT * FROM tasks WHERE u_id = :u_id", u_id = u_id)

# returns goals of current user
def select_goal(u_id, goal):
     return db.execute("SELECT * FROM goals WHERE u_id = :u_id AND Goal = :goal", u_id = u_id, goal = goal)

# returns goals and accompnying ii of current user
def select_goals_with_ii(u_id):
    # gets goals of current user
    cur_user_goals = db.execute("SELECT id, Goal FROM goals WHERE u_id = :u_id", u_id = u_id)
    # appends accompanying ii's for for each goal with key ["ii"] 
    for goal in cur_user_goals:
        cur_user_goals[cur_user_goals.index(goal)]["ii"] = db.execute("SELECT obstacle, response FROM ii WHERE g_id = :g_id", g_id = goal['id']) 
    return cur_user_goals

# deletes completed goals and accompanying ii of current user
def delete_goals_with_ii(u_id):
    # gets completed goals of current users
    to_delete = db.execute("SELECT id FROM goals WHERE Completed = 'true' AND u_id = :u_id", u_id = u_id)
    # create list of ids of completed goals
    to_delete_ids = [li["id"] for li in to_delete]
    # delete accompanying ii's for each goal
    for id in to_delete_ids:
        db.execute("DELETE FROM ii WHERE g_id = :g_id", g_id = id)
    # delete complete goals
    db.execute("DELETE FROM goals WHERE Completed = 'true' AND u_id = :u_id", u_id = u_id)
        
# delete completed tasks of current users         
def delete_task(u_id):
    db.execute("DELETE FROM tasks WHERE Completed = 'true' AND u_id = :u_id", u_id = u_id)
    
# insert user into users table
def insert_user(username, hash_pwd):
    return db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash_pwd)", username = username, hash_pwd = hash_pwd)
    
#insert task into tasks table
def insert_task(u_id, task, time, location, how):
     db.execute("INSERT INTO tasks (u_id, Task, Time, Location, How) VALUES (:u_id, :task, :time, :location, :how)", 
            u_id = u_id, task = task, time = time, location = location, how = how)

#insert ii into ii table
def insert_ii(g_id, obstacle, response):
    db.execute("INSERT INTO ii (g_id, obstacle, response) VALUES (:g_id, :obstacle, :response)",
            g_id = g_id, obstacle = obstacle, response = response)
        
# insert goal into goals table
def insert_goal(u_id, goal):
    db.execute("INSERT INTO goals (u_id, Goal) VALUES (:u_id, :goal)", 
            u_id = u_id, goal = goal)
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

   
    

    
