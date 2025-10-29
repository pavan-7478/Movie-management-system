from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
 
DATABASE_URL = "mysql+pymysql://pavan:Testing%40123@127.0.0.1:3306/project"
 
# pymysql is the driver which helps to connect to MySQL database with python
# create_engine function is used to create a connection to the database
 
engine = create_engine(DATABASE_URL)
 
# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Base class for ORM models 
Base = declarative_base()
# try:
#     Base.metadata.create_all(bind=engine)
# except Exception as e:
#     print("Error:", e)
#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
