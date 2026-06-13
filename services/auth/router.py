"""FastAPI routes for secure organization-scoped authentication."""

import os
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field, field_validator

from services.auth.repository import auth_repository
from services.auth.security import (
    AuthContext,
    create_access_token,
    generate_one_time_token,
    get_current_auth,
    hash_one_time_token,
    hash_password,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["authentication"])
EXPOSE_DEV_TOKENS = os.getenv("AUTH_EXPOSE_DEV_TOKENS", "false").lower() == "true"


class RegisterRequest(BaseModel):
    company: str = Field(min_length=2, max_length=160)
    name: str = Field(default="", max_length=120)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=10, max_length=128)
    organization_type: Literal["PME", "COOPERATIVE", "EXPORTER"] = "PME"
    country: str = Field(default="Maroc", max_length=80)
    city: str = Field(default="", max_length=80)
    sector: str = Field(default="", max_length=120)
    size: str = Field(default="", max_length=80)
    products: list[str] = Field(default_factory=list, max_length=30)
    target_markets: list[str] = Field(default_factory=list, max_length=30)
    export_experience: str = Field(default="", max_length=120)
    remember: bool = True

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("Le mot de passe doit contenir une majuscule et un chiffre.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
            raise ValueError("Email professionnel invalide.")
        return normalized


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str
    remember: bool = False

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=20)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=10, max_length=128)


def _set_auth_cookie(response: Response, token: str, max_age: int) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="lax",
        path="/",
    )


async def _account_payload(user, membership, organization) -> dict:
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "email_verified": user.emailVerified,
            "role": membership.role,
        },
        "organization": {
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
            "type": organization.type,
            "country": organization.country,
            "city": organization.city,
            "sector": organization.sector,
            "size": organization.size,
            "products": organization.products,
            "target_markets": organization.targetMarkets,
            "export_experience": organization.exportExperience,
        },
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, response: Response):
    if await auth_repository.find_user_by_email(req.email):
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email.")

    user, organization, membership = await auth_repository.create_account(
        req.model_dump(),
        hash_password(req.password),
    )
    verification_token, verification_hash = generate_one_time_token()
    await auth_repository.create_verification_token(user.id, verification_hash)
    access_token, max_age = create_access_token(
        user_id=user.id,
        organization_id=organization.id,
        membership_role=membership.role,
        email=user.email,
        remember=req.remember,
    )
    _set_auth_cookie(response, access_token, max_age)
    payload = await _account_payload(user, membership, organization)
    if EXPOSE_DEV_TOKENS:
        payload["verification_token_dev"] = verification_token
    return payload


@router.post("/login")
async def login(req: LoginRequest, response: Response):
    user = await auth_repository.find_user_by_email(req.email)
    if not user or not user.isActive or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
    membership = await auth_repository.get_membership(user.id)
    if not membership:
        raise HTTPException(status_code=403, detail="Aucune PME active associée à ce compte.")
    organization = await auth_repository.get_organization(membership.organizationId)
    if not organization or not organization.isActive:
        raise HTTPException(status_code=403, detail="Espace PME désactivé.")

    token, max_age = create_access_token(
        user_id=user.id,
        organization_id=organization.id,
        membership_role=membership.role,
        email=user.email,
        remember=req.remember,
    )
    _set_auth_cookie(response, token, max_age)
    await auth_repository.update_last_login(user.id)
    return await _account_payload(user, membership, organization)


@router.get("/me")
async def me(auth: AuthContext = Depends(get_current_auth)):
    user = await auth_repository.find_user_by_id(auth.user_id)
    membership = await auth_repository.get_membership(auth.user_id, auth.organization_id)
    organization = await auth_repository.get_organization(auth.organization_id)
    if not user or not membership or not organization:
        raise HTTPException(status_code=401, detail="Session invalide.")
    return await _account_payload(user, membership, organization)


@router.post("/verify-email")
async def verify_email(req: VerifyEmailRequest):
    if not await auth_repository.verify_email_token(hash_one_time_token(req.token)):
        raise HTTPException(status_code=400, detail="Jeton de vérification invalide ou expiré.")
    return {"verified": True}


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    user = await auth_repository.find_user_by_email(req.email)
    # Keep the public response identical to prevent account enumeration.
    response = {"sent": True}
    if user and user.isActive:
        reset_token, reset_hash = generate_one_time_token()
        await auth_repository.create_password_reset_token(user.id, reset_hash)
        if EXPOSE_DEV_TOKENS:
            response["reset_token_dev"] = reset_token
    return response


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if not await auth_repository.reset_password(hash_one_time_token(req.token), hash_password(req.password)):
        raise HTTPException(status_code=400, detail="Jeton de réinitialisation invalide ou expiré.")
    return {"password_reset": True}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"logged_out": True}
