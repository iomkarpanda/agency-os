from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from db.client import get_db
from repository.users import get_user_username, get_user_email
from schemas.users import UserInput,LoginInput
from service.token import create_access_token , create_refresh_token
from db.models import Users
from service.auth import hashpassword, verifypassword
import uuid


auth_route = APIRouter() 

@auth_route.post("/api/auth/signup")
async def signup(request: UserInput, db=Depends(get_db)):   
    username = request.username
    pass1 = request.password1
    pass2 = request.password2
    display_name = request.display_name
    email = request.email
    
    if pass1 != pass2:
        return JSONResponse({'status': 'password mismatch'}, status_code=400)
    
    if not username or len(username) < 3:
        return JSONResponse({'status': 'username must be at least 3 characters'}, status_code=400)
    
    if await get_user_username(username, db):
        return JSONResponse({'status': 'username already exists'}, status_code=409)
    
    if await get_user_email(email, db):
        return JSONResponse({'status': 'email already exists'}, status_code=409)

    
    try:
        user = Users(
            id=uuid.uuid4(),
            username=username,
            password_hash=hashpassword(pass1),
            display=display_name,
            email=email
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)  
        
        return JSONResponse({'status': 'success', 'user_id': str(user.id)}, status_code=201)
    except Exception as e:
        await db.rollback()
        return JSONResponse({'status': 'failed to create user'}, status_code=500)

@auth_route.post("/api/auth/login")
async def login(request: LoginInput, db=Depends(get_db)):
    email = request.email
    password = request.password

    user = await get_user_email(email, db)
    if not user:  
        return JSONResponse({"status": "email does not exist, please sign up"}, status_code=404)

    if not verifypassword(password, user.password_hash):
        return JSONResponse({"status": "incorrect password"}, status_code=401)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return JSONResponse({
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user.id)
    }, status_code=200)


@auth_route.post("/api/auth/access_token")
async def get_access_token(request:Request):
    body = await request.json()
    userid = body["userid"]
    return create_access_token(userid)


@auth_route.post("/api/auth/refresh_token")
async def get_refresh_token(request:Request):
    body = await request.json()
    userid = body["userid"]
    return create_refresh_token(userid)