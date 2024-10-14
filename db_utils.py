import mysql.connector

def get_database_connection():
    return mysql.connector.connect(
        host="103.185.53.105",
        user="devsecop_user",  
        # password="Sthr33.c0.1d!", 
        password="C?%A{^2A~bBi", 
        database="devsecop_database"
    )