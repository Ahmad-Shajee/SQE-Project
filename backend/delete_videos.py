import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"], allow_headers="*")

# MySQL configuration (for flask_mysqldb)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"  # Replace with actual password
app.config["MYSQL_DB"] = "video_streaming_app"

mysql = MySQL(app)

# Local video storage path
VIDEO_STORAGE_PATH = "C:/SEMESTER 6/5 - Software Quality Engineering/SQE Photos Videos Project"

@app.route("/videos/delete/<int:video_id>", methods=["DELETE"])
def delete_video_endpoint(video_id):
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    try:
        user_id = int(user_id)
        return delete_video(video_id, user_id)
    except ValueError:
        return jsonify({"message": "Invalid User ID"}), 400


def delete_video(video_id, user_id):
    try:
        cursor = mysql.connection.cursor()

        # Fetch file_size and filename
        cursor.execute("SELECT file_size, upload_name FROM uploads WHERE id = %s", (video_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "Video not found"}), 404

        file_size, filename = result
        video_file_path = os.path.join(VIDEO_STORAGE_PATH, filename)

        if not os.path.exists(video_file_path):
            return jsonify({"message": "Video file not found in local storage"}), 404

        os.remove(video_file_path)
        print(f"Deleted video file: {filename}")

        # Delete from DB
        cursor.execute("DELETE FROM uploads WHERE id = %s AND user_id = %s", (video_id, user_id))
        mysql.connection.commit()

        # Log deletion
        cursor.execute("""
            INSERT INTO user_logs (user_id, action_type, file_size, action_date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, "delete_video", file_size, datetime.now()))
        mysql.connection.commit()

        cursor.close()
        return jsonify({"message": "Video deleted successfully"}), 200

    except Exception as e:
        print(str(e))
        try:
            if cursor:
                cursor.execute("""
                    INSERT INTO user_logs (user_id, action_type, action_date)
                    VALUES (%s, %s, %s)
                """, (user_id, f"error_deleting_video: {str(e)}", datetime.now()))
                mysql.connection.commit()
        except:
            pass
        return jsonify({"message": f"Error deleting video: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5009)
