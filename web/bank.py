from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient # mongo python client
import bcrypt
import requests
import subprocess
import json

app = Flask(__name__) # __name__ convention
api = Api(app)

client = MongoClient('mongodb://db:27017') # db -> from the docker compose
db = client.imageRecogDB # instance
users = db['Users'] # collection

def UserExist(username):
    if users.find({'username': username}).count() == 0:
        return False
    return True

def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Invalid username"), True
    correct_pw = verifyPw(username, password)
    if not correct_pw:
        return generateReturnDictionary(302, "Invalid Password"), True
    return None, False

def verifyPw(username,password):
    if not UserExist(username):
        return false
    hashed_pw = users.find({'username': username})[0]['password']
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def cashWithUser(username):
    cash = users.find({"username": username})[0]['own']
    return cash

def debtWithUser(username):
    debt = users.find({"username": username})[0]['debt']
    return debt

def generateReturnDictionary(status, msg):
    retJson = {"status": status, "msg": msg}
    return retJson

def updateAccount(username, balance):
    users.update({"username": username},"$set": {"own": balance})

def updateDebt(username, balance):
    users.update({"username": username},"$set": {"debt": balance})

def countTokens(username):
    tokens = users.find({'username': username})[0]['token']
    return tokens

class Add(Resource):
    def post(self):
        postedData = request.get_json()
        # getting data
        username = postedData['username']
        password = postedData['password']
        money = postedData["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        if money <= 0:
            return jsonify(generateReturnDictionary(304, "The money amount must be greater than 0"))

        cash = cashWithUser(username)
        money -=1
        bank_cash = cashWithUser("BANK")
        updateAccount("BANK", bank_cash + 1) # the bank balance
        updateAccount(username, cash + money) # user balance
        return jsonify(generateReturnDictionary(200, "Amount added successfully to the account"))

class Transfer(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData['username']
        password = postedData['password']
        to = postedData["to"]
        money = postedData["amount"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(username)
        if cash <= 0:
            return jsonify(generateReturnDictionary(304, "You're out of money, please do something"))

        if not UserExist(to):
            return jsonify(generateReturnDictionary(301, "Receiver username is invalid"))

        cash_from = cashWithUser(username)
        cash_to = cashWithUser(to)
        bank_cash = cashWithUser("BANK")
        updateAccount("BANK", bank_cash + 1)
        updateAccount(to, cash_to + money - 1)
        updateAccount(username, cash_from - money)
        return jsonify(generateReturnDictionary(200, "Transfer successfully"))

class Register(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        # getting data
        username = postedData['username']
        password = postedData['password']

        if UserExist(username):
            retJson = {"status": 301, "msg": "Invalid Username"}
            return jsonify(retJson)
        # hashing_password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        # store in DB
        users.insert({"username" : username, "password": hashed_pw, "token": 10})
        retJson = {"status": 200, "msg": "Your successfully signed up for the API"}
        return jsonify(retJson)

class Balance(Resource):
    def post(self):
        postedData = request.get_json()
        # getting data
        username = postedData['username']
        password = postedData['password']

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        retJson = users.find({"username": username}. {"password": 0, "_id": 0})[0] # conditioning find result
        return jsonify(retJson)

class TakeLoan(Resource):
    def post(self):
        postedData = request.get_json()
        # getting data
        username = postedData['username']
        password = postedData['password']
        money = postedData["amount"]

        retJson, password = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(username)
        debt = debtWithUser(username)
        updateAccount(username, cash + money)
        updateDebt(username, debt + money)
        return jsonify(generateReturnDictionary(200, "Loan added successfully"))

class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()
        # getting data
        username = postedData['username']
        password = postedData['password']
        money = postedData["amount"]

        retJson, password = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        cash = cashWithUser(username)
        if cash < money:
            return jsonify(generateReturnDictionary(303, "Not enough cash in your account"))

        debt = debtWithUser(username)
        updateAccount(username, cash - money)
        updateDebt(username, debt - money)
        return jsonify(generateReturnDictionary(200, "Load paid"))


class Refill(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"]

        if not UserExist(username):
            return jsonify(generateReturnDictionary(301, "Invalid username"))

        correct_pw = 'abc123' # handling errors (other way)
        if not password == correct_pw:
            return jsonify(generateReturnDictionary(304, "Invalid Admin Password"))

        # discounting tokens
        current_tokens = countTokens(username)
        users.update({'username': username}, {'$set': {"token": refill_amount}})

        return jsonify(generateReturnDictionary(200, "Refilled successfully"))

# attaching the resources to the API
api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(TakeLoan, "/take-loan")
api.add_resource(Payloan, "/pay-loan")
api.add_resource(Refill, "/refill")

@app.route('/')
def hello_world():
    return "Hello, World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
