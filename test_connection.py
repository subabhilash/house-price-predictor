import psycopg2

def test_database():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="house_price_app",
            user="app_user",
            password="abhi"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database();")
        result = cursor.fetchone()
        
        print("✅ Database Connection Successful!")
        print(f"User: {result[0]}")
        print(f"Database: {result[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database()
