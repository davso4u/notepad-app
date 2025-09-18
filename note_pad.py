# from sql_flask_setup import *
from dotenv import load_dotenv
import os
import random
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, flash, url_for, redirect, request, session
# To use flash, a little code using jinja2 must be written in the template of the function to use it,
# and this is useful when dealing with logins...this help to show user if login successful or not

# GET method is to display message or info while POST method is used to add post on a site

load_dotenv()

app=Flask(__name__)
app.secret_key= os.getenv('FLASK_SECRET_KEY')      #This line of code must be written for messages to show while using flash

'''
# These line of codes are for SQL SERVER

sql_server = os.getenv('SQL_SERVER')
sql_database = os.getenv('SQL_DATABASE')
sql_driver = os.getenv('SQL_DRIVER')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mssql+pyodbc://@{sql_server}/{sql_database}?driver={sql_driver}&trusted_connection=yes"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

'''


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///note_pad.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    notes = db.relationship('Note', backref='owner', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), nullable=False, default="Medium")
    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



# Automatically create tables if they don’t exist
with app.app_context():
    # db.drop_all()
    db.create_all()










#current_user = None       #A Global variable To store the logged-in user, so that non registered member cannot access the note page

# API for the random news site
news_api_key = os.getenv('news_api_key')

@app.route("/", methods=["GET", "POST"])     #Pages with forms(login,register, add note, edit note, etc) uses method=[GET, POST] while a page just displaying info/details only uses the GET method
def home_page():
   # global current_user
    if request.method=="POST":
        # this is to store the variables in the html here so that it can read it
        username=request.form["username"]
        password=request.form["password"]

        # Check if user exists from SQL server
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
           # global current_user
            #current_user = username     #This saves the username in the current_username placeholder (Global)
            
            #storing user info in session (SQL) instead of in global variable (current_user) 
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login Successful")
            return redirect(url_for("notes"))   #This takes user to the note page if login is successful
        else:
            flash("Invalid username or password!")
            return redirect(url_for("home_page"))   #This reload the home_page to re-enter login details if initial details are wrong( either username or password)

    # The random API on the home page
    try:
        url=f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api_key}"
        response =requests.get(url)
        # this return the list of articles if it exists, otherwise it returns an empty list ([]) instead of crashing.
        if response.status_code == 200:
            news_data = response.json().get("articles", [])
            article = random.choice(news_data)
            news_title = article.get("title")
            news_url = article.get("url")

        else:
            news_title, news_url = "Error fetching API", "#"
    
    except Exception as e:
        news_title, news_url = "Failed to fetch API", "#"
    
    return render_template("notepad_homepage.html", news_title=news_title, news_url=news_url)




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        special_chars= "@#!%$&?"

        if password!=confirm_password:
            flash("Password not match! Try again")
            return redirect(url_for("register"))
        
        if len(password) <6:
            flash("password is less than 6 digits, try again")
            return redirect(url_for("register"))
        
        # checking if user exists from SQL Server
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))
        
        if not any(char in special_chars for char in password):     #Using list comprehension to loop through the password and find if there is any special_chars there
            flash("Password must contain at least one special character (@#!%$&?)")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful, please login")
        return redirect(url_for("home_page"))

    return render_template("register.html")




@app.route("/notes", methods=["GET", "POST"])
def notes():
    # global current_user
    # if current_user is None:
        # flash("Please login first!")
        # return redirect(url_for("home_page"))

# The above code works thesame way to check dt no unauthorized person access the note 
# but this below one is checking the SQL database for the user info
    if "user_id" not in session:
        flash("Please login first!")
        return redirect(url_for("home_page"))
        

    if request.method =="POST":
        title = request.form["title"]
        body = request.form["body"]
        priority = request.form["priority"]


        #creating a new note in the note page and assigning it to the current user (storing it in sql)
        new_note = Note(
            title=title,
            body=body,
            priority=priority,
            user_id=session["user_id"])
         # Adding the new note to the current user's list
        db.session.add(new_note)
        db.session.commit()
        
        flash("Note added successfully")
        # It is redirected back to note so that the user can still continue on the note page
        return redirect(url_for("notes"))

    # GET request: fetch all notes for the logged in user using the note id for all the notes
    User_notes = Note.query.filter_by(user_id=session["user_id"]).all()
    return render_template("written_notes.html", username=session["username"], notes=User_notes)



