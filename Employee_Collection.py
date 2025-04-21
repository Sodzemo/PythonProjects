from flask import Flask,request,jsonify
from flasgger import Swagger,swag_from
import pymongo
import os
from dotenv import load_dotenv
#load environment variables
load_dotenv("config.env")
#mongoDB connection
db_name=os.getenv('database')
collection_name=os.getenv('collection')
client=pymongo.MongoClient(host='localhost',port=27017)
db=client[db_name]
collection = db[collection_name]

#flask app
app = Flask(__name__)
Swagger=Swagger(app)

@app.route("/")
def index():
    return "Flask+Pymongo+Swagger!"

#post(insert)
@app.route("/insert", methods=["POST"])
@swag_from({
    'tags': ['Insert User'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'emp_id':{'type':'integer'},
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'},
                    'salary': {'type':'integer'}
                },
                'required': ['emp_id','name', 'age','salary']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User inserted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'id': {'type': 'string'}
                }
            }
        },
        400:{
            'description':'missing or invalid date'
        }
    }
})
def insert_user():
 try:
    data = request.get_json()
    required_fields = ['emp_id', 'name', 'age', 'salary']

    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    data['emp_id'] = int(data['emp_id'])
    data['age'] = int(data['age'])
    data['salary'] = int(data['salary'])

    result = collection.insert_one(data)
    return jsonify({"message": "User inserted", "id": str(result.inserted_id)})

 except Exception as e:
    return jsonify({"error": str(e)}), 500

#get(read)
@app.route('/out', methods=['GET'])
@swag_from({
    'tags': ['Employee'],
    'responses': {
        200: {
            'description': 'A list of all employees',
            'examples': {
                'application/json': [
                    {
                        'emp_id': 1001,
                        'name': 'John Doe',
                        'age': 25,
                        'salary': 50000
                    },
                    {
                        'emp_id': 1002,
                        'name': 'Jane Smith',
                        'age': 28,
                        'salary': 60000
                    }
                ]
            }
        },
        404: {
            'description': 'No employees found',
            'examples': {
                'application/json': {
                    'message': 'No data found in the database.'
                }
            }
        }
    }
})
def get_user():
    employees = list(collection.find({}, {"_id": 0}))  # Get all employees without _id

    if employees:
        return jsonify(employees), 200
    else:
        return jsonify({"message": "No data found in the database."}), 404
    

@app.route('/out/<int:emp_id>', methods=['GET'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {
            'name': 'emp_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the employee to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Employee data retrieved successfully',
            'examples': {
                'application/json': {
                    'emp_id': 1001,
                    'age': 27,
                    'name': 'John Doe',
                    'salary': 50000
                }
            }
        },
        404: {
            'description': 'Employee not found'
        }
    }
})
def get_user_by_id(emp_id):
    employee = collection.find_one({"emp_id": emp_id}, {"_id": 0})  # Find by emp_id, exclude _id

    if employee:
        return jsonify(employee), 200
    else:
        return jsonify({"message": "No data found in the database."}), 404
    
#put(update)
@app.route('/out/<int:emp_id>', methods=['PUT'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {
            'name': 'emp_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the employee to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'age':{'type':'integer'},
                    'salary': {'type': 'integer'}
                },
                'required': ['name', 'salary','age']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Employee updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Employee updated successfully'
                }
            }
        },
        404: {
            'description': 'Employee not found'
        }
    }
})
def update_employee(emp_id):  
    data = request.get_json()

    update_employee = {
        "name":data.get("name"),
        "age":data.get("age"),
        "salary":data.get("salary")
    }
    result = collection.update_one({"emp_id":emp_id},{"$set":update_employee})
    
    if result.matched_count == 0:
        return jsonify({"message":"employee not found"}),404
    else:
     return jsonify({"message": "Employee updated successfully"}), 200

#delete(delete)    
@app.route('/out/<int:emp_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {
            'name': 'emp_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the employee to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Employee deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'Employee deleted successfully'
                }
            }
        },
        404: {
            'description': 'Employee not found'
        }
    }
})
def delete_employee(emp_id):
    result = collection.delete_one({"emp_id": emp_id})

    if result.deleted_count == 0:
        return jsonify({"message": "Employee not found"}), 404
    else:
        return jsonify({"message": "Employee deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)