"""
scripts/update_services_etape4.py — Mise à jour des services pour Étape 4
Migration vers PostgreSQL + Redis + Authentification
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Any

def update_cache_manager():
    """Mettre à jour le CacheManager pour supporter Redis."""
    cache_manager_path = Path("services/cache/cache_manager.py")

    if not cache_manager_path.exists():
        print("⚠️ CacheManager non trouvé, création...")
        return

    # Lire le contenu actuel
    with open(cache_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ajouter le support Redis
    redis_import = "import redis\nfrom redis import Redis"
    if redis_import not in content:
        # Ajouter après les autres imports
        import_section = content.find("from typing import")
        if import_section != -1:
            end_imports = content.find("\n\n", import_section)
            content = content[:end_imports] + f"\n{redis_import}" + content[end_imports:]

    # Mettre à jour la classe CacheManager
    old_class_def = "class CacheManager:"
    new_class_def = """class CacheManager:
    def __init__(self, redis_url: str = None, fs_cache_dir: str = ".cache_marotrade"):
        self.redis_url = redis_url
        self.fs_cache_dir = fs_cache_dir
        self.redis = None

        # Initialiser Redis si URL fournie
        if redis_url:
            try:
                self.redis = Redis.from_url(redis_url)
                self.redis.ping()  # Test connexion
                print("✅ Redis connecté")
            except Exception as e:
                print(f"⚠️ Redis non disponible: {e}")
                self.redis = None

        # Créer répertoire filesystem cache
        os.makedirs(fs_cache_dir, exist_ok=True)"""

    if old_class_def in content:
        # Trouver la définition de classe actuelle
        class_start = content.find(old_class_def)
        class_end = content.find("\n\n", class_start)
        if class_end == -1:
            class_end = len(content)

        # Remplacer
        content = content[:class_start] + new_class_def + content[class_end:]

    # Mettre à jour la méthode get
    old_get_method = "def get(self, key: str, ttl_seconds: int) -> Optional[dict]:"
    new_get_method = """def get(self, key: str, ttl_seconds: int = 3600) -> Optional[dict]:
        # Essayer Redis d'abord
        if self.redis:
            try:
                data = self.redis.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"⚠️ Erreur Redis get: {e}")

        # Fallback filesystem cache
        cache_file = os.path.join(self.fs_cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Vérifier TTL
                if "timestamp" in data:
                    age = datetime.now() - datetime.fromisoformat(data["timestamp"])
                    if age.total_seconds() > ttl_seconds:
                        return None

                return data.get("data")
            except Exception as e:
                print(f"⚠️ Erreur lecture cache FS: {e}")

        return None"""

    if old_get_method in content:
        get_start = content.find(old_get_method)
        get_end = content.find("\n\n", get_start)
        if get_end == -1:
            get_end = len(content)

        content = content[:get_start] + new_get_method + content[get_end:]

    # Ajouter méthode set
    if "def set(self, key: str, data: dict, ttl_seconds: int = 3600) -> None:" not in content:
        set_method = """

    def set(self, key: str, data: dict, ttl_seconds: int = 3600) -> None:
        timestamp = datetime.now().isoformat()
        cache_data = {"data": data, "timestamp": timestamp}

        # Sauvegarder dans Redis
        if self.redis:
            try:
                self.redis.setex(key, ttl_seconds, json.dumps(cache_data))
            except Exception as e:
                print(f"⚠️ Erreur Redis set: {e}")

        # Sauvegarder dans filesystem cache
        cache_file = os.path.join(self.fs_cache_dir, f"{key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erreur écriture cache FS: {e}")"""

        # Ajouter après la méthode get
        get_end = content.find("\n\n", content.find("return None"))
        if get_end != -1:
            content = content[:get_end] + set_method + content[get_end:]

    # Écrire le fichier mis à jour
    with open(cache_manager_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ CacheManager mis à jour pour Redis")

def update_data_sources():
    """Mettre à jour data_sources.py pour utiliser le cache Redis."""
    data_sources_path = Path("data_sources.py")

    if not data_sources_path.exists():
        print("⚠️ data_sources.py non trouvé")
        return

    with open(data_sources_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ajouter import du CacheManager
    cache_import = "from services.cache.cache_manager import CacheManager"
    if cache_import not in content:
        import_section = content.find("from typing import")
        if import_section != -1:
            end_imports = content.find("\n\n", import_section)
            content = content[:end_imports] + f"\n{cache_import}" + content[end_imports:]

    # Initialiser le cache manager
    cache_init = """
# Initialiser le cache manager
CACHE_MANAGER = CacheManager(
    redis_url=os.getenv("REDIS_URL"),
    fs_cache_dir=os.getenv("CACHE_DIR", ".cache_marotrade")
)"""

    if "CACHE_MANAGER" not in content:
        # Ajouter après les constantes
        constants_end = content.find("\n\n", content.rfind("}"))
        if constants_end != -1:
            content = content[:constants_end] + cache_init + content[constants_end:]

    # Écrire le fichier mis à jour
    with open(data_sources_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ data_sources.py mis à jour pour Redis")

def update_api_auth():
    """Ajouter l'authentification à l'API FastAPI."""
    api_path = Path("api.py")

    if not api_path.exists():
        print("⚠️ api.py non trouvé")
        return

    with open(api_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ajouter les imports d'authentification
    auth_imports = """from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import bcrypt
from datetime import datetime, timedelta
from prisma import Prisma"""

    if "from fastapi import Depends" not in auth_imports[:30]:
        import_section = content.find("from fastapi import")
        if import_section != -1:
            end_imports = content.find("\n\n", import_section)
            content = content[:end_imports] + f"\n{auth_imports}" + content[end_imports:]

    # Ajouter les constantes JWT
    jwt_constants = """
# Configuration JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "marotrade-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Sécurité
security = HTTPBearer()"""

    if "SECRET_KEY" not in content:
        # Ajouter après les imports
        constants_pos = content.find("\n\n", content.find("import"))
        if constants_pos != -1:
            content = content[:constants_pos] + jwt_constants + content[constants_pos:]

    # Ajouter les fonctions d'authentification
    auth_functions = """

# Fonctions d'authentification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    # Vérifier utilisateur en base
    db = Prisma()
    await db.connect()
    try:
        user = await db.user.find_unique(where={"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return user
    finally:
        await db.disconnect()

# Routes d'authentification
@app.post("/auth/login")
async def login(email: str, password: str):
    db = Prisma()
    await db.connect()
    try:
        user = await db.user.find_unique(where={"email": email})
        if not user or not verify_password(password, user.hashedPassword):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        await db.disconnect()

@app.post("/auth/register")
async def register(email: str, password: str, company_name: str = None):
    db = Prisma()
    await db.connect()
    try:
        # Vérifier si utilisateur existe
        existing = await db.user.find_unique(where={"email": email})
        if existing:
            raise HTTPException(status_code=400, detail="Utilisateur déjà existant")

        # Créer utilisateur
        hashed_password = get_password_hash(password)
        user = await db.user.create(data={
            "email": email,
            "hashedPassword": hashed_password,
            "companyName": company_name,
            "isActive": True,
        })

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        await db.disconnect()"""

    if "def verify_password" not in content:
        # Ajouter avant les routes existantes
        routes_start = content.find("@app.")
        if routes_start != -1:
            content = content[:routes_start] + auth_functions + "\n\n" + content[routes_start:]

    # Mettre à jour les routes existantes pour nécessiter l'authentification
    # Par exemple, pour /api/scoring
    old_scoring_route = "@app.get(\"/api/scoring\")"
    new_scoring_route = "@app.get(\"/api/scoring\")\nasync def get_scoring("

    if old_scoring_route in content:
        # Ajouter current_user: User = Depends(get_current_user) au paramètre
        scoring_start = content.find(old_scoring_route)
        scoring_end = content.find("):", scoring_start)
        if scoring_end != -1:
            content = content[:scoring_end] + ", current_user: User = Depends(get_current_user)" + content[scoring_end:]

    # Écrire le fichier mis à jour
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ api.py mis à jour avec authentification")

def update_requirements():
    """Mettre à jour requirements.txt pour Étape 4."""
    requirements_path = Path("requirements.txt")

    if not requirements_path.exists():
        print("⚠️ requirements.txt non trouvé")
        return

    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Nouvelles dépendances pour Étape 4
    new_deps = [
        "prisma~=0.11.0",
        "redis~=5.0.0",
        "bcrypt~=4.1.0",
        "PyJWT~=2.8.0",
        "slowapi~=0.1.9",
        "python-multipart~=0.0.6",  # Pour FastAPI file uploads
    ]

    for dep in new_deps:
        if dep.split("~=")[0] not in content:
            content += f"\n{dep}"

    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ requirements.txt mis à jour pour Étape 4")

def main():
    """Fonction principale de mise à jour des services."""
    print("🚀 MISE À JOUR SERVICES ÉTAPE 4")
    print("=" * 50)

    update_cache_manager()
    update_data_sources()
    update_api_auth()
    update_requirements()

    print("=" * 50)
    print("✅ MISE À JOUR TERMINÉE")
    print("📋 Services prêts pour PostgreSQL + Redis + Auth")

if __name__ == "__main__":
    main()