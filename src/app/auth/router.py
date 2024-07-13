from fastapi import APIRouter, Depends, HTTPException, Body, Request
from typing import Any
from motor.core import AgnosticDatabase
from pydantic import EmailStr
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.config import settings
from app.deps import get_db
from app.user import crud
from app.auth import crud as auth_crud
from app.auth import security, deps
from app.auth.service import send_email_validation_email, send_reset_password_email
from app.auth.schemas import EmailValidation, Token
from authlib.integrations.starlette_client import OAuth

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# Initialize OAuth
oauth = OAuth()

# Register OAuth clients
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=f"{settings.API_V1_STR}/auth/callback/google",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="microsoft",
    client_id=settings.MICROSOFT_CLIENT_ID,
    client_secret=settings.MICROSOFT_CLIENT_SECRET,
    authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    authorize_params=None,
    access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=f"{settings.API_V1_STR}/auth/callback/microsoft",
    client_kwargs={"scope": "User.Read"},
)

oauth.register(
    name="apple",
    client_id=settings.APPLE_CLIENT_ID,
    client_secret=settings.APPLE_CLIENT_SECRET,
    authorize_url="https://appleid.apple.com/auth/authorize",
    authorize_params=None,
    access_token_url="https://appleid.apple.com/auth/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=f"{settings.API_V1_STR}/auth/callback/apple",
    client_kwargs={"scope": "name email"},
)


@router.get("/login/{provider}")
async def login(request: Request, provider: str) -> Any:
    """
    Redirects the user to the OAuth provider's login page.
    """
    redirect_uri = request.url_for("auth:callback", provider=provider, _external=True)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@router.route("/callback/{provider}")
async def callback(
    request: Request, provider: str, db: AgnosticDatabase = Depends(get_db)
) -> Any:
    """
    Handles the OAuth provider's callback.
    """
    token = await oauth.create_client(provider).authorize_access_token(request)
    user_info = await oauth.create_client(provider).parse_id_token(request, token)

    # Your logic to handle user information and login
    user = await crud.user.get_by_email(db, email=user_info["email"])
    if not user:
        # If the user does not exist, create a new one
        user = await crud.user.create_oauth_user(db, user_info=user_info)
    else:
        # If the user exists, update any necessary details (optional)
        pass

    # Generate access and refresh tokens
    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)
    await auth_crud.token.create(db=db, obj_in=refresh_token, user_obj=user)

    return JSONResponse(
        status_code=200,
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        },
    )


@router.post("/login/oauth", response_model=Token)
async def login_with_oauth2_email(
    db: AgnosticDatabase = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    First step with OAuth2 compatible token login, get an access token for future requests.
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Login failed; incorrect email or password"
        )
    # if not crud.user.is_email_validated(user):
    #     raise HTTPException(status_code=400, detail="Email not verified")
    # if not crud.user.is_active(user):
    #     raise HTTPException(status_code=400, detail="Inactive User")

    # Check if totp active
    refresh_token = None
    force_totp = True
    if not user.totp_secret:
        # No TOTP, so this concludes the login validation
        force_totp = False
        refresh_token = security.create_refresh_token(subject=user.id)
        await auth_crud.token.create(db=db, obj_in=refresh_token, user_obj=user)
    return {
        "access_token": security.create_access_token(
            subject=user.id, force_totp=force_totp
        ),  # noqa
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/verify/email")
async def verify_email(
    *,
    email: EmailStr = Body(...),
    pin: str = Body(...),
    db: AgnosticDatabase = Depends(get_db),
) -> JSONResponse:
    """
    Verify email, it depends on a verification pin from the email verification sent to the user.
    """
    # Fetch user by email
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Check if the provided PIN matches the one in the database
    if not security.verify_verification_pin(db_obj=user, pin=pin):
        raise HTTPException(status_code=400, detail="Invalid verification pin")

    # # Update user verification status
    await crud.user.validate_email(db=db, db_obj=user)
    return JSONResponse(
        status_code=200, content={"message": "Email verified successfully"}
    )


@router.post("/resend-code/")
async def resend_code(
    email: EmailStr = Body(...), db: AgnosticDatabase = Depends(get_db)
) -> JSONResponse:
    """Resend verification email with a new verification code."""

    # Fetch user by email
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Generate Verification Pin
    verification_pin = security.create_verification_pin()

    # Update user verification PIN
    await crud.user.update(
        db, db_obj=user, obj_in={"verification_pin": verification_pin}
    )

    email_data = EmailValidation(
        email=email, subject="Email Verification", token=verification_pin
    )  # noqa

    # send email verifiication to email
    if settings.EMAILS_ENABLED and email:
        send_email_validation_email(email_data)

    return JSONResponse(
        status_code=200, content={"message": "Verification code resent successfully"}
    )


@router.post("/recover/{email}")
async def recover_password(email: str, db: AgnosticDatabase = Depends(get_db)) -> Any:
    """
    Password Recovery endpoint, sends an email to the user with a token to reset their password.
    """
    user = await crud.user.get_by_email(db, email=email)
    if user and crud.user.is_active(user):
        tokens = security.create_magic_tokens(subject=user.id)
        if settings.EMAILS_ENABLED:
            send_reset_password_email(email_to=user.email, email=email, token=tokens[0])
            return JSONResponse(
                status_code=200,
                content={
                    "message": "If that login exists, we'll send you an email to reset your password.",
                    "data": [{"claim": tokens[1]}],
                },
            )


@router.post("/reset")
async def reset_password(
    *,
    db: AgnosticDatabase = Depends(get_db),
    new_password: str = Body(...),
    claim: str = Body(...),
    magic_in: str = Depends(deps.get_magic_token),
) -> Any:
    """
    Reset password endpoint, requires a valid claim token and depends on the magic token dependency.
    """
    claim_in = deps.get_magic_token(token=claim)
    # Get the user
    user = await crud.user.get(db, id=magic_in.sub)
    # Test the claims
    if (
        (claim_in.sub == magic_in.sub)
        or (claim_in.fingerprint != magic_in.fingerprint)
        or not user
        or not crud.user.is_active(user)
    ):
        raise HTTPException(
            status_code=400, detail="Password update failed; invalid claim."
        )
    # Update the password
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    await user.save()
    return {"msg": "Password updated successfully."}
