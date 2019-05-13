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

def generateReturnDictionary(status, msg):
    retJson = {"status": status, "msg": msg}
    return retJson

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

class Classify(Resource):
    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        url = postedData["url"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        tokens = users.find({"username": username})[0]["token"]
        if tokens <= 0:
            return jsonify(generateReturnDictionary(303,"Not enough tokens!"))

        r = requests.get(url) # getting the url file
        retJson = {}
        with open("temp.jpg","wb") as f: # opening the image
            f.write(r.content) # desired image - writing the image into the temp
            # opening the trained file
            proc = subrocess.Popen('python3 classify_image.py --model_dir=. --image_file=./temp.jpg')
            proc.communicate()[0] #
            proc.wait() # thread completion
            with open('text.txt') as g: # getting the resulting txt in the JSON file
                retJson = json.load(g)

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
api.add_resource(Classify, "/classify")
api.add_resource(Refill, "/refill")

@app.route('/')
def hello_world():
    return "Hello, World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
