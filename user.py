from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Model użytkownika
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    
    def delete(self, session):
        session.delete(self)
        session.commit()

# Tworzenie nowego użytkownika
def create_user(first_name, last_name, username, email, password, session):
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password
    )
    session.add(new_user)
    session.commit()
    return new_user

# Pobranie użytkownika po ID
def get_user_by_id(user_id, session):
    return session.query(User).filter_by(user_id=user_id).first()

# Edycja danych użytkownika(haslo)
def change_user_password(user_id, new_password, session):
    user = get_user_by_id(user_id)
    if user:
        user.password = new_password
        session.commit()
        return True
    return False

# Usunięcie użytkownika
def delete_user(user_id, session):
    user = get_user_by_id(user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


# Pobranie wszystkich użytkowników
def get_all_users(session):
    return session.query(User).all()
