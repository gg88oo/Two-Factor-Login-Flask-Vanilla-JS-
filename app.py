
from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from cs50 import SQL
import requests
import redis
import random

app = Flask("__name__")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#main database for storing everything
db = SQL("sqlite:///database.db")
#redis for only email verifticaiton keys
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


@app.route("/")
def index():
    try:
        id = session['user_id']
    except KeyError:
        return redirect("/login")
    
    account = db.execute("SELECT * FROM accounts WHERE idINTEGER = ?",id)
    return render_template("/index.html", username=account[0]['username'])


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        account = db.execute("SELECT * FROM accounts WHERE email = ?", email)
        print(f"debug, email:{email}, password {password} accout {account}")
        if len(account) == 0:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        if not check_password_hash(account[0]["password"], password):
            return jsonify({"status": "fail"}), 200


        # if the email and password are correct then setup for a two way authonticaiton

        # 1 CREATE A 5 LONG DIGIT CODE AND STORE IT IN REDIS FOR 60 SECONDS
        # 2 SEND THAT CODE TO THE USER'S EMAIL
        # ONCE USER WRITES THE CODE DOWN CHECK IF IT'S CORRECT AND LOG HIM
        # IF NOT CORRECT LET HIM TRY AGAIN
        code = random_code(5)
        account_id = account[0]['idINTEGER']
        r.set(account_id, code, ex=60)
        print(code)
        return jsonify({"success": True, "id":account[0]['idINTEGER']}), 200
    else:
        return render_template("login.html")

@app.route("/verify-code", methods=['POST'])
def verifycode():
    data = request.get_json()
    id = data.get("id")
    code = data.get("code")

    check = r.get(id)

    # check if the code hasn't died

    if check is None:
        return redirect("/login")
    
    # check if correct, then setup session and redirect user to the homepage

    if check == code:
        # setup session
        session['user_id'] = id
        return jsonify({"success": True}), 200
    else:
        return jsonify({"status": "fail"}), 200
    
def random_code(n):
    code = ""
    for i in range(n):
        code = code + str(random.randint(0, 9))

    return code

