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

# Test successful user registration
def test_register_success():
    with app.app_context():
        # Set up test data
        test_username = "TestUser"
        test_email = "testuser@example.com"
        test_password = "testpassword"

        # Perform registration request
        register_url = "http://localhost:5002/register"
        response = requests.post(
            register_url,
            json={
                "username": test_username,
                "email": test_email,
                "password": test_password,
            },
        )

        # Assert response
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["message"] == "User registered successfully"
        assert "userId" in response_data
        assert "access_token" in response_data

        # Clean up test data
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
        conn.commit()

# Test registration with missing fields
@pytest.mark.parametrize(
    "payload, expected_message",
    [
        ({"email": "testuser@example.com", "password": "testpassword"}, "Missing required fields!"),
        ({"username": "TestUser", "password": "testpassword"}, "Missing required fields!"),
        ({"username": "TestUser", "email": "testuser@example.com"}, "Missing required fields!"),
    ],
)
def test_register_missing_fields(payload, expected_message):
    register_url = "http://localhost:5002/register"
    response = requests.post(register_url, json=payload)

    # Assert response
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["message"] == expected_message

# # Test registration with duplicate email
def test_register_duplicate_user():
    with app.app_context():
        # Set up test data
        test_username = "TestUser"
        test_email = "duplicateuser@example.com"
        test_password = "testpassword"
        hashed_password = generate_password_hash(test_password)

        # Insert duplicate user into the database
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (test_username, test_email, hashed_password),
        )
        conn.commit()

        # Perform registration request
        register_url = "http://localhost:5002/register"
        response = requests.post(
            register_url,
            json={
                "username": test_username,
                "email": test_email,
                "password": test_password,
            },
        )

        # Assert response
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["message"] == "User already exists!"

        # Clean up test data
        cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
        conn.commit()