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

# Local photo storage path (same as in get_photos.py)
PHOTO_STORAGE_PATH = "C:\\Users\\DELL\\Desktop"

# Ensure storage directory exists
if not os.path.exists(PHOTO_STORAGE_PATH):
    os.makedirs(PHOTO_STORAGE_PATH)

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

# Test successful retrieval of photos
def test_get_photos_success():
    with app.app_context():
        # Set up test data
        test_user_id = 1
        test_photo_name = "test_photo.jpg"
        print("Photo storage path: ", PHOTO_STORAGE_PATH)
        test_photo_path = os.path.join(PHOTO_STORAGE_PATH, test_photo_name)

        # Insert test photo record into the database
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO uploads (user_id, upload_name, type) VALUES (%s, %s, %s)",
            (test_user_id, test_photo_name, "photo"),
        )
        conn.commit()

        # Create a dummy photo file in the storage path
        with open(test_photo_path, "wb") as f:
            f.write(b"dummy photo content")

        # Perform GET request to fetch photos
        photos_url = f"http://localhost:5005/photos/{test_user_id}"
        response = requests.get(photos_url)

        # Assert response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["photos"][0]["name"] == test_photo_name
        
        # Clean up test data
        cursor.execute("DELETE FROM uploads WHERE user_id = %s AND upload_name = %s", (test_user_id, test_photo_name))
        conn.commit()
        os.remove(test_photo_path)

# Test when no photos are found for the user
def test_get_photos_no_photos():
    with app.app_context():
        test_user_id = 9999  # Use a user ID that doesn't exist in the database

        # Perform GET request to fetch photos
        photos_url = f"http://localhost:5005/photos/{test_user_id}"
        response = requests.get(photos_url)

        # Assert response
        assert response.status_code == 404
        response_data = response.json()
        assert response_data["success"] is False
        assert response_data["message"] == "No photos found for this user."

# # Test when a photo file is missing in storage
def test_get_photos_missing_file():
    with app.app_context():
        # Set up test data
        test_user_id = 2
        test_photo_name = "missing_photo.jpg"

        # Insert test photo record into the database without creating the file
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO uploads (user_id, upload_name, type) VALUES (%s, %s, %s)",
            (test_user_id, test_photo_name, "photo"),
        )
        conn.commit()

        # Perform GET request to fetch photos
        photos_url = f"http://localhost:5005/photos/{test_user_id}"
        response = requests.get(photos_url)

        # Assert response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert len(response_data["photos"]) == 1
        assert response_data["photos"][0]["name"] == test_photo_name
        assert response_data["photos"][0]["content"] is None
        assert response_data["photos"][0]["message"] == "Photo not found in storage."

        # Clean up test data
        cursor.execute("DELETE FROM uploads WHERE user_id = %s AND upload_name = %s", (test_user_id, test_photo_name))
        conn.commit()