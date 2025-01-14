from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'login' 
migrate = Migrate()