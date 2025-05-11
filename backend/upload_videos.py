import base64
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

# Add the parent directory to sys.path to import limit checks
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from limit_checks.daily_limit import check_daily_limit
from limit_checks.max_limit import check_max_limit

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"

# MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"
app.config["MYSQL_DB"] = "video_streaming_app"

mysql = MySQL(app)

# Enable Cross-Origin Resource Sharing
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])

# Set the folder where uploaded videos will be saved
UPLOAD_FOLDER = os.path.join("C:/SEMESTER 6/5 - Software Quality Engineering/SQE Photos Videos Project")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed video formats
ALLOWED_EXTENSIONS = {"mp4", "mkv", "avi", "mov"}

def allowed_file(filename):
    """Check if the file has an allowed video extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/videos/upload", methods=["POST"])
def upload_video_endpoint():
    return upload_video(request, mysql)


def upload_video(request, mysql):
    """Handle video upload, save to local folder, update DB, and log the action."""
    try:
        user_id = int(request.form.get("user_id"))
        video_file = request.files.get("video")

        if not video_file:
            return jsonify({"message": "No video file found in the request"}), 400

        if not allowed_file(video_file.filename):
            return jsonify({"message": "Unsupported file type"}), 400

        # Get video size and reset pointer
        video_size = len(video_file.read())
        video_file.seek(0)

        # Check max and daily upload limits
        is_allowed, message = check_max_limit(user_id, video_size, mysql)
        if not is_allowed:
            return jsonify({"success": False, "message": message}), 400

        is_allowed, message = check_daily_limit(user_id, video_size, mysql)
        if not is_allowed:
            return jsonify({"success": False, "message": message}), 400

        # Save file locally
        filename = secure_filename(f"{video_file.filename}")
        local_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        video_file.save(local_path)

        formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save upload metadata to DB
        cursor = mysql.connection.cursor()
        cursor.execute(
            """ 
            INSERT INTO uploads (user_id, file_size, upload_name, upload_url, upload_date, type)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (user_id, video_size, filename, local_path, formatted_datetime, "video"),
        )
        mysql.connection.commit()

        # Log upload in user_logs table
        cursor.execute(
            """
            INSERT INTO user_logs (user_id, action_type, file_size, action_date)
            VALUES (%s, %s, %s, %s);
            """,
            (user_id, "upload", video_size, formatted_datetime),
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "message": "Video uploaded and logged successfully!",
            "file_path": local_path
        }), 200

    except Exception as e:
        print("Upload Error:", str(e))
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@app.route("/videos/<filename>")
def serve_video(filename):
    """Serve video files from local storage."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
