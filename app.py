import base64
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy

from helpers import login_required, decode
from items import Summary, Happiness, Location

# Configure application
app = Flask(__name__)
app.secret_key = "No one will ever find out"

# Custom jinja filter for decoding base64
app.jinja_env.filters['b64decode'] = decode

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diarylite.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Initialize database
db = SQLAlchemy(app)

all_items = {
    1:Summary(),
    2:Happiness(),
    3:Location()
}

preferred_items = [
]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email =  db.Column(db.String(100), nullable=False, unique=True)
    hash = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    entries = db.relationship('Entry', backref='user', lazy=True)
    prefs = db.relationship('Prefs', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.firstname}', '{self.lastname}', '{self.email}')"


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_logged = db.Column(db.DateTime, default=datetime.now())
    items = db.relationship('Item', backref = "entry", lazy=True)

    def __repr__(self):
        return f"Entry('Log {self.id}', '{self.date_logged}')"

# Item is all the items that were logged for a specific entry
# Category is the type of item (e.x. description) for that entry. Each item type will have a unique 
# category, like (arbitrarily) lets say description had a category of 1
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable = False)

    def __repr__(self):
        return f"Item('Type {self.category}', 'Entry {self.entry_id}', 'Content {self.content}'"

# Preferences will store all the items selected for to be visible in the log menu for each user id
# If a user decides to add an item in preferences, then we will db.session.add(Prefs(category=category, user_id = session["user_id"]))
class Prefs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Prefs('Type {self.category}', 'user_id {self.user_id}')"

    def __init__(self, category, user_id):
        self.category = category
        self.user_id = user_id

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_daily_log():
    now = datetime.now()
    todays_date = f"%{str(now.year).zfill(4)}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)}%"
    return Entry.query.filter(Entry.date_logged.like(todays_date), Entry.user_id==session["user_id"]).first()

