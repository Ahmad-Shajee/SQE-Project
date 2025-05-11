import base64
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__)

# Apply CORS to allow cross-origin requests (adjust as needed)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])  # Allowing all origins, specify specific origins as needed

# MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"  # Add username if needed
app.config["MYSQL_PASSWORD"] = "shajee"  # Replace with your MySQL password
app.config["MYSQL_DB"] = "video_streaming_app"  # Database name

mysql = MySQL(app)

# Path to store videos (update this based on your storage path)
VIDEO_STORAGE_PATH = "C:/SEMESTER 6/5 - Software Quality Engineering/SQE Photos Videos Project"  # Adjust to your actual video storage path

@app.route("/videos/names/<int:userId>", methods=["GET"])
def get_video_metadata(userId):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT id, upload_name, upload_url, type FROM uploads WHERE type = 'video' AND user_id = %s",
            (userId,)
        )

        # Fetch all the video metadata
        videos = cursor.fetchall()
        cursor.close()

        if videos:
            # Remove 'upload_data' field from the metadata to avoid sending large binary data
            for video in videos:
                video.pop("upload_data", None)
            return jsonify({"video_metadata": videos}), 200

        return jsonify({"message": "No videos found"}), 404
    except Exception as e:
        print(f"Error fetching video metadata: {str(e)}")
        return jsonify({"message": "An unexpected error occurred."}), 500

@app.route("/videos/<int:video_id>", methods=["GET"])
def get_video_by_id(video_id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT upload_url FROM uploads WHERE id = %s", (video_id,))
        
        # Fetch the video data for the given ID
        video = cursor.fetchone()
        cursor.close()

        if video:
            # Get the path of the video file
            video_path = os.path.join(VIDEO_STORAGE_PATH, video["upload_url"])

            # Check if the video file exists
            if os.path.exists(video_path):
                # Open and read the video file as binary
                with open(video_path, "rb") as f:
                    encoded_video = base64.b64encode(f.read()).decode("utf-8")

                # Return the base64 encoded video as a JSON response
                return jsonify({"video_data": encoded_video}), 200

            return jsonify({"message": "Video file not found in storage"}), 404

        return jsonify({"message": "Video not found"}), 404

    except Exception as e:
        print(f"Error fetching video by ID: {str(e)}")
        return jsonify({"message": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5008)
