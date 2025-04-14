from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5002@localhost:5432/mydata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)


class Task(db.Model):
    __tablename__ = 'task'
    emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_name = db.Column(db.String(200), nullable=False)
    emp_salary = db.Column(db.Integer)

    def __init__(self, emp_name, emp_salary):
        self.emp_name = emp_name
        self.emp_salary = emp_salary


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


@app.route('/task', methods=['POST'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'emp_name': {'type': 'string'},
                    'emp_salary': {'type': 'integer'}
                },
                'required': ['emp_name', 'emp_salary']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Employee created successfully',
            'examples': {
                'application/json': {
                    'emp_id': 1,
                    'emp_name': 'John Doe',
                    'emp_salary': 50000
                }
            }
        }
    }
})
def create_employee():
    data = request.get_json()
    emp = Task(emp_name=data['emp_name'], emp_salary=data['emp_salary'])
    db.session.add(emp)
    db.session.commit()
    return task_schema.jsonify(emp), 201

@app.route('/task', methods=['GET'])
@swag_from({
    'tags': ['Employee'],
    'responses': {
        200: {
            'description': 'A list of all employees',
            'examples': {
                'application/json': [
                    {
                        'emp_id': 1,
                        'emp_name': 'John Doe',
                        'emp_salary': 50000
                    },
                    {
                        'emp_id': 2,
                        'emp_name': 'Jane Smith',
                        'emp_salary': 60000
                    }
                ]
            }
        }
    }
})
def get_employees():
    emp = Task.query.all()  
    return tasks_schema.jsonify(emp)



@app.route('/task/<int:emp_id>', methods=['GET'])
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
                    'emp_id': 1,
                    'emp_name': 'John Doe',
                    'emp_salary': 50000
                }
            }
        },
        404: {
            'description': 'Employee not found'
        }
    }
})
def get_employee(emp_id):
    emp = Task.query.get_or_404(emp_id)  
    return task_schema.jsonify(emp)
@app.route('/task/<int:emp_id>', methods=['PUT'])
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
                    'emp_name': {'type': 'string'},
                    'emp_salary': {'type': 'integer'}
                },
                'required': ['emp_name', 'emp_salary']
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
    emp = Task.query.get_or_404(emp_id)  
    data = request.get_json()

    emp.emp_name = data.get('emp_name', emp.emp_name)
    emp.emp_salary = data.get('emp_salary', emp.emp_salary)

    db.session.commit()  
    return jsonify({"message": "Employee updated successfully"}), 200
@app.route('/task/<int:emp_id>', methods=['PATCH'])
@swag_from({
    'tags': ['Employee'],
    'parameters': [
        {
            'name': 'emp_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the employee to update partially'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'emp_name': {'type': 'string'},
                    'emp_salary': {'type': 'integer'}
                }
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
def update_partial_employee(emp_id):
    emp = Task.query.get_or_404(emp_id)
    data = request.get_json()

    task_schema.load(data, instance=emp, partial=True)
    db.session.commit()
    
    return jsonify({"message": "Employee updated successfully"}), 200
@app.route('/task/<int:emp_id>', methods=['DELETE'])
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
    emp = Task.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()

    return jsonify({"message": "Employee deleted successfully"}), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
