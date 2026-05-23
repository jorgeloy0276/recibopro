from flask import Flask
# Nueva forma
import mysql.connector

#Antigua flask_mysqldb depende de C++ 
# from flask_mysqldb import MySQL
import os


from config import Config
from flask_mail import Mail
mail = Mail()

#Antigua flask_mysqldb
# mysql = MySQL()


def create_app():
    app = Flask(__name__)
    # Si se desea que la carpeta de vistas sea difrerente a templates usar:
    #app = Flask(__name__, template_folder='views')

    app.config.from_object(Config)

    #Inicializa objeto de MySQL
    #Antigua flask_mysqldb
    # mysql.init_app(app)

    # Inicializamos mail con la app
    mail.init_app(app)

    # Crear carpeta de exportación si no existe
    export_dir = os.path.join(app.root_path, 'static', 'export')
    os.makedirs(export_dir, exist_ok=True)

    from app.routes.receipts_routes import receipt_bp
    from app.routes.receipts_routes import pdf_bp
    from app.routes.receipts_routes import email_bp

    app.register_blueprint(receipt_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(email_bp)
    return app
