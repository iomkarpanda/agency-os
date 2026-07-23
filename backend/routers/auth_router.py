from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from db.client import get_db
from repository.users import get_user_username, get_user_email
from repository.tokens import add_access_and_refresh_tokens , update_access_and_expiry
from schemas.users import UserInput,LoginInput
from services.token import create_access_token, create_refresh_token, revalidate_access_token
from db.models import Users
from services.auth import hash_password, verify_password
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
        user_id = uuid.uuid4()
        user = Users(
            id=user_id,
            username=username,
            password_hash=hash_password(pass1),
            display=display_name,
            email=email
        )
        db.add(user)
        await db.commit()

        return JSONResponse({'status': 'success', 'user_id': str(user_id)}, status_code=201)
    except Exception as e:
        await db.rollback()
        return JSONResponse({'status': 'failed to create user'}, status_code=500)

@auth_route.post("/api/auth/login")
async def login(request: LoginInput, req:Request, db=Depends(get_db)):
    email = request.email
    password = request.password

    user_agent = req.headers.get("user-agent")

    user = await get_user_email(email, db)
    if not user:  
        return JSONResponse({"status": "email does not exist, please sign up"}, status_code=404)

    if not verify_password(password, user.password_hash):
        return JSONResponse({"status": "incorrect password"}, status_code=401)

    user_id = user.id 

    access_token, access_expiry_time = create_access_token(str(user_id))
    refresh_token, refresh_expiry_time = create_refresh_token(str(user_id))

    await add_access_and_refresh_tokens(
        db=db,
        id=uuid.uuid4(),
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires_at=access_expiry_time,
        refresh_token_expires_at=refresh_expiry_time,
        device_info=user_agent,
        is_revoked=False
    )

    return JSONResponse({
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user_id)
    }, status_code=200)




@auth_route.post("/api/auth/refresh_access_token")
async def refresh_access_token(request: Request, db=Depends(get_db)):

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return JSONResponse({"status": "refresh token missing"}, status_code=401)

    result = revalidate_access_token(refresh_token)
    if not result:
        return JSONResponse({"status": "invalid or expired refresh token"}, status_code=401)

    new_access_token, new_expiry_time, userid = result

    await update_access_and_expiry(db, refresh_token, new_access_token, new_expiry_time)
    return JSONResponse({'access_token':new_access_token})

