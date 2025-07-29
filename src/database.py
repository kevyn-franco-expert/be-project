import mysql.connector
from mysql.connector import Error
from src.config import Config

class DatabaseManager:
    def __init__(self):
        self.config = Config.DB_CONFIG
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=False):
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
            
            return result
        except Error as e:
            print(f"Database error: {e}")
            connection.rollback()
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()