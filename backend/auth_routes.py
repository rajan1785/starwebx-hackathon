from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from database import get_db
from models import User, Notification
from schemas import (
    GoogleAuthRequest, TokenResponse, UserResponse, UserProfileUpdate
)
from auth import verify_google_token, create_access_token, verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# Log activity helper
def log_activity(db: Session, user_id: int, activity_type: str, details: dict, request: Request):
    from models import ActivityLog
    activity_log = ActivityLog(
        user_id=user_id,
        activity_type=activity_type,
        details=details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(activity_log)
    db.commit()


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_request: GoogleAuthRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user with Google OAuth token"""
    google_user = verify_google_token(auth_request.token)
    
    if not google_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.email == google_user['email']).first()
    
    if not user:
        # Create new user
        user = User(
            email=google_user['email'],
            full_name=google_user['name'],
            profile_picture_url=google_user.get('picture')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create welcome notification
        notification = Notification(
            user_id=user.id,
            title="Welcome to Coding Ka Big Boss!",
            message="Complete your profile to get started with the hackathon.",
            type="welcome"
        )
        db.add(notification)
        db.commit()
    
    # Log login activity
    log_activity(db, user.id, "login", {"method": "google"}, request)
    
    # Create JWT token
    access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # Log profile update
    log_activity(db, current_user.id, "profile_update", profile_data.dict(exclude_unset=True), request)
    
    return UserResponse.from_orm(current_user)