@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    deleteOption = False
    # This will only be called if deleteOption is true since that will active a form
    if request.method == "POST":
        user_entries = Entry.query.filter_by(user_id = session["user_id"]).all()
        for entry in user_entries:
            user_items = Item.query.filter_by(entry_id = entry.id).delete()
            db.session.commit()
        x = Entry.query.filter_by(user_id = session["user_id"]).delete()
        print(f"deleted {x} entries from this user")
        print(f"deleted {user_items} items from user")
        db.session.commit()
        return redirect("/")
    else:
        user = User.query.filter_by(id=session["user_id"]).first()
        firstname = user.firstname.capitalize()
        userdate = user.date_created.date().strftime("%Y-%m-%d")
        todaysdate = datetime.now().strftime('%Y-%m-%d')
        firsttime = True
        hasLogged = False
        if userdate != todaysdate:
            firsttime = False
        daily_log = get_daily_log()
        if daily_log:
            hasLogged = True
        return render_template("index.html", firstname = firstname, firsttime = firsttime, hasLogged = hasLogged, deleteOption = deleteOption)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # SQLAlchemy's way of SELECTing, through query. The User is the class/table
        # defined above, then we query it WHERE email (User.email) is email(request.form.get("email"))
        # and then select the first row (which gives me a dictionary as opposed to a list of dictionaries)
        user = User.query.filter(User.email==email).first()
        if user is None:
            flash("No account registered with that email", category="error")
            return redirect("/login")
        
        # Check password hash
        if not check_password_hash(user.hash, password):
            flash("Incorrect password", category="error")
            # Sends email to login.html to preserve input fields when reloading the page
            return render_template("login.html", email=email)
            
        # Remember which user has logged in
        session["user_id"] = user.id

        flash("Logged in", category="success")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Boolean that when true will have password checks. Good for testing.
        checkPassword = True
        # Declarations so we don't have to keep typing request.form.get
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        email = request.form.get("email")
        confirmation = request.form.get("confirmation")

        # Database has max length of 25 for firstname and lastname and 100 for email
        if len(firstname) > 25:
            flash("Firstname has a maximum length of 25 characters.", category="error")
            return render_template("register.html", lastname = lastname, email = email, password = password)
        if len(lastname) > 25:
            flash("Lastname has a maximum length of 25 characters.", category="error")
            return render_template("register.html", firstname = firstname, email = email, password = password)
        if len(email) > 100:
            flash("Email has a maximum length of 100 characters.", category="error")
            return render_template("register.html", firstname = firstname, lastname = lastname, password = password)
        # Password checks:
        if checkPassword:
            if len(password) < 8:
                flash("Password must be at least 8 characters", category="error")
                return render_template("register.html", firstname = firstname, lastname = lastname, email = email)
            if password != confirmation:
                flash("Passwords do not match", category="error")
                return render_template("register.html", firstname = firstname, lastname = lastname, email = email)

            # Checks for numbers in password
            if not any(character.isnumeric() for character in password):
                flash("Password must contain a number", category="error")
                return render_template("register.html", firstname = firstname, lastname = lastname, email = email)
                
            
            # Checks for both uppercase and lowercase characters 
            if not (any(letter.islower() for letter in password) and any(letter.isupper() for letter in password)):
                flash("Password must contain both uppercase and lowercase letters", category="error")
                return render_template("register.html", firstname = firstname, lastname = lastname, email = email)
            

        users = User.query.filter_by(email=email).all()
        if(len(users) != 0):
            flash("User with the same email already exists", category="error")
            return render_template("register.html", firstname = firstname, lastname = lastname, password = password)

        user = User(firstname=firstname, lastname=lastname, email=email, hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        # Setting default on preferences for a new user being summary and slider
        pref1 = Prefs(1, user.id)
        pref2 = Prefs(2, user.id)
        db.session.add(pref1)
        db.session.add(pref2)
        db.session.commit()

        
        flash("Registered", category="success")
        session["user_id"] = user.id

        return redirect("/")
    else:
        return render_template("register.html")

# Steps for creating a new item:
# Create new item class in items.py with everything you need including the custom html/disabledhtml. Make sure to have appropriate name and id
# Import the name of the item at the top of app.py
# Add item and corresponding category to all_items
# Set deleteOption in app.route("/") to be true and delete all entries

@app.route("/log", methods = ["GET", "POST"])
@login_required
def log():
    hasLogged = False
    items = None
    daily_log = get_daily_log()
    if daily_log:
        hasLogged = True
        items = Item.query.filter(Item.entry_id == daily_log.id).all()
    readable_date = datetime.today().strftime('%A %B %d, %Y')
    if request.method == "POST":
        if not hasLogged:
            entry = Entry(user_id = session["user_id"])
            db.session.add(entry)
            db.session.commit()
            # Content will store the content of an item for that entry. '---' indicates a new input field in the case of some items having multiple inputs. This will be used to set values in memory_results
            for category in preferred_items:
                # input_box is the name of the box we are searching for. So for summary that's "summarybox"
                # We get the value (class) at all_items with key of category
                input_box = all_items[category].name.lower()+"box" 
                encoded_content = base64.b64encode(bytes(request.form.get(input_box), 'utf-8'))
                new_item = Item(category = category, content = encoded_content, entry_id = entry.id)
                db.session.add(new_item)
                db.session.commit()
                flash("Logged new journal entry. ")
        else: 
            items_categories = []
            print(items)
            for item in items:
                if item.category in preferred_items:
                    input_box = all_items[item.category].name.lower()+"box" 
                    # Update item content to be what's in the box
                    encoded_content = base64.b64encode(bytes(request.form.get(input_box), 'utf-8'))
                    item.content = encoded_content
                    db.session.commit()
                else:
                    item.content = None
                    db.session.commit()
                if item.content:
                    items_categories.append(item.category)
            print(items_categories)
            
            entry = Entry.query.filter_by(user_id = session["user_id"]).first()
            for category in preferred_items:
                if category not in items_categories:
                    input_box = all_items[category].name.lower()+"box" 
                    encoded_content = base64.b64encode(bytes(request.form.get(input_box), 'utf-8'))
                    new_item = Item(category = category, content = encoded_content, entry_id = entry.id)
                    db.session.add(new_item)
                    db.session.commit()
            flash("Updated journal entry.")


        return redirect("/")

                
    else:
        # Requery the user's preferences to update preferred items each time the log page is got
        preferred_items.clear()
        preferences = Prefs.query.filter_by(user_id = session["user_id"]).order_by(Prefs.category).all()
        for preference in preferences:
            preferred_items.append(preference.category)
        return render_template("log.html", preferred_items = preferred_items, all_items = all_items, hasLogged = hasLogged, logged_items = items, date = readable_date)


@app.route("/prefs", methods=["GET", "POST"])
@login_required
def prefs():
    preferences = Prefs.query.filter_by(user_id = session["user_id"]).order_by(Prefs.category).all()

    if request.method == "POST":
        # Reset list so that we can add all items that were checked
        preferred_items.clear()
        # Iterates through all possible items and if the checkbox with the name of the lowercase item name is checked (not None) 
        # then we add it to the preferred items list. 
        for category in all_items:
            if request.form.get(all_items[category].name.lower()):
                preferred_items.append(category)
        # Delete all current preferences linked to the id since 'Update Preferences' button was hit
        Prefs.query.filter_by(user_id = session["user_id"]).delete()
        # Iterate through the items in our preferred list and add them back to the base
        for item in preferred_items:
            new_pref = Prefs(item, session["user_id"])
            db.session.add(new_pref)

        db.session.commit()
        flash("Updated Preferences", category="success")
        return redirect("/")
    else:
        # Once we open the preference page using get, it gets all the current preferences from that user id and adds them to the preferred items 
        preferred_items.clear()
        for preference in preferences:
            preferred_items.append(preference.category)
        return render_template("prefs.html", preferred_items = preferred_items, all_items = all_items)

# Memories will just contain the search option, whereas memories/view will appear with the relevant entries that can be viewed
@app.route("/memories")
@login_required
def memories():
    return render_template("memories.html")

@app.route("/results", methods = ["GET", "POST"])
@login_required
def results():
    if request.method == "POST":
        user_date = request.form.get("searchbar").strip()
        if user_date.lower() == "today":
            todays_date = datetime.now()
            user_date = datetime.strftime(todays_date, "%m %d %Y")
        elif user_date.lower() == "yesterday":
            yesterdays_date = datetime.now() - timedelta(days=1)
            user_date = datetime.strftime(yesterdays_date, "%m %d %Y")
        
        # Check if the user inputted like m-d-y or m/d/y
        times = ""
        if "-" in user_date:
            times = user_date.split("-")
        elif "/" in user_date:
            times = user_date.split("/")
        else:
            times = user_date.split()

        # Make sure there is and only is year month and year
        if len(times) != 3:
            flash("Input must be comprised of the year, month, and date", category = "error")
            return redirect("/memories")

        # Make sure all characters are numeric
        for time in times:
            if not time.isnumeric():
                flash("Input must be formatted using only '-', '/', ' ', and numbers", category = "error")
                return redirect("/memories")
        
        times[0] = times[0].zfill(2)
        if len(times[0]) != 2:
            flash("Invalid length for month", category = "error")
            return redirect("/memories")
        elif int(times[0]) < 0 or int(times[0]) > 12:
            flash("Invalid value for month", category = "error")
            return redirect("/memories")

        times[1] = times[1].zfill(2)
        if len(times[1]) != 2:
            flash("Invalid length for day", category = "error")
            return redirect("/memories")
        elif int(times[1]) < 0 or int(times[1]) > 31:
            flash("Invalid value for day", category = "error")
            return redirect("/memories")
        n = len(times[2])
        if n != 2 and n != 4:
            flash("Invalid length for year", category = "error")
            return redirect("/memories")
        if n == 2:
            # Just adds for example 20 to the front in the year 2021 by getting first two digits of current year
            times[2] = str(int(datetime.now().year / 100)) + times[2]
        times[2] = times[2].zfill(4)
        # Since this website is created in 2021, there's no way they have log before 2021. 
        # We also check if the year is greater than the current year
        if int(times[2]) < 2021 or int(times[2]) > datetime.now().year:
            flash("Invalid value for year", category = "error")
            return redirect("/memories")
        searched_date = f"{times[2]}-{times[0]}-{times[1]}"
        date_object = datetime.strptime(searched_date, "%Y-%m-%d")
        # Since we have a % before the year, the user can input 21 instead of 2021 and it will still search for years that have 21 in them
        like_date = f"%{searched_date}%"
        # Yesterday's date, next day's date, calculated by adding 1 day. Are also in like_date format with encompassing %%s
        yDate = "%" + (date_object-timedelta(days=1)).strftime('%Y-%m-%d') + "%"
        nDate = "%" + (date_object+timedelta(days=1)).strftime('%Y-%m-%d') + "%"
        entry = Entry.query.filter(Entry.date_logged.like(like_date), Entry.user_id==session["user_id"]).first()
        # Bit of copy-paste, but since they're different variable names there's no avoiding it
        yEntry = Entry.query.filter(Entry.date_logged.like(yDate), Entry.user_id==session["user_id"]).first()
        nEntry = Entry.query.filter(Entry.date_logged.like(nDate), Entry.user_id==session["user_id"]).first()
        yItems = None
        nItems = None
        if entry:
            items = Item.query.filter_by(entry_id = entry.id).all()
        else:
            items = None
            flash("No log entry available for that date. Try a different date.", category="error")
            return redirect("/memories")
        if yEntry:
            yItems = Item.query.filter_by(entry_id = yEntry.id).all()
        if nEntry:
            nItems = Item.query.filter_by(entry_id = nEntry.id).all()

        readable_date = date_object.strftime('%A %B %d, %Y')
        return render_template("memory_results.html", date = readable_date, items = items, all_items = all_items, yItems = yItems, nItems = nItems)
    else:
        return redirect("/memories")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
