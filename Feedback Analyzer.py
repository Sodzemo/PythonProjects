from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from textblob import TextBlob
import pymongo
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("detailsconfig.env")

# MongoDB setup
db_name1 = os.getenv('database1')  # ProductDetails
collection_name1 = os.getenv('collection1')  # products
collection_name2 = os.getenv('collection2')  # feedbacks
collection_name3 = os.getenv('collection3')  # sentimentscore  
host = os.getenv('host')
portclient = os.getenv('port')

client = pymongo.MongoClient(host=str(host), port=int(portclient))

# Correctly connect to the right collections
db = client[db_name1]
collection = db[collection_name1]  # FIXED: products collection
collection2 = db[collection_name2]  # feedbacks collection
collection3 = db[collection_name3]  # Connect to the sentimentscore collection 

# Flask app
app = Flask(__name__)
swagger = Swagger(app)

@app.route("/")
def index():
    return "Product Feedback Analyzer!"

# POST (insert products into the database)
# This endpoint allows you to insert product details into the database.
@app.route("/insert_product", methods=["POST"])
@swag_from({
    'tags': ['Insert Product'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'product_id': {'type': 'integer'},
                    'product_name': {'type': 'string'},
                    'product_category': {'type': 'string'},
                    'product_price': {'type': 'integer'},
                    'product_manufacture_date': {'type': 'string'},
                    'product_expiration_date': {'type': 'string'}
                },
                'required': ['product_id', 'product_name', 'product_category', 'product_price', 'product_manufacture_date', 'product_expiration_date']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Product inserted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'id': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Missing or invalid data'
        }
    }
})
# This endpoint allows you to insert product details into the database.
def insert_product():
    try:
        data = request.get_json()
        required_fields = ['product_id', 'product_name', 'product_category', 'product_price', 'product_manufacture_date', 'product_expiration_date']

        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Optional: check if product already exists
        if collection.find_one({"product_id": int(data['product_id'])}):
            return jsonify({"error": "Product with this ID already exists"}), 400

        # Insert data
        result = collection.insert_one({
            'product_id': int(data['product_id']),
            'product_name': str(data['product_name']),
            'product_category': str(data['product_category']),
            'product_price': int(data['product_price']),
            'product_manufacture_date': str(data['product_manufacture_date']),
            'product_expiration_date': str(data['product_expiration_date'])
        })

        return jsonify({"message": "Product inserted successfully", "id": str(result.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#GET (get all products from the database)
# This endpoint retrieves all products from the database.
@app.route("/get_all_products", methods=["GET"])
@swag_from({
    'tags': ['Get All Products'],
    'responses': {
        200: {
            'description': 'List of All Products',
            'schema': {
                'type': 'object',
                'properties': {
                    'products': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer'},
                                'product_name': {'type': 'string'},
                                'product_category': {'type': 'string'},
                                'product_price': {'type': 'integer'},
                                'product_manufacture_date': {'type': 'string'},
                                'product_expiration_date': {'type': 'string'}
                            },
                            'required': ['product_id', 'product_name', 'product_category', 'product_price', 'product_manufacture_date', 'product_expiration_date']
                        }
                    }
                }
            },
            'examples': {
                'products': [
                    {
                        'product_id': 1,
                        'product_name': 'Product A',
                        'product_category': 'Category 1',
                        'product_price': 100,
                        'product_manufacture_date': '2023-01-01',
                        'product_expiration_date': '2024-01-01'
                    },
                    {
                        'product_id': 2,
                        'product_name': 'Product B',
                        'product_category': 'Category 2',
                        'product_price': 200,
                        'product_manufacture_date': '2023-02-01',
                        'product_expiration_date': '2024-02-01'
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
        },
        500: {
            'description': 'Internal Server Error'
        },
        400: {
            'description': 'Invalid Request'
        }
    }
})
def get_all_products():
    try:
        products = list(collection.find({}, {'_id': 0}))
        return jsonify({"products": products}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET (get product by ID from the database)
# This endpoint retrieves a product by its ID from the database.  
@app.route("/get_all_products/<int:product_id>", methods=["GET"])
@swag_from({
    'tags': ['Get Product by ID'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the product to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Product found',
            'schema': {
                'type': 'object',
                'properties': {
                    'product_id': {'type': 'integer'},
                    'product_name': {'type': 'string'},
                    'product_category': {'type': 'string'},
                    'product_price': {'type': 'integer'},
                    'product_manufacture_date': {'type': 'string'},
                    'product_expiration_date': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Product not found'
        },
        500: {
            'description': 'Internal Server Error'
        }
    }
})
def get_product_by_id(product_id):
    try:
        product = collection.find_one({"product_id": product_id}, {'_id': 0})
        if product:
            return jsonify(product), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#PUT (update product by ID)
# This endpoint updates a product by its ID in the database.
@app.route("/update_product/<int:product_id>", methods=["PUT"])
@swag_from({
    'tags': ['Update Product'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the product to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'product_name': {'type': 'string'},
                    'product_category': {'type': 'string'},
                    'product_price': {'type': 'integer'},
                    'product_manufacture_date': {'type': 'string'},
                    'product_expiration_date': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Product updated successfully'
        },
        404: {
            'description': 'Product not found'
        },
        500: {
            'description': 'Internal Server Error'
        }
    }
})
def update_product(product_id):
    try:
        data = request.get_json()
        result = collection.update_one({"product_id": product_id}, {"$set": data})
        if result.matched_count > 0:
            return jsonify({"message": "Product updated successfully"}), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#DELETE (Delete Product By ID from the database)
# This endpoint deletes a product by its ID from the database.   
@app.route("/delete_product/<int:product_id>", methods=["DELETE"])
@swag_from({
    'tags': ['Delete Product'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the product to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Product deleted successfully'
        },
        404: {
            'description': 'Product not found'
        },
        500: {
            'description': 'Internal Server Error'
        }
    }
})
def delete_product(product_id):
    try:
        result = collection.delete_one({"product_id": product_id})
        if result.deleted_count > 0:
            return jsonify({"message": "Product deleted successfully"}), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST (insert feedback into the database but in feedbacks collection)
# This endpoint allows you to insert feedback for a product into the database.
@app.route("/insert_feedback", methods=["POST"])
@swag_from({
    'tags': ['Insert Feedback'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'product_id': {'type': 'integer'},
                    'user_name': {'type': 'string'},
                    'feedback_text': {'type': 'string'},
                    'rating': {'type': 'integer'}
                },
                'required': ['product_id', 'user_name' ,'feedback_text', 'rating']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Feedback inserted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'id': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Missing or invalid data'
        }
    }
})
# This endpoint allows you to insert feedback for a product into the database.
def insert_feedback():
    try:
        data = request.get_json()
        required_fields = ['product_id', 'user_name' ,'feedback_text', 'rating']

        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Optional: check if product exists
        if not collection.find_one({"product_id": int(data['product_id'])}):
            return jsonify({"error": "Product with this ID does not exist"}), 400

        # Insert data
        result = collection2.insert_one({
            'product_id': int(data['product_id']),
            'user_name': str(data['user_name']),
            'feedback_text': str(data['feedback_text']),
            'rating': int(data['rating'])
        })

        return jsonify({"message": "Feedback inserted successfully", "id": str(result.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# GET (get all feedbacks from the collection)
# This endpoint retrieves all feedbacks from the database.
@app.route("/get_all_feedbacks", methods=["GET"])
@swag_from({
    'tags': ['Get All Feedbacks'],
    'responses': {
        200: {
            'description': 'List of All Feedbacks',
            'schema': {
                'type': 'object',
                'properties': {
                    'feedbacks': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer'},
                                'user_name': {'type': 'string'},
                                'feedback_text': {'type': 'string'},
                                'rating': {'type': 'integer'}
                            },
                            'required': ['product_id', 'user_name', 'feedback_text', 'rating']
                        }
                    }
                }
            },
            'examples': {
                'feedbacks': [
                    {
                        'product_id': 1,
                        'user_name': "John Doe",
                        'feedback_text': "Great product!",
                        'rating': 5
                    },
                    {
                        'product_id': 2,
                        'user_name': "Jane Smith",
                        'feedback_text': "Not bad.",
                        'rating': 3
                    }
                ]
            }
        },
        404: {
            'description': 'No feedbacks found',
            'examples': {
                'application/json': {
                    'message': "No data found in the database."
                }
            }
        },
        500: {
            'description': "Internal Server Error"
        },
        400: {
            "description": "Invalid Request"
        }
    }
})
def get_all_feedbacks():
    try:
        feedbacks = list(collection2.find({}, {'_id': 0}))
        return jsonify({"feedbacks": feedbacks}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET (get feedback by product ID)
# This endpoint retrieves feedback for a specific product by its ID from the database.
@app.route("/get_feedback_by_product/<int:product_id>", methods=["GET"])    
@swag_from({
    'tags': ['Get Feedback by Product ID'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the product to retrieve feedback for'
        }
    ],
    'responses': {
        200: {
            'description': 'Feedback found',
            'schema': {
                'type': 'object',
                'properties': {
                    'product_id': {'type': 'integer'},
                    'user_name': {'type': 'string'},
                    'feedback_text': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': "Feedback not found"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
})

def get_feedback_by_product(product_id):
    try:
        feedback = list(collection2.find({"product_id": product_id}, {'_id': 0}))
        if feedback:
            return jsonify(feedback), 200
        else:
            return jsonify({"error": "Feedback not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# PUT (update feedback)
# This endpoint updates feedback for a specific product by its ID in the database.
@app.route("/update_feedback/<int:product_id>", methods=["PUT"])
@swag_from({
    'tags': ['Update Feedback'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the feedback to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_name': {'type': 'string'},
                    'feedback_text': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Feedback updated successfully"
        },
        404: {
            "description": "Feedback not found"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
})
def update_feedback(product_id):
    try:
        data = request.get_json()
        result = collection2.update_one({"product_id": product_id}, {"$set": data})
        if result.matched_count > 0:
            return jsonify({"message": "Feedback updated successfully"}), 200
        else:
            return jsonify({"error": "Feedback not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#PATCH (update feedback by ID)
# This endpoint updates feedback for a specific product by its ID in the database.
@app.route("/update_feedback/<int:product_id>", methods=["PATCH"])
@swag_from({
    'tags': ['Patch Feedback'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the feedback to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_name': {'type': 'string'},
                    'feedback_text': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': "Feedback updated successfully"
        },
        404: {
            "description": "Feedback not found"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
})
def patch_feedback(product_id):
    try:
        data = request.get_json()
        result = collection2.update_one({"product_id": product_id}, {"$set": data})
        if result.matched_count > 0:
            return jsonify({"message": "Feedback updated successfully"}), 200
        else:
            return jsonify({"error": "Feedback not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# DELETE (delete feedback by ID)
# This endpoint deletes feedback for a specific product by its ID from the database.
@app.route("/delete_feedback/<int:product_id>", methods=["DELETE"])
@swag_from({
    'tags': ['Delete Feedback'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the feedback to delete'
        }
    ],
    'responses': {
        200: {
            'description': "Feedback deleted successfully"
        },
        404: {
            "description": "Feedback not found"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
})
def delete_feedback(product_id):
    try:
        result = collection2.delete_one({"product_id": product_id})
        if result.deleted_count > 0:
            return jsonify({"message": "Feedback deleted successfully"}), 200
        else:
            return jsonify({"error": "Feedback not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET (analyze sentiments using TextBlob)
# This endpoint analyzes the sentiments of feedbacks based on their ratings.
@app.route("/analyze_sentiments/<int:product_id>", methods=["GET"])
@swag_from({
    'tags': ['Sentiment Analysis'],
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the product to analyze feedback for'
        }
    ],
    'responses': {
        200: {
            'description': 'Sentiment analysis completed using rating',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'analyzed_feedbacks': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer'},
                                'feedback_text': {'type': 'string'},
                                'rating': {'type': 'integer'},
                                'polarity': {'type': 'number'},
                                'sentiment': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        500: {'description': 'Internal Server Error'}
    }
})

def analyze_sentiments(product_id):
    try:
        # check if product exists
        if not collection.find_one({"product_id": product_id}):
            return jsonify({"error": "Product with this ID does not exist"}), 400
        # check if feedback exists
        if not collection2.find_one({"product_id": product_id}):
            return jsonify({"error": "No feedbacks found for this product ID"}), 404
         
        #fetch feedbacks for the product
        feedbacks = list(collection2.find({'product_id': product_id}))
        analyzed = []

        #analyze feedbacks using rating
        for feedback in feedbacks:
            rating = feedback.get('rating')
            if rating is None:
                continue  # Skip if no rating

            # Convert rating to sentiment and polarity-like score
            if rating >= 4:
                sentiment = "positive"
            elif rating == 3:
                sentiment = "neutral"
            else:
                sentiment = "negative"

            polarity = round((rating - 3) / 2, 2)  # Normalize to range -1 to +1
    
        # create processed feedback entry
            result = {
                'product_id': product_id,
                'feedback_text': feedback.get('feedback_text', ''),
                'rating': rating,
                'polarity': polarity,
                'sentiment': sentiment
            }

            analyzed.append(result)

        # STATS SECTION (calclate stats)
        # Calculate total feedbacks, average polarity, most positive and most negative feedbacks
        total_feedbacks = len(analyzed)
        avg_polarity = round(sum(f['polarity'] for f in analyzed) / total_feedbacks, 3) if total_feedbacks else 0
        
        most_positive = max(analyzed, key=lambda x: x['polarity'], default=None)
        most_negative = min(analyzed, key=lambda x: x['polarity'], default=None)

    #store stats in sentimentscore collection
    # Create a new document with the stats
        stats = {
            "product_id": product_id, 
            "total_feedbacks": total_feedbacks,
            "average_polarity": avg_polarity,
            "average_sentiment": "positive" if avg_polarity > 0.2 else "negative" if avg_polarity < -0.2 else "neutral",
            "most_positive_feedback": {
                "text": most_positive['feedback_text'] if most_positive else None,
                "polarity": most_positive['polarity'] if most_positive else None,
                "rating": most_positive['rating'] if most_positive else None
            } if most_positive else None,
            "most_negative_feedback": {
                "text": most_negative['feedback_text'] if most_negative else None,
                "polarity": most_negative['polarity'] if most_negative else None,
                "rating": most_negative['rating'] if most_negative else None
            } if most_negative else None
        }
        #update or insert stats in sentimentscore collection
        collection3.update_one(
            {"product_id": product_id},
            {"$set": stats},
            upsert=True
        )
        # Return the analyzed feedbacks and stats
        return jsonify({
            "message": "Sentiment analysis completed using rating",
            "analyzed_feedbacks": analyzed,
            "stats": stats
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
