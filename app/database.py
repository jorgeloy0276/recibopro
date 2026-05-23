import mysql.connector
from config import Config

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
            )
        # print( f'Estado de conexion:  {connection.is_connected()}')
        return connection
    except mysql.connector.Error as error:
        # print(' ERROR MYSQL --> Failed to  connect to MySQL server {}'.format(error))
        messages = error
        print(messages)
        return messages


