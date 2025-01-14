import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")  
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("testsheet30@gmail.com")
    MAIL_PASSWORD = os.getenv("Testsheet303030")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME