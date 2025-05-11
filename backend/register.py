from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mysqldb import MySQL
from mysql.connector import Error
from werkzeug.security import generate_password_hash

app = Flask(__name__)
# Enable CORS for all routes
CORS(
    app, origins="*", methods=["GET", "POST", "PUT", "DELETE"]
)  # You can specify the allowed origins and methods here

# MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"  # Add username if needed
app.config["MYSQL_PASSWORD"] = "shajee"  # Replace with your MySQL password
app.config["MYSQL_DB"] = "video_streaming_app"  # Database name
app.config["SECRET_KEY"] = "your_secret_key_here"

# Initialize MySQL and JWT manager
mysql = MySQL(app)
jwt = JWTManager(app)


# Route to register a user
@app.route("/register", methods=["POST"])
def register():
    try:
        return register_user(request, mysql)
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


def register_user(request, mysql):
    data = request.get_json()

    # Validate input data
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing required fields!"}), 400

    # Check if user already exists
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"message": "User already exists!"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password),
        )
        mysql.connection.commit()

        # Fetch the newly created user's ID
        user_id = cursor.lastrowid

        # Generate JWT token (optional)
        access_token = create_access_token(identity=email)
        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "userId": user_id,
                    "access_token": access_token,
                }
            ),
            201,
        )

    except Error as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    finally:
        cursor.close()


if __name__ == "__main__":
    app.run(debug=True, port=5002)

