"""
Auth Router — Signup, Login, Me.
"""

import uuid
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from app.db import get_db
from app.auth import hash_password, verify_password, create_token, decode_token

router = APIRouter()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "passenger"          # "passenger" or "police"
    language_pref: str = "en"
    phone: Optional[str] = None      # contact number (for FIR)
    address: Optional[str] = None    # home address (for FIR)


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(req: SignupRequest):
    if req.role not in ("passenger", "police"):
        raise HTTPException(400, "Role must be 'passenger' or 'police'")

    db = get_db()
    try:
        # Check if email already exists
        existing = db.execute("SELECT id FROM users WHERE email = ?", (req.email,)).fetchone()
        if existing:
            raise HTTPException(409, "Email already registered")

        user_id = f"{req.role[0]}_{uuid.uuid4().hex[:8]}"
        db.execute(
            """INSERT INTO users (id, name, email, password_hash, role, language_pref,
               phone, address)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, req.name, req.email, hash_password(req.password),
             req.role, req.language_pref, req.phone, req.address),
        )
        db.commit()

        token = create_token(user_id, req.role)
        return {
            "token": token,
            "user": {
                "id": user_id,
                "name": req.name,
                "email": req.email,
                "role": req.role,
                "language_pref": req.language_pref,
                "phone": req.phone,
                "address": req.address,
            },
        }
    finally:
        db.close()


@router.post("/login")
async def login(req: LoginRequest):
    db = get_db()
    try:
        user = db.execute("SELECT * FROM users WHERE email = ?", (req.email,)).fetchone()
        if not user:
            raise HTTPException(401, "Invalid email or password")
        if not verify_password(req.password, user["password_hash"]):
            raise HTTPException(401, "Invalid email or password")

        token = create_token(user["id"], user["role"])
        return {
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "language_pref": user["language_pref"],
                "phone": user["phone"],
                "address": user["address"],
            },
        }
    finally:
        db.close()


@router.get("/me")
async def me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    db = get_db()
    try:
        user = db.execute("SELECT * FROM users WHERE id = ?", (payload["user_id"],)).fetchone()
        if not user:
            raise HTTPException(401, "User not found")
        return {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "language_pref": user["language_pref"],
                "phone": user["phone"],
                "address": user["address"],
            }
        }
    finally:
        db.close()