import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from limit_checks.daily_limit import check_daily_limit
from limit_checks.max_limit import check_max_limit
from werkzeug.utils import secure_filename

# Flask App setup
app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])

# MySQL Database Configuration (LOCAL)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"  # Update if needed
app.config["MYSQL_DB"] = "video_streaming_app"
mysql = MySQL(app)

# Local uploads folder defined as a simple string (no os module used)
UPLOAD_FOLDER = "C:/SEMESTER 6/5 - Software Quality Engineering/SQE Photos Videos Project"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/photos/upload", methods=["POST"])
def upload_photo():
    try:
        if "photo" not in request.files:
            return jsonify({"message": "No file part"}), 400

        photo = request.files["photo"]
        user_id = request.form.get("user_id")

        if photo.filename == "":
            return jsonify({"message": "No selected file"}), 400

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            file_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"
            photo_data = photo.read()
            photo_size = len(photo_data)

            # Check max and daily limits
            is_allowed, message = check_max_limit(user_id, photo_size, mysql)
            if not is_allowed:
                return jsonify({"success": False, "message": message}), 400

            is_allowed, message = check_daily_limit(user_id, photo_size, mysql)
            if not is_allowed:
                return jsonify({"success": False, "message": message}), 400

            # Save the file locally
            with open(file_path, "wb") as f:
                f.write(photo_data)

            # Generate local URL or path
            local_path = os.path.join(UPLOAD_FOLDER, filename)


            # Save metadata in MySQL
            cursor = mysql.connection.cursor()
            cursor.execute(
                """
                INSERT INTO uploads (user_id, file_size, upload_name, upload_url, upload_date, type)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, photo_size, filename, local_path, datetime.now(), "photo"),
            )
            mysql.connection.commit()

            # Log the upload
            cursor.execute(
                """
                INSERT INTO user_logs (user_id, action_type, file_size, action_date)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, "upload", photo_size, datetime.now()),
            )
            mysql.connection.commit()
            cursor.close()

            return jsonify(
                {
                    "success": True,
                    "message": "Photo uploaded successfully!",
                    "url": local_path,
                }
            ), 200
        else:
            return jsonify(
                {"message": "Invalid file type. Only JPG, PNG, and GIF are allowed."}
            ), 400
    except Exception as e:
        print(f"Error uploading photo: {str(e)}")
        return jsonify({"message": "An error occurred while uploading the photo."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5007)
