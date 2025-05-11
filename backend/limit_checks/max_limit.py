# Maximum allowed total storage per user in bytes (50MB)
MAX_LIMIT = 50 * 1024 * 1024  # 50MB

def check_max_limit(user_id, file_size, mysql):
    try:
        # Get a cursor from the MySQL connection
        cursor = mysql.connection.cursor()

        # Query to calculate total uploads for the user
        query = """
            SELECT COALESCE(SUM(file_size), 0) 
            FROM uploads 
            WHERE user_id = %s;
        """
        cursor.execute(query, (user_id,))
        total_usage = cursor.fetchone()[0]  # Fetch the sum or default to 0

        # Check if adding the new file exceeds the max limit
        if total_usage + file_size > MAX_LIMIT:
            return False, f"Total storage limit exceeded. You can upload up to {MAX_LIMIT - total_usage} bytes more."

        return True, "Upload is within the maximum limit."
    except Exception as e:
        print(str(e))
        return False, f"Error checking max limit: {str(e)}"

