from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)

# Local MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"  # Use local MySQL server
app.config["MYSQL_USER"] = "root"      # Update with your local MySQL user
app.config["MYSQL_PASSWORD"] = "shajee"  # Update with your local MySQL password
app.config["MYSQL_DB"] = "video_streaming_app"  # Local database name

mysql = MySQL(app)


@app.route("/update-username", methods=["POST"])
def update_username():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        new_username = data.get("username")

        if not user_id or not new_username:
            return jsonify({"message": "User ID and username are required"}), 400

        # Update username in the database
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE users SET username = %s WHERE id = %s", (new_username, user_id)
        )
        mysql.connection.commit()

        return jsonify({"message": "Username updated successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error updating username"}), 500


@app.route("/update-password", methods=["POST"])
def update_password():
    try:
        data = request.get_json()
        print("data",data)
        user_id = data.get("user_id")
        new_password = data.get("new_password")
        current_password = data.get("current_password")  # Added field to verify current password

        if not user_id or not new_password or not current_password:
            return jsonify({"message": "User ID, current password, and new password are required"}), 400

        # Fetch the user's current password from the database to verify it
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404

        stored_password = user[0]

        # Verify the current password
        if not check_password_hash(stored_password, current_password):
            return jsonify({"message": "Current password is incorrect"}), 401

        # Hash the new password before updating it
        hashed_password = generate_password_hash(new_password)

        # Update password in the database
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id)
        )
        mysql.connection.commit()

        return jsonify({"message": "Password updated successfully!"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error updating password"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5003)
