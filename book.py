from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from bson import ObjectId  # To handle ObjectId in JSON responses

# Connect to MongoDB
client = MongoClient('mongodb+srv://<username>:<password>@cluster0.uxgbf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['book_database']
collection = db['books']

try:
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Create (POST) operation
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    last_book = collection.find_one(sort=[("id", -1)])  # หา id ที่มากสุด
    new_id = (last_book["id"] + 1) if last_book else 1

    new_book = {
    "id": new_id,
    "title": data["title"],
    "author": data["author"],
    "image_url": data["image_url"]
}

    result = collection.insert_one(new_book)
    new_book['_id'] = str(result.inserted_id)  # Convert ObjectId to string for JSON compatibility
    return jsonify(new_book), 201

# Read (GET) operation - Get all books
@app.route('/books', methods=['GET'])
@cross_origin()
def get_all_books():
    books = collection.find()  # ดึงข้อมูลจาก MongoDB
    result = []
    for book in books:
        book['_id'] = str(book['_id'])  # แปลง ObjectId เป็น string
        book['id'] = book.get('id', None)  # เพิ่ม id แบบตัวเลข
        result.append(book)
    return jsonify({"books": result})


# Read (GET) operation - Get a specific book by ID
@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = collection.find_one({"_id": ObjectId(book_id)})  # Query by ObjectId
        if book:
            book['_id'] = str(book['_id'])  # Convert ObjectId to string for JSON compatibility
            return jsonify(book)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format"}), 400

# Update (PUT) operation
@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.get_json()
        result = collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": data}
        )
        if result.matched_count > 0:
            updated_book = collection.find_one({"_id": ObjectId(book_id)})
            updated_book['_id'] = str(updated_book['_id'])
            return jsonify(updated_book)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format"}), 400

# Delete operation
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        result = collection.delete_one({"_id": ObjectId(book_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Book deleted successfully"})
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": "Invalid ID format"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
