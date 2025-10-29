from app.models.user import User
from app.core.security import PasswordManager
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, role: str, password: str):
        repo = UserRepository(self.db)

        if repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email already exists")

        if not PasswordManager.is_strong_password(password):
            raise HTTPException(
                status_code=400,
                detail="Password too weak. Must be 8+ chars, include uppercase, lowercase, number & special char."
            )

        new_user = User(
            username=username,
            email=email,
            role=role,
            password=PasswordManager.hash_password(password)
        )
        return repo.create(new_user)

    def list_users(self):
        repo = UserRepository(self.db)
        return repo.list()
