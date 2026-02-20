from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt  # Direct bcrypt import
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List
import database

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Config
SECRET_KEY = "knowmap_super_secret_key"
ALGORITHM = "HS256"

# Password hashing functions using bcrypt directly
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Convert password to bytes and hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# Pydantic Models
class UserAuth(BaseModel):
    username: str
    password: str

class ProfileData(BaseModel):
    username: str
    interests: List[str]

# Database dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "Backend is running!"}

# 1. SIGNUP ENDPOINT - FIXED with direct bcrypt
@app.post("/signup")
def signup(request: UserAuth, db: Session = Depends(get_db)):
    try:
        print(f"📝 Signup attempt for user: {request.username}")
        print(f"📝 Password length: {len(request.password)}")
        
        # Check if user exists
        user = db.query(database.User).filter(database.User.username == request.username).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash password using direct bcrypt
        try:
            hashed_pw = hash_password(request.password)
            print(f"✅ Password hashed successfully")
            print(f"   Hash length: {len(hashed_pw)}")
        except Exception as e:
            print(f"❌ Password hashing error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Password hashing failed: {str(e)}")
        
        # Create new user
        new_user = database.User(
            username=request.username, 
            hashed_password=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ User created with ID: {new_user.id}")
        
        # Auto-create empty profile for user
        new_profile = database.UserProfile(
            user_id=new_user.id,
            interests="",
            saved_graphs=""
        )
        db.add(new_profile)
        db.commit()
        
        print(f"✅ Empty profile created for user")
        
        return {"message": "Account created successfully", "user_id": new_user.id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

# 2. LOGIN ENDPOINT - FIXED with direct bcrypt
@app.post("/login")
def login(request: UserAuth, db: Session = Depends(get_db)):
    try:
        print(f"🔑 Login attempt for user: {request.username}")
        
        user = db.query(database.User).filter(database.User.username == request.username).first()
        if not user:
            print(f"❌ User not found: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password using direct bcrypt
        try:
            password_valid = verify_password(request.password, user.hashed_password)
            print(f"✅ Password verification result: {password_valid}")
        except Exception as e:
            print(f"❌ Password verification error: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not password_valid:
            print(f"❌ Invalid password for user: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token_data = {
            "sub": user.username, 
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        print(f"✅ Login successful for user: {request.username}")
        return {
            "access_token": token, 
            "token_type": "bearer",
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# 3. SAVE PROFILE ENDPOINT
@app.post("/save_profile")
def save_profile(profile: ProfileData, db: Session = Depends(get_db)):
    try:
        print(f"💾 Save profile for user: {profile.username}")
        print(f"   Interests: {profile.interests}")
        
        # Find user by username
        user = db.query(database.User).filter(database.User.username == profile.username).first()
        if not user:
            print(f"❌ User not found: {profile.username}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"✅ Found user with ID: {user.id}")
        
        # Convert interests list to string
        interests_str = ", ".join(profile.interests) if profile.interests else ""
        
        # Check if profile exists
        existing_profile = db.query(database.UserProfile).filter(
            database.UserProfile.user_id == user.id
        ).first()
        
        if existing_profile:
            print("🔄 Updating existing profile")
            existing_profile.interests = interests_str
        else:
            print("🆕 Creating new profile")
            new_profile = database.UserProfile(
                user_id=user.id,
                interests=interests_str,
                saved_graphs=""
            )
            db.add(new_profile)
        
        db.commit()
        print("✅ Profile saved successfully")
        
        return {"message": "Profile updated successfully", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Save profile error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

# 4. GET PROFILE ENDPOINT
@app.get("/get_profile/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    try:
        print(f"📂 Get profile for user: {username}")
        
        user = db.query(database.User).filter(database.User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = db.query(database.UserProfile).filter(
            database.UserProfile.user_id == user.id
        ).first()
        
        if profile:
            interests_list = profile.interests.split(", ") if profile.interests else []
            return {
                "interests": interests_list,
                "saved_graphs": profile.saved_graphs or ""
            }
        else:
            return {"interests": [], "saved_graphs": ""}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

# 5. DEBUG ENDPOINT
@app.get("/debug")
def debug(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        users = db.query(database.User).all()
        profiles = db.query(database.UserProfile).all()
        
        return {
            "tables": tables,
            "users_count": len(users),
            "profiles_count": len(profiles),
            "users": [{"id": u.id, "username": u.username} for u in users],
            "profiles": [{"id": p.id, "user_id": p.user_id, "interests": p.interests} for p in profiles]
        }
    except Exception as e:
        return {"error": str(e)}