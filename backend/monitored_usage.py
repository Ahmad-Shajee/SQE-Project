from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])

# Local MySQL Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "shajee"
app.config["MYSQL_DB"] = "video_streaming_app"

mysql = MySQL(app)

# Maximum allowed storage per user in bytes (50MB)
MAX_LIMIT = 50 * 1024 * 1024
DAILY_LIMIT = 100 * 1024 * 1024

@app.route("/api/usage/<int:user_id>", methods=["GET"])
def get_usage(user_id):
    try:
        cursor = mysql.connection.cursor()

        # Fetch total storage used
        cursor.execute(
            "SELECT COALESCE(SUM(file_size), 0) FROM uploads WHERE user_id = %s",
            (user_id,),
        )
        used_storage = cursor.fetchone()[0] or 0
        remaining_storage_mb = (MAX_LIMIT - used_storage) / (1024 * 1024)

        # Fetch today's bandwidth usage
        cursor.execute(
            """
            SELECT COALESCE(SUM(CASE WHEN action_type = 'upload' THEN file_size ELSE 0 END), 0)
            FROM user_logs
            WHERE user_id = %s AND DATE(action_date) = %s
            """,
            (user_id, datetime.now().date()),
        )
        used_bandwidth = cursor.fetchone()[0] or 0
        remaining_bandwidth_mb = (DAILY_LIMIT - used_bandwidth) / (1024 * 1024)

        cursor.close()

        return jsonify({
            "remainingStorage": f"{remaining_storage_mb:.2f} MB",
            "remainingBandwidth": f"{remaining_bandwidth_mb:.2f} MB",
        }), 200
    except Exception as e:
        print(f"Error fetching usage data: {e}")
        return jsonify({"message": "Error fetching usage data"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5004)
