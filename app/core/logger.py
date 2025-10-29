import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIRS= "logs"
os.makedirs(LOG_DIRS, exist_ok= True)

# Naming the logger
logger = logging.getLogger("AuthLogger")
logger.setLevel(logging.DEBUG)

# Now we make a custom logger to handle all the auth_logging

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] [%(module)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Rotating File Handler
file_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIRS, "auth.log"),
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=3
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

