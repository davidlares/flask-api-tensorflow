from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient # mongo python client
import bcrypt

app = Flask(__name__) # __name__ convention
api = Api(app)

client = MongoClient('mongodb://db:27017') # db -> from the docker compose
db = client.sentencesDB # instance
users = db['Users'] # collection

def checkPostedData(postedData, functionName):
    if(functionName == "register"):
        if "username" not in postedData or "password" not in postedData:
            return 301
        else:
            return 200

def verifyPw(username,password):
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
        # hashing_password
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        # store in DB
        users.insert({"username" : username, "password": hashed_pw, "sentence": "", "token": 10})
        retJson = {"status": 200, "msg": "Your successfully signed up for the API"}
        return jsonify(retJson)

class Store(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        correct_pw = verifyPw(username, password) # handling errors (other way)
        if not correct_pw:
            retJson = {"status": 302}
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {"status": 301}
            return jsonify(retJson)

        # storing the sentence
        users.update({"username": username},{"$set": {"sentence": sentence, "token": num_tokens - 1}})
        retJson = {"status": 302, "msg": "Sentence saved successfully"}
        return jsonify(retJson)

class Get(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username, password) # handling errors (other way)
        if not correct_pw:
            retJson = {"status": 302}
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {"status": 301}
            return jsonify(retJson)

        # discounting tokens
        users.update({'username': username}, {'$set': {"token": num_tokens - 1}})

        # getting the sentence
        sentence = users.find({'username' : username})[0]['sentence']
        retJson = {"status": 200, "msg": sentence}
        return jsonify(retJson)

# attaching the resources to the API
api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")

@app.route('/')
def hello_world():
    return "Hello, World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
