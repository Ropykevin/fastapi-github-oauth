from fastapi import FastAPI, Depends
from starlette.responses import RedirectResponse
import httpx
from database import get_db
from sqlalchemy.orm import Session
from models import StudentAccs



app = FastAPI()

# GitHub OAuth credentials
github_client_id = "Ov23lioLuZSPQOmomywd"
github_secret = "512874739b51fdfcfc5b4a5b1093418e4a78003b"


@app.get('/')
async def index():
    return {"message": "Hello dev"}

# Redirect to GitHub for login


@app.get('/github-login')
async def login():
    return RedirectResponse(f"https://github.com/login/oauth/authorize?client_id={github_client_id}"
                            "&scope=user:email", status_code=302)

# GitHub callback

@app.get('/github-code')
async def github_code(code: str, db: Session = Depends(get_db)):
    # Step 1: Exchange code for access token
    params = {
        "client_id": github_client_id,
        "client_secret": github_secret,
        "code": code,
        "scope": "user:email"  # Requesting email scope
    }
    headers = {
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token', params=params, headers=headers)

    # Step 2: Extract access token
    access_token = response.json().get('access_token')

    if not access_token:
        return {"error": "Access token not found", "details": response.json()}

    # Step 3: Fetch user's emails from GitHub
    async with httpx.AsyncClient() as client:
        headers.update({'Authorization': f'Bearer {access_token}'})
        response = await client.get('https://api.github.com/user/emails', headers=headers)

    user_emails = response.json()

    # Step 4: Check for error response
    if response.status_code != 200:
        return {"error": "Failed to fetch user emails", "details": user_emails}

    # Step 5: Safely extract the primary email
    if isinstance(user_emails, list):
        primary_email = next(
            (email['email'] for email in user_emails if email.get('primary')), None)
    else:
        return {"error": "Unexpected response format for emails", "details": user_emails}

    if not primary_email:
        return {"error": "No primary email found"}

    # Step 6: Check if user already exists in the database
    existing_user = db.query(StudentAccs).filter(
        StudentAccs.email == primary_email).first()

    if not existing_user:
        # Step 7: Create new user
        new_user = StudentAccs(email=primary_email, isverified=True)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "New user created", "user": primary_email}
    else:
        # Step 8: Handle existing user login
        return {"message": "User already exists", "user": primary_email}
