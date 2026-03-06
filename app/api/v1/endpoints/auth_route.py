from fastapi import APIRouter,Depends,Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.oauth import oauth
import os
from app.config.database import get_db
from app.models.oauth import OAuthAccount
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/google", summary="Redirect to Google login")
async def google_login(request: Request):
    """
    Initiates the Google OAuth flow.
    Redirects the user to Google's consent screen.
    """
    #redirect_uri = request.url_for("google_callback")
    redirect_uri = f"{os.getenv('BASE_URL')}/auth/google/callback"
    print(f"DEBUG redirect_uri: {redirect_uri}") 
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):

    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    email = user_info["email"]
    google_id = user_info["sub"]
    full_name = user_info.get("name", "")

    first_name = full_name.split(" ")[0]
    last_name = " ".join(full_name.split(" ")[1:]) if " " in full_name else ""

    # check oauth account
    result = await db.execute(
        select(OAuthAccount)
        .options(selectinload(OAuthAccount.user))
        .where(
            OAuthAccount.provider == "google",
            OAuthAccount.provider_user_id == google_id
        )
    )
    oauth_account = result.scalar_one_or_none()

    if oauth_account:
        user = oauth_account.user

    else:
        # check user by email
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            # create new user
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # create oauth mapping
        oauth_account = OAuthAccount(
            provider="google",
            provider_user_id=google_id,
            user_id=user.id
        )
        db.add(oauth_account)
        await db.commit()
         # 🔐 CREATE JWT TOKEN
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "provider": "google"
            }   
        )

    #response=RedirectResponse(url="http://localhost:3000/agents")
    #response=RedirectResponse(url="https://brook-unrecitative-exhaustingly.ngrok-free.dev/agents/")

     # OPTION A — Redirect to frontend with token (most common SPA pattern)
    response = RedirectResponse(
        url=f"http://localhost:3000/auth/callback?token={access_token}"
    )
    return response

    # OPTION B — Return JSON (if frontend calls callback via API)
    # return {
    #     "access_token": access_token,
    #     "token_type": "bearer",
    #     "user": {
    #         "id": user.id,
    #         "email": user.email,
    #         "first_name": user.first_name,
    #         "last_name": user.last_name
    #     }
    # }
     
     