from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

config = {
  "apiKey": "AIzaSyBgQD6aYXng_d47Sj56kTV-yF9h6ExG2p4",
  "authDomain": "clils-project.firebaseapp.com",
  "projectId": "clils-project",
  "storageBucket": "clils-project.appspot.com",
  "messagingSenderId": "147852976889",
  "appId": "1:147852976889:web:d1a3fe7e7f8b69edbd3828",
  "measurementId": "G-YRBZZPR6QJ",
  "databaseURL":"https://clils-project-default-rtdb.firebaseio.com/"
};

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


#welcome page
@app.route('/')
def welcome_page():
    return render_template("index.html") 

#signup page
@app.route('/signup', methods=['GET','POST'])
def signup():
    error=""
    if request.method=='POST':
        email=request.form['email']
        password = request.form['password']
        try:
            login_session['email']=email
            login_session['password']=password
            login_session['user'] = auth.create_user_with_email_and_password(email,password)
            user = {"firstname":request.form['firstname'], "username":request.form['username']}
            UID = login_session['user']['localId']
            db.child("Users").child(UID).set(user)
            return redirect(url_for('home'))
        except:
            return render_template("signup.html")
            
    return render_template("signup.html")

#login page
@app.route('/login' , methods=['GET','POST'])
def login():
    if request.method =='POST':
        email=request.form['email']
        password=request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email,password)
            UID = login_session['user']['localId']
            user = db.child("Users").child(UID).get().val()
            
            return redirect (url_for('home'))
        except:
            return render_template("login.html")

    return render_template("login.html")

#home page
@app.route('/home',methods=['GET', 'POST'])
def home():
    error = ""

    UID = login_session['user']['localId']
    user = db.child("Users").child(UID).get().val()
    name=user['firstname']
    username=user['username']

    if request.method=="POST":
        meal=request.form['favmeal']
        favorite={"username":username,"meal":meal,"rating":request.form['rating']}

        db.child("Favorites").push(favorite)
        #db.child("Users").child(UID).child("favorites").push(favorite)
        meals = db.child("Meals").get().val()
        return render_template("home.html", name=name,all_meals=meals)

    else:
        try:
            meals = db.child("Meals").get().val()
            return render_template("home.html", all_meals=meals, name=name)
        
        except:
            error = "Failed to get meals, try to refresh."
            return render_template("home.html", name=name, error=error)

@app.route('/fav_meals')
def fav_meals():
    UID = login_session['user']['localId']
    user = db.child("Users").child(UID).get().val()
    name=user['firstname']   
    favorites = db.child("Favorites").get().val()
    return render_template("fav_meals.html", favorites=favorites,name=name)

@app.route('/signout')
def signout():
    login_session['user']= None
    auth.current_user = None
    return redirect (url_for('welcome_page'))

@app.route('/meal/<string:meal_id>')
def meal(meal_id):
    UID=login_session['user']['localId']
    user = db.child("Users").child(UID).get().val()
    name=user['firstname']
    meal= db.child("Meals").child(meal_id).get().val()

    return render_template("meal.html", name=name, meal_id=meal_id,meal=meal)

@app.route('/add_meal',methods=['GET' , 'POST'])
def add_meal():
    if request.method=='POST':
        try:
            title=request.form['title']
            img=request.form['image']
            text=request.form['text']
            meal={"title": title, "img": img, "text":text }
            db.child("Meals").push(meal)
        except:
            return render_template("add_meal.html")
    return render_template("add_meal.html")



#Code goes above here

if __name__ == '__main__':
    app.run(debug=True)


