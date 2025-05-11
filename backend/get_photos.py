import os
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])

# MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"
app.config["MYSQL_DB"] = "video_streaming_app"

# Local photo storage path
PHOTO_STORAGE_PATH = "C:/SEMESTER 6/5 - Software Quality Engineering/SQE Photos Videos Project"

mysql = MySQL(app)

# Ensure storage directory exists
if not os.path.exists(PHOTO_STORAGE_PATH):
    os.makedirs(PHOTO_STORAGE_PATH)


@app.route("/photos/<int:user_id>", methods=["GET"])
def get_photos_as_objects(user_id):
    """
    Fetch all photos for a specific user and return them as base64-encoded strings.
    """
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT upload_name FROM uploads WHERE user_id = %s AND type = 'photo'",
            (user_id,)
        )
        photo_names = cursor.fetchall()
        cursor.close()

        if not photo_names:
            return jsonify({"success": False, "message": "No photos found for this user."}), 404

        photos = []
        for photo_name_tuple in photo_names:
            filename = photo_name_tuple[0]
            photo_path = os.path.join(PHOTO_STORAGE_PATH, filename)

            if os.path.exists(photo_path):
                with open(photo_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read()).decode("utf-8")
                    photos.append({
                        "name": filename,
                        "content": encoded_string  # base64 string
                    })
            else:
                photos.append({
                    "name": filename,
                    "content": None,
                    "message": "Photo not found in storage."
                })

        return jsonify({"success": True, "photos": photos}), 200

    except Exception as e:
        print(f"Error retrieving photos: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred while retrieving photos."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5005)
