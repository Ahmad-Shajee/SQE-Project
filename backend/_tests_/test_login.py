import pytest
import requests
from flask import Flask
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

# Minimal Flask app setup for testing MySQL connection
app = Flask(__name__)

# MySQL Configuration for testing
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"
app.config["MYSQL_DB"] = "video_streaming_app"

mysql = MySQL(app)

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

# Test login functionality
def test_login_functionality():
    with app.app_context():
        # Set up test data
        test_email = "testuser@example.com"
        test_password = "testpassword"
        hashed_password = generate_password_hash(test_password)

        # Insert test user into the database
        try:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                ("TestUser", test_email, hashed_password),
            )
            conn.commit()

            # Perform login request
            login_url = "http://localhost:5001/login"
            response = requests.post(
                login_url,
                json={"email": test_email, "password": test_password},
            )

            # Assert response
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["message"] == "Login successful"
            assert "access_token" in response_data

        finally:
            # Clean up test data
            cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
            conn.commit()