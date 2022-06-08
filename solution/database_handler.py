from sqlalchemy import create_engine, Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


# The user logins table model that exists within the Postgresql database
# Defined here using the ORM
base = declarative_base()
class UserLogin(base):
    __tablename__ = "user_logins"
    user_id = Column(String, primary_key=True)
    device_type = Column(String)
    masked_ip = Column(String)
    masked_device_id = Column(String)
    locale = Column(String)
    app_version = Column(String)
    create_date = Column(Date, default=func.now())


# The database handler that the login_processor will instantiate and utilize to interact with the user_logins table
class UserDatabaseHandler:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def insert_logins(self, logins: dict):
        # Instantiate a SQLAlchemy session with the database
        with Session(self.engine) as session:
            # For each login dict in the logins list, assign it an entry within the user_logins table
            # Since we formatted the login dictionary to match the columns in the table, we can pass the dict keys and values as named arguments using the doublestar operator
            for login in logins:
                login_entry = UserLogin(**login)
                session.add(login_entry)
            session.commit() # Commit entries all at once-- rolling back if any one entry throws an error