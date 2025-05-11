from datetime import date
DAILY_LIMIT = 100 * 1024 * 1024  # 100MB

def check_daily_limit(user_id, file_size, connection):
    try:
        cursor = connection.connection.cursor()
        # Query to calculate daily bandwidth
        query = """
                SELECT 
                    COALESCE(SUM(CASE WHEN action_type = 'upload' THEN file_size ELSE 0 END), 0) 
                    AS daily_bandwidth
                    FROM user_logs
                    WHERE user_id = %s AND action_date = %s;
            """
        today = date.today()
        cursor.execute(query, (user_id, today))
        daily_bandwidth = cursor.fetchone()[0]  # Fetch the calculated bandwidth
        print("daily_bandwidth",daily_bandwidth)
        # Check if adding the new file exceeds the daily limit
        if daily_bandwidth + file_size > DAILY_LIMIT:
                return False, f"Daily limit exceeded. You can upload up to {DAILY_LIMIT - daily_bandwidth} bytes more today."

        return True, "Upload is within the daily limit."
    except Exception as e:
        return False, f"Error checking daily limit: {str(e)}"

