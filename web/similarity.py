from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient # mongo python client
import bcrypt
import spacy

app = Flask(__name__) # __name__ convention
api = Api(app)

client = MongoClient('mongodb://db:27017') # db -> from the docker compose
db = client.similarityDB # instance
users = db['Users'] # collection

def UserExist(username):
    if users.find({'username': username}).count() == 0:
        return False
    return True

def verifyPw(username,password):
    if not UserExist(username):
        return false
    hashed_pw = users.find({'username': username})[0]['password']
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({'username': username})[0]['token']
    return tokens

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

class Detect(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        text_one = postedData["t1"]
        text_two = postedData["t2"]

        if not UserExist(username):
            retJson = {"status": 301, "msg": "Invalid Username"}

        correct_pw = verifyPw(username, password) # handling errors (other way)
        if not correct_pw:
            retJson = {"status": 302}
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {"status": 303, "msg": "You are out of tokens, please refill"}
            return jsonify(retJson)

        # calculating distance
        nlp = spacy.load('en_core_web_sm')
        text_one = nlp(text_one)
        text_two = nlp(text_two)
        # ratio - number range 0 - 1. closer to 1 (more close in similarity)
        ratio = text_one.similarity(text_two)
        retJson = {"status": 200, "similarity": ratio , "msg": "Similarity score calculated successfully"}
        current_tokens = countTokens(username)
        users.update({"username": username}, {"$set": {"token": current_tokens - 1}})
        return jsonify(retJson)

class Refill(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"]

        if not UserExist(username):
            retJson = {"status": 301, "msg": "Invalid Username"}
            return jsonify(retJson)

        correct_pw = 'abc123' # handling errors (other way)
        if not password == correct_pw:
            retJson = {"status": 304, "msg": "Invalid Admin Password"}
            return jsonify(retJson)

        # discounting tokens
        current_tokens = countTokens(username)
        users.update({'username': username}, {'$set': {"token": refill_amount}})

        retJson = {"status": 200, "msg": "Refilled successfully"}
        return jsonify(retJson)

# attaching the resources to the API
api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refill, "/refill")

@app.route('/')
def hello_world():
    return "Hello, World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