@app.route("/logout")
def logout():
    #global current_user
   # current_user = None     #This will clear the stored username meaning no username to continue on the notes page
    session.clear()     #calling the clear method in session
    flash("You have been logged out.")
    return redirect(url_for("home_page"))



@app.route("/notes/<int:id>/read_note")
def read_note(id):
    #global current_user         #Here is just to secure the note so that without login, u cant access it
    #if current_user is None:
     #   flash("Please Login first")
     #   return redirect(url_for("home_page"))

     if "user_id" not in session:
        flash("Please login first!")
        return redirect(url_for("home_page"))
    #Getting the note using the assigned id,
    # it is passed as a parameter inside the method read_note
    # note = notes_data[current_user][id]

    # using SQL database saved data to access the notes
     note = Note.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()
    
     return render_template("read_note.html", note=note)




@app.route("/notes/<int:id>/edit_note", methods=["GET", "POST"])
def edit_note(id):
    # global current_user
    # if current_user is None:
        # flash("Please login first!")
        # return redirect(url_for("home_page"))
    if "user_id" not in session:
        flash("Please login first!")
        return redirect(url_for("home_page"))
     
    # note= notes_data[current_user][id]      #This will get the particular note to edit by its id
    note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
    
    if request.method =="POST":
        note.title = request.form["title"]   #This will update the existing note with the new values from the form
        note.body = request.form["body"]
        note.priority = request.form["priority"]
        note.completed = "completed" in request.form

        db.session.commit()
        flash("Note updated successfully")
        return redirect(url_for("notes"))
    

    return render_template("edit_note.html", note=note)


@app.route("/notes/<int:id>/delete_note")
def delete_note(id):
    # global current_user
    # if current_user is None:
        # flash("Please login first")
        # return redirect(url_for("home_page"))
    
    """# THESE LINE OF CODES IS USED WHEN STORED IN PYTHON, USED IN RE-ASSIGNING id AFTER ONE ITEM /NOTE IS DELETED

    # This remove the note with the given id
    # if id >= 0 and id < len(notes_data[current_user]):
        # notes_data[current_user].pop(id)

        # Re-index id of the remaining notes after a note deletion
        # looping through the current user's stored note_data which is a dict
        # for i, note in enumerate(notes_data[current_user]):
        #for i in range(len(notes_data[current_user])):   #instead of using enumerate, this gets the note dict at position i
        #    note = notes_data[current_user][i]          # then assign the index as its id
            # note["id"] = i
        """
    

    if "user_id" not in session:
            flash("Please login first!")
            return redirect(url_for("home_page"))
    

    note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        flash("Note deleted successfully")
       
    else:
        flash("Note not found")
       
    return redirect(url_for("notes"))



# Toggle flips the status of the note (completed / not completed)
# if note is completed, toggle will make it not completed and vis-versa
@app.route("/notes/<int:id>/toggle", methods=["POST"])
def toggle(id):
    """global current_user

    # This checks if the id exists in the user's notes list
    if id >=0 and id < len(notes_data[current_user]):
        note = notes_data[current_user][id]
        # if checkbox was checked ; mark completed
        if "completed" in request.form:
            note["completed"] = True
        else:
            note["completed"] = False
        flash("Note status updated!")

        return redirect(url_for("notes"))"""
   


    note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
    if "completed" in request.form:
       note.completed = True
    else:
        note.completed = False
        
    db.session.commit()
    flash("Note status updated!")

    return redirect(url_for("notes"))






# works on local running not on render

# if __name__=="__main__":
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)