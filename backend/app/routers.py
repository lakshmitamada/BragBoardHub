from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import List

from .auth import get_current_admin_user, get_password_hash, authenticate_user, create_access_token, create_refresh_token, oauth2_scheme, settings
from . import crud, schemas
from .database import get_db
from .models import User, SecurityKey

router = APIRouter(tags=["Auth"])
admin_router = APIRouter(tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------- REGISTER ----------------
@router.post("/register", response_model=schemas.UserOut)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    if await crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Admin security key check
    if user.role == "admin":
        if not user.security_key:
            raise HTTPException(status_code=403, detail="Security key required")
        q = select(SecurityKey).where(SecurityKey.key == user.security_key, SecurityKey.is_used == False)
        res = await db.execute(q)
        key_obj = res.scalars().first()
        if not key_obj:
            raise HTTPException(status_code=403, detail="Invalid or used key")
        key_obj.is_used = True
        await db.commit()

    hashed_password = get_password_hash(user.password)
    new_user = await crud.create_user(
        db,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        name=user.name
    )
    return new_user

# ---------------- LOGIN ----------------
@router.post("/login", response_model=schemas.Token)
async def login_user(
    response: Response,
    user_credentials: schemas.UserLogin,
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": str(user.id)}, expires_delta=refresh_token_expires)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60*60*24*settings.REFRESH_TOKEN_EXPIRE_DAYS,
        samesite="lax",
        secure=False
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# ---------------- CURRENT USER ----------------
@router.get("/me", response_model=schemas.UserOut)
async def me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ---------------- ADMIN ROUTES ----------------
@admin_router.get("/employees", response_model=List[schemas.UserOut])
async def list_employees(current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.role == "employee"))
    return result.scalars().all()

@admin_router.delete("/employees/{emp_id}")
async def delete_employee(emp_id: int, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == emp_id, User.role == "employee"))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    await db.delete(employee)
    await db.commit()
    return {"msg": "Employee deleted"}

@admin_router.patch("/employees/{emp_id}/suspend")
async def suspend_employee(emp_id: int, suspend: bool, current_admin: User = Depends(get_current_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == emp_id, User.role == "employee"))
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.is_active = not suspend
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return {"msg": f"Employee {'suspended' if suspend else 'activated'} successfully"}

# ---------------- SECURITY KEY ROUTES ----------------
@router.post("/security-keys", dependencies=[Depends(get_current_admin_user)])
async def create_security_key(db: AsyncSession = Depends(get_db)):
    import secrets
    key_value = secrets.token_urlsafe(16)
    new_key = SecurityKey(key=key_value)
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return {"security_key": new_key.key, "id": new_key.id}
