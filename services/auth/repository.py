"""Prisma-backed repository for users, organizations, and memberships."""

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Optional

from fastapi import HTTPException, status


class AuthRepository:
    def __init__(self):
        self.db = None
        self.available = False
        self.error = ""

    async def connect(self) -> None:
        if self.available:
            return
        try:
            from prisma import Prisma

            self.db = Prisma()
            await self.db.connect()
            self.available = True
            self.error = ""
        except Exception as exc:
            self.db = None
            self.available = False
            self.error = str(exc)

    async def disconnect(self) -> None:
        if self.db and self.available:
            await self.db.disconnect()
        self.available = False

    async def require_db(self):
        if not self.available or self.db is None:
            await self.connect()
        if not self.available or self.db is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Base utilisateurs indisponible. Démarrez PostgreSQL puis exécutez Prisma.",
            )
        return self.db

    async def find_user_by_email(self, email: str):
        db = await self.require_db()
        return await db.user.find_unique(where={"email": email.strip().lower()})

    async def find_user_by_id(self, user_id: str):
        db = await self.require_db()
        return await db.user.find_unique(where={"id": user_id})

    async def get_membership(self, user_id: str, organization_id: Optional[str] = None):
        db = await self.require_db()
        where: dict[str, Any] = {"userId": user_id}
        if organization_id:
            where["organizationId"] = organization_id
        memberships = await db.membership.find_many(where=where, take=1)
        return memberships[0] if memberships else None

    async def get_organization(self, organization_id: str):
        db = await self.require_db()
        return await db.organization.find_unique(where={"id": organization_id})

    async def create_account(self, payload: dict, password_hash: str):
        db = await self.require_db()
        slug_base = re.sub(r"[^a-z0-9]+", "-", payload["company"].lower()).strip("-") or "entreprise"
        slug = slug_base
        suffix = 1
        while await db.organization.find_unique(where={"slug": slug}):
            suffix += 1
            slug = f"{slug_base}-{suffix}"

        organization = await db.organization.create(
            data={
                "name": payload["company"].strip(),
                "slug": slug,
                "type": payload.get("organization_type", "PME"),
                "country": payload.get("country", "Maroc"),
                "city": payload.get("city") or None,
                "sector": payload.get("sector") or None,
                "size": payload.get("size") or None,
                "products": payload.get("products", []),
                "targetMarkets": payload.get("target_markets", []),
                "exportExperience": payload.get("export_experience") or None,
            }
        )
        user = await db.user.create(
            data={
                "email": payload["email"].strip().lower(),
                "name": payload.get("name") or payload["company"].strip(),
                "password": password_hash,
                "emailVerified": False,
                "isActive": True,
            }
        )
        membership = await db.membership.create(
            data={"userId": user.id, "organizationId": organization.id, "role": "OWNER"}
        )
        return user, organization, membership

    async def update_last_login(self, user_id: str) -> None:
        db = await self.require_db()
        await db.user.update(where={"id": user_id}, data={"lastLoginAt": datetime.now(timezone.utc)})

    async def create_verification_token(self, user_id: str, token_hash: str):
        db = await self.require_db()
        return await db.emailverificationtoken.create(
            data={
                "userId": user_id,
                "tokenHash": token_hash,
                "expiresAt": datetime.now(timezone.utc) + timedelta(hours=24),
            }
        )

    async def verify_email_token(self, token_hash: str) -> bool:
        db = await self.require_db()
        record = await db.emailverificationtoken.find_unique(where={"tokenHash": token_hash})
        if not record or record.usedAt or record.expiresAt < datetime.now(timezone.utc):
            return False
        await db.emailverificationtoken.update(
            where={"id": record.id}, data={"usedAt": datetime.now(timezone.utc)}
        )
        await db.user.update(where={"id": record.userId}, data={"emailVerified": True})
        return True

    async def create_password_reset_token(self, user_id: str, token_hash: str):
        db = await self.require_db()
        return await db.passwordresettoken.create(
            data={
                "userId": user_id,
                "tokenHash": token_hash,
                "expiresAt": datetime.now(timezone.utc) + timedelta(minutes=30),
            }
        )

    async def reset_password(self, token_hash: str, password_hash: str) -> bool:
        db = await self.require_db()
        record = await db.passwordresettoken.find_unique(where={"tokenHash": token_hash})
        if not record or record.usedAt or record.expiresAt < datetime.now(timezone.utc):
            return False
        await db.passwordresettoken.update(
            where={"id": record.id}, data={"usedAt": datetime.now(timezone.utc)}
        )
        await db.user.update(where={"id": record.userId}, data={"password": password_hash})
        return True

    async def save_workspace_analysis(
        self,
        *,
        user_id: str,
        organization_id: str,
        product_name: str,
        hs_code: str,
        top_n: int,
        results: list[dict],
    ):
        db = await self.require_db()
        from prisma import Json

        return await db.workspaceanalysis.create(
            data={
                "userId": user_id,
                "organizationId": organization_id,
                "productName": product_name,
                "hsCode": hs_code,
                "topN": top_n,
                "results": Json(results),
            }
        )

    async def list_workspace_analyses(self, organization_id: str, take: int = 30):
        db = await self.require_db()
        return await db.workspaceanalysis.find_many(
            where={"organizationId": organization_id},
            order={"createdAt": "desc"},
            take=min(max(take, 1), 100),
        )

    async def delete_workspace_analysis(self, analysis_id: str, organization_id: str) -> bool:
        db = await self.require_db()
        record = await db.workspaceanalysis.find_first(
            where={"id": analysis_id, "organizationId": organization_id}
        )
        if not record:
            return False
        await db.workspaceanalysis.delete(where={"id": analysis_id})
        return True


auth_repository = AuthRepository()
