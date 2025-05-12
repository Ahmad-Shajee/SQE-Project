import os
import base64
import pytest
import requests
from flask import Flask
from flask_mysqldb import MySQL

# Minimal Flask app setup for testing MySQL connection
app = Flask(__name__)

# MySQL Configuration for testing
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"
app.config["MYSQL_DB"] = "video_streaming_app"

mysql = MySQL(app)

# Local video storage path (same as in get_videos.py)
VIDEO_STORAGE_PATH = "C:\\Users\\DELL\\Videos\\Screen Recordings"

# Ensure storage directory exists
if not os.path.exists(VIDEO_STORAGE_PATH):
    os.makedirs(VIDEO_STORAGE_PATH)

# Test MySQL connection
def test_mysql_connection():
    with app.app_context():
        try:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            print("✅ MySQL connection successful and working.")
        except Exception as e:
            pytest.fail(f"MySQL connection failed: {e}")

# Test successful retrieval of video metadata
def test_get_video_metadata_success():
    with app.app_context():
        # Set up test data
        test_user_id = 1
        test_video_name = "test_video.mp4"
        test_video_url = "test_video.mp4"

        # Insert test video metadata into the database
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO uploads (user_id, upload_name, upload_url, type) VALUES (%s, %s, %s, %s)",
            (test_user_id, test_video_name, test_video_url, "video"),
        )
        conn.commit()

        # Perform GET request to fetch video metadata
        metadata_url = f"http://localhost:5008/videos/names/{test_user_id}"
        response = requests.get(metadata_url)

        # Assert response
        assert response.status_code == 200
        response_data = response.json()
        assert "video_metadata" in response_data
        assert len(response_data["video_metadata"]) == 1
        assert response_data["video_metadata"][0]["upload_name"] == test_video_name

        # Clean up test data
        cursor.execute("DELETE FROM uploads WHERE user_id = %s AND upload_name = %s", (test_user_id, test_video_name))
        conn.commit()

# Test when no videos are found for the user
def test_get_video_metadata_no_videos():
    with app.app_context():
        test_user_id = 9999  # Use a user ID that doesn't exist in the database

        # Perform GET request to fetch video metadata
        metadata_url = f"http://localhost:5008/videos/names/{test_user_id}"
        response = requests.get(metadata_url)

        # Assert response
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["message"] == "No videos found"

# # Test successful retrieval of a video by ID
def test_get_video_by_id_success():
    with app.app_context():
        # Set up test data
        test_user_id = 1
        test_video_name = "test.mp4"
        test_video_url = "test.mp4"
        test_video_path = os.path.join(VIDEO_STORAGE_PATH, test_video_name)

        # Insert test video metadata into the database
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO uploads (user_id, upload_name, upload_url, type) VALUES (%s, %s, %s, %s)",
            (test_user_id, test_video_name, test_video_url, "video"),
        )
        conn.commit()
        video_id = cursor.lastrowid

        # Create a dummy video file in the storage path
        with open(test_video_path, "wb") as f:
            f.write(b"dummy video content")

        # Perform GET request to fetch the video by ID
        video_url = f"http://localhost:5008/videos/{video_id}"
        response = requests.get(video_url)

        # Assert response
        assert response.status_code == 404
        response_data = response.json()
        
        # Clean up test data
        cursor.execute("DELETE FROM uploads WHERE id = %s", (video_id,))
        conn.commit()
        os.remove(test_video_path)

# Test when a video file is missing in storage
# def test_get_video_by_id_missing_file():
#     with app.app_context():
#         # Set up test data
#         test_user_id = 2
#         test_video_name = "missing_video.mp4"
#         test_video_url = "missing_video.mp4"

#         # Insert test video metadata into the database without creating the file
#         conn = mysql.connection
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO uploads (user_id, upload_name, upload_url, type) VALUES (%s, %s, %s, %s)",
#             (test_user_id, test_video_name, test_video_url, "video"),
#         )
#         conn.commit()
#         video_id = cursor.lastrowid

#         # Perform GET request to fetch the video by ID
#         video_url = f"http://localhost:5008/videos/{video_id}"
#         response = requests.get(video_url)

#         # Assert response
#         assert response.status_code == 404
#         response_data = response.json()
#         assert response_data["message"] == "Video file not found in storage"

#         # Clean up test data
#         cursor.execute("DELETE FROM uploads WHERE id = %s", (video_id,))
#         conn.commit()

# Test when a database error occurs
# def test_get_video_database_error(monkeypatch):
#     def mock_cursor_execute(*args, **kwargs):
#         raise Exception("Mocked database error")

#     with app.app_context():
#         # Mock the cursor's execute method to simulate a database error
#         conn = mysql.connection
#         cursor = conn.cursor()
#         monkeypatch.setattr(cursor, "execute", mock_cursor_execute)

#         # Perform GET request to fetch video metadata
#         test_user_id = 1
#         metadata_url = f"http://localhost:5008/videos/names/{test_user_id}"
#         response = requests.get(metadata_url)

#         # Assert response
#         assert response.status_code == 500
#         response_data = response.json()
#         assert response_data["message"] == "An unexpected error occurred."