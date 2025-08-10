from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets

app = FastAPI(
    title="Login/Logout API"
    description="A simple API for user login and logout using FastAPI.",
    version="1.0.0"
)

# In-memory user store for demonstration purposes
fake_users_db = {
    "alice": {
        "username": "alice",
        "password": "wonderland"  # In production, use hashed passwords!
    }
}

# In-memory token store for demonstration purposes
active_tokens = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

@app.post("/login", response_model=Token, summary="Login to get an access token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return an access token.

    - **username**: User's username
    - **password**: User's password
    """
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    # Generate a simple token (for demo only; use JWT in production)
    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        "username": user["username"],
        "created_at": datetime.utcnow()
    }
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current user from the token.
    """
    token_data = active_tokens.get(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return User(username=token_data["username"])

@app.post("/logout", summary="Logout and invalidate the access token")
def logout(token: str = Depends(oauth2_scheme)):
    """
    Invalidate the current access token, logging the user out.
    """
    if token in active_tokens:
        del active_tokens[token]
        return {"message": "Successfully logged out."}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@app.get("/me", response_model=User, summary="Get current user info")
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the current logged-in user's information.
    """
    return current_user

# --- API Documentation Markdown Generation ---

@app.on_event("startup")
def generate_api_docs():
    """
    Generate a Markdown file with the API documentation and flow.
    """
    with open("API_DOC.md", "w") as f:
        f.write("# Login/Logout API Documentation\n\n")
        f.write("## Endpoints\n\n")
        f.write("### 1. Login\n")
        f.write("`POST /login`\n\n")
        f.write("Authenticate user and return an access token.\n\n")
        f.write("**Request Body (form):**\n")
        f.write("- username: string\n- password: string\n\n")
        f.write("**Response:**\n")
        f.write("```\n{\n  \"access_token\": \"...\",\n  \"token_type\": \"bearer\"\n}\n```\n\n")

        f.write("### 2. Logout\n")
        f.write("`POST /logout`\n\n")
        f.write("Invalidate the current access token, logging the user out.\n\n")
        f.write("**Headers:**\n")
        f.write("- Authorization: Bearer <access_token>\n\n")
        f.write("**Response:**\n")
        f.write("```\n{\n  \"message\": \"Successfully logged out.\"\n}\n```\n\n")

        f.write("### 3. Get Current User\n")
        f.write("`GET /me`\n\n")
        f.write("Get the current logged-in user's information.\n\n")
        f.write("**Headers:**\n")
        f.write("- Authorization: Bearer <access_token>\n\n")
        f.write("**Response:**\n")
        f.write("```\n{\n  \"username\": \"alice\"\n}\n```\n\n")

        f.write("## Flow of the Code\n\n")
        f.write("1. **Login**: User sends username and password to `/login`. If valid, receives an access token.\n")
        f.write("2. **Authenticated Requests**: User includes the access token in the `Authorization` header as `Bearer <token>` for protected endpoints (e.g., `/me`, `/logout`).\n")
        f.write("3. **Logout**: User calls `/logout` with the token to invalidate it. The token is removed from the active session store.\n")
        f.write("4. **Token Validation**: Each protected endpoint checks if the token is valid and active.\n\n")
        f.write("> **Note:** This is a demonstration. In production, use secure password hashing and JWT tokens.\n")
