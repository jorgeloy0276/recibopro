import os
from dotenv import load_dotenv


load_dotenv()
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'receipts_db'
    MYSQL_PORT =  os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_CURSORCLASS = 'DictCursor'
    MYSQL_SSL_CA=os.environ.get('MYSQL_SSL_CA')
    MAIL_SERVER =  os.environ.get('MAIL_SERVER') or 'smtp.server.com'
    MAIL_PORT =  os.environ.get('MAIL_PORT')or 111
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() in ["true", "1", "yes"]
    # MAIL_USE_TLS =False
    # MAIL_USE_SSL = True
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 'False'
    # MAIL_USE_SSL =  os.environ.get('MAIL_USE_SSL') or 'True'
    MAIL_USERNAME =  os.environ.get('MAIL_USERNAME') or 'tucorreo@correo.com'
    MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD') or 'tu password'
