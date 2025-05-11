from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_mysqldb import MySQL
from mysql.connector import Error
from werkzeug.security import check_password_hash
from datetime import timedelta 

# Set up Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# JWT Config
app.config["SECRET_KEY"] = "your_secret_key_here"  # Replace with a secure key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Set token expiration time
jwt = JWTManager(app)

# Local MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"  # Add your local password if needed
app.config["MYSQL_DB"] = "video_streaming_app"

mysql = MySQL(app)

# Login Route
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Missing required fields!"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, username, email, password FROM users WHERE email = %s", (email,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found!"}), 404

        id, username, email, stored_password = user

        # Verify password with hashed password
        if check_password_hash(stored_password, password):
            access_token = create_access_token(identity=email)
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "username": username,
                "userId": id,
            }), 200
        else:
            return jsonify({"message": "Invalid password!"}), 401

    except Error as db_error:
        return jsonify({"message": f"Database error: {str(db_error)}"}), 500
    except Exception as e:
        print("error", str(e))
        return jsonify({"message": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
