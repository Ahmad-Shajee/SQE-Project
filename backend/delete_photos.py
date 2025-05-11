import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"], allow_headers="*")

# MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"  # Use local MySQL host
app.config["MYSQL_USER"] = "root"      # Update with your local MySQL user
app.config["MYSQL_PASSWORD"] = "shajee"  # Update with your local MySQL password
app.config["MYSQL_DB"] = "video_streaming_app"  # Local database name

mysql = MySQL(app)

@app.route("/photos/delete/<string:photo_id>", methods=["DELETE"])
def delete_photo_endpoint(photo_id):
    """Endpoint to delete a photo."""
    user_id = request.args.get("user_id")  # Get the user_id from query parameters

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    try:
        user_id = int(user_id)  # Ensure user_id is an integer
        return delete_photo(photo_id, user_id)
    except ValueError:
        return jsonify({"message": "Invalid User ID"}), 400


def delete_photo(photo_id, user_id):
    """Delete a photo file and its database record, and log the action."""
    cursor = None
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        # Fetch the file size and local file path before deleting from DB
        cursor.execute(
            "SELECT file_size, upload_url FROM uploads WHERE user_id = %s AND upload_name = %s",
            (user_id, photo_id),
        )
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "Photo not found"}), 404

        file_size, file_path = result

        # Attempt to delete the actual file (if it exists)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not delete file from disk: {e}")

        # Delete photo record from uploads table
        cursor.execute(
            "DELETE FROM uploads WHERE upload_name = %s AND user_id = %s",
            (photo_id, user_id),
        )
        conn.commit()

        # Log the deletion in user_logs
        cursor.execute(
            """
            INSERT INTO user_logs (user_id, action_type, file_size, action_date)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, "delete", file_size, datetime.now()),
        )
        conn.commit()

        return jsonify({"message": "Photo deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Error deleting photo: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()

if __name__ == "__main__":
    app.run(debug=True, port=5006)
