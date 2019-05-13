from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient # mongo python client
import os

app = Flask(__name__) # __name__ convention
api = Api(app)

client = MongoClient('mongodb://db:27017') # db -> from the docker compose
db = client.newDB # instance
userNum = db['userNum'] # collection

# dummy insertion
userNum.insert({'num_of_users' : 0})

def checkPostedData(postedData, functionName):
    if(functionName == "add" or functionName == "substract" or functionName == "multiply"):
        if "x" not in postedData or "y" not in postedData:
            return 301
        else:
            return 200
    elif(functionName == "divide"):
        if "x" not in postedData or "y" not in postedData:
            return 301
        elif int(postedData['y']) == 0:
            return 302 # getting the Zero (casting it to INT)
        else:
            return 200 # all good

class Add(Resource):

    # post because the HTTP verb
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, "add") # handling errors
        if (status_code != 200):
            retJson = { "Message": "An error happened", "Status code": status_code }
            return jsonify(retJson)

        x = int(postedData['x'])
        y = int(postedData['y'])
        ret = x + y
        retJson = {"Sum": ret, "Status_Code": 200}
        return jsonify(retJson)

class Subtract(Resource):
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, "substract") # handling errors
        if (status_code != 200):
            retJson = { "Message": "An error happened", "Status code": status_code }
            return jsonify(retJson)

        x = int(postedData['x'])
        y = int(postedData['y'])
        ret = x - y
        retJson = {"Substract": ret, "Status_Code": 200}
        return jsonify(retJson)

class Multiply(Resource):
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, "multiply") # handling errors
        if (status_code != 200):
            retJson = { "Message": "An error happened", "Status code": status_code }
            return jsonify(retJson)

        x = int(postedData['x'])
        y = int(postedData['y'])
        ret = x * y
        retJson = {"Times": ret, "Status_Code": 200}
        return jsonify(retJson)

class Divide(Resource):
    def post(self):
        postedData = request.get_json()
        status_code = checkPostedData(postedData, "divide") # handling errors
        if (status_code != 200):
            retJson = { "Message": "An error happened", "Status code": status_code }
            return jsonify(retJson)

        x = int(postedData['x'])
        y = int(postedData['y'])
        ret = (x * 1.0) / y # forcing float convertion - avoiding ByZeroError
        retJson = {"Division": ret, "Status_Code": 200}
        return jsonify(retJson)

# User tracking added to DB
class Visit(Resource):
    def get(self):
        prev_num = userNum.find({})[0]['num_of_users']
        new_visitor = prev_num + 1 # new visitor
        userNum.update({}, {"$set": {'num_of_users': new_visitor}})
        return "Hello, user: " + str(new_visitor)


# attaching the resources to the API
api.add_resource(Add, "/add")
api.add_resource(Subtract, "/substract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visit, "/hello")

@app.route('/')
def hello_world():
    return "Hello, World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
