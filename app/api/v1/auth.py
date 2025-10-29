"""
This module handles authentication functionality, including login, token
management, and user verification for the application.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer 
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserLogins
from app.schemas.user import UserCreate, UserLogin
from app.services.user import UserService
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
#from jose import jwt, JWTError
from app.core.security import PasswordManager, JWTManager
from app.utils.decorators import login_required, admin_required
from app.db.session import get_db 
from app.core.logger import logger


router = APIRouter(prefix="/auth")
security = HTTPBearer()

# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# ----------------- Register -----------------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    This route is for user registration
    """
    logger.info({
                "message":"User registration has started",
                "timestamp": datetime.utcnow().isoformat()
                })
    service = UserService(db)
    created_user = service.create_user(user.username, user.email, user.role, user.password)
    logger.info({
            "event": "user_registered",
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "timestamp": datetime.utcnow().isoformat()
        })

    return {"message":"User registered successfully"}

# ------------------Get all users --------------
@router.get("/get_users", dependencies=[Depends(security)])
@admin_required
def get_users(request:Request,db: Session = Depends(get_db)):
    """
    Route for getting all the users details generally only for admins
    """
    logger.info({
             "message":"Getting the info of all the users",
             "timestamp": datetime.utcnow().isoformat()
             })
    service= UserService(db)
    users= service.list_users()
    logger.info({
        "event": "admin_view_users",
        "admin": request.state.user.username,
        "total_users": len(users),
        "timestamp": datetime.utcnow().isoformat()
    })

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at,
        }
        for u in users
    ]



# ----------------- Login -----------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
   
    """
         This is the login route
    """
    logger.info({
              "message":"Logging route request received",
              "timestamp": datetime.utcnow().isoformat()
        }) 

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not db_user.verify_password(user.password):
        logger.warning({
                    "message":"Error in verify password or user access",
                    "timestamp": datetime.utcnow().isoformat()    
                        })
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = JWTManager.create_jwt({"user_id": db_user.id, "role": db_user.role})
   # db_user.status= "active"
    # Save login record
    login_record = UserLogins(
        user_id=db_user.id,
        token=token,
        expiration_date=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # We should even set the status of User table
    db_user.status= "active"
    db.add(login_record)
    db.commit()
    db.refresh(login_record)
    db.refresh(db_user)

    logger.info({
        "event": "login_success",
        "user_id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "access_token": token, 
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role,
            "status": db_user.status
        }
        }

# ----------------- Protected route -----------------
@router.get("/me",dependencies=[Depends(security)])
@login_required
async def me(request: Request):
    user = request.state.user
    logger.debug({
        "event": "user_profile_accessed",
        "user_id": user.id,
        "username": user.username,
        "timestamp": datetime.utcnow().isoformat()
    })
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status
    }

#---------------Logout route-------------------------
@router.post("/logout", dependencies=[Depends(security)])
def logout(request: Request,db: Session=Depends(get_db)):
    
    """
    Route for logout with the auth-credentials which is the access token
    """
    logger.info({
                "message":"Logout route accessed",
                "timestamp": datetime.utcnow().isoformat()
                 }) 
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None

    if not token:
        logger.warning({
            "event": "logout_failed",
            "reason": "missing_token",
            "timestamp": datetime.utcnow().isoformat()
        })
        raise HTTPException(status_code=401, detail="Token missing")

    #Handling user logins table
    login_record= db.query(UserLogins).filter(UserLogins.token == token).first()
    users= db.query(UserLogins).filter(UserLogins.user_id == login_record.user_id).all()
    
    if not login_record or login_record.status == "suspended":
        logger.warning({
            "message":"Check for login record and user can be suspended",
            "timestamp": datetime.utcnow().isoformat()            
            })
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= "Check for login record and user can be suspended")
    
    for user in users:
        user.status= "suspended"

    # We should even handle the user table by changing its status
    User_update_record = db.query(User).filter(User.id == login_record.user_id).first()
    if not User_update_record:
       raise HTTPException(status_code=404, detail="User not found")

    User_update_record.status = "suspended"

    db.commit()
    db.refresh(login_record) 
    db.refresh(User_update_record)
    logger.info({
        "event": "logout_success",
        "user": request.state.user.username,
        "timestamp": datetime.utcnow().isoformat()
    })
    return {"message": f"User '{request.state.user.username}' logged out successfully"}


# --------------Delete a user ---------------------------
@router.delete("/delete_users", summary="Admin only", dependencies=[Depends(security)])
@admin_required
def delete_users(request:Request, user_id : int,db: Session = Depends(get_db)):
    
    """
    Route for deleting users
    """
    logger.info("Delete user route accessed") 

    deleted = db.query(User).filter(User.id == user_id).first()
    
    if not deleted:
        logger.warning("User not found")
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(deleted)
    db.commit()

    logger.info("User successfully deleted")
    return {"deleted": deleted}
# --------------- Update a user -----------------

@router.put("/update_users",dependencies=[Depends(security)])
@admin_required
def update_user(request:Request, userid: int, user: UserCreate, db: Session = Depends(get_db)):

    """
    Route for updating the existing user
    """
    logger.info({
                 "message":"Update user route accessed",
                 "timestamp": datetime.utcnow().isoformat()            
                 }) 
    repo = UserRepository(db)
    existing_user = db.query(User).filter(User.id == userid).first()

 # We should even add a condition in it to not change the role of the user

    if existing_user.role!= user.role:
        logger.warning({
                         "message":"Cannot change the role",
                         "timestamp": datetime.utcnow().isoformat()
                        })
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= "Cannot change the role")

    if not repo.get_by_id(userid):
        logger.warning({
                         "message":"User details not found",
                         "timestamp": datetime.utcnow().isoformat()
                        }) 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User details not found")
   
    user_object= repo.get_by_email(user.email)
    if user_object and user_object.id!= userid:
        logger.warning({
                        "message":"Error with the email",
                         "timestamp": datetime.utcnow().isoformat()
                        })
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Error with the email")
   
    if not PasswordManager.is_strong_password(user.password):
        logger.warning({
                      "message":"Use strong passwords for safety reasons",
                      "timestamp": datetime.utcnow().isoformat()            
                        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too weak. Must be 8+ chars, include uppercase, lowercase, number & special char."
        )
 
    hashed_pw = PasswordManager.hash_password(user.password)
   
    for attr, value in {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw,
        "role": user.role
    }.items():
        setattr(existing_user, attr, value)
   
    db.commit()
    db.refresh(existing_user)

    logger.info("User successfully updated")
    return {
        "id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email,
        "role": existing_user.role,
        "created_at": existing_user.created_at
    }

# users = db.query(User).all()
#     result = []
#     for user in users:
#         result.append({
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "role": user.role,
#             "password":user.password,
#             "status": user.status,
#             "created_at": user.created_at,
#             "updated_at": user.updated_at
#         })
#     return result
