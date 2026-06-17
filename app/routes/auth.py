from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import re

from app.db.session import get_db
from app.models.user import User
from app.services.auth_utils import hash_password, verify_password


# Router for auth
router = APIRouter(tags=["Auth"])

# Jinja templates
templates = Jinja2Templates(directory="templates")


# ✅ Password validation function
def is_valid_password(password: str) -> bool:
    """
    Rules:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one number
    """
    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    return True


# ======================================================
# LOGIN PAGE (GET)
# ======================================================
@router.get("/login")
def login_page(request: Request,registered: int = 0):

    """
    Shows login HTML page
    """
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "error": None,
            "registered": registered

        }
    )


# ======================================================
# LOGIN ACTION (POST)
# ======================================================
@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handles login logic
    """

    # ✅ Step 1: Find user
    user = db.query(User).filter(User.username == username).first()

    # ❌ If user not found
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid username or password"
            }
        )

    # ❌ Step 2: Verify password
    if not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid username or password"
            }
        )

    # ✅ Step 3: Successful login → redirect
    response = RedirectResponse(url="/dashboard", status_code=303)

    # ✅ Store user_id in cookie
    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,
        path="/"
    )

    return response


# ======================================================
# REGISTER PAGE (GET)
# ======================================================
@router.get("/register")
def register_page(request: Request):
    """
    Shows register HTML page
    """
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
            "error": None
        }
    )


# ======================================================
# REGISTER ACTION (POST)
# ======================================================
@router.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handles user registration
    """

    # ✅ Step 1: Check if username exists
    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": "Username already exists"
            }
        )

    # ✅ Step 2: Validate password (NEW ✅)
    if not is_valid_password(password):
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": "Password must be at least 8 characters, include one uppercase letter and one number"
            }
        )

    # ✅ Step 3: Hash password
    hashed_password = hash_password(password)

    # ✅ Step 4: Create user
    user = User(
        username=username,
        password_hash=hashed_password,
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Step 5: Redirect to login

    return RedirectResponse(url="/login?registered=1", status_code=303)



# ======================================================
# LOGOUT
# ======================================================
@router.get("/logout")
def logout():
    """
    Logs out the user
    """
    response = RedirectResponse(url="/login", status_code=303)

    # ✅ Remove cookie
    response.delete_cookie("user_id", path="/")

    return response