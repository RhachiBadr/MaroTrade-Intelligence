# Authentification multi-tenant MaroTrade

## Modèle de sécurité

- Une PME, coopérative ou société exportatrice est une `Organization`.
- Les utilisateurs rejoignent une organisation via `Membership`.
- Les rôles disponibles sont `OWNER`, `ADMIN`, `MEMBER` et `VIEWER`.
- Le JWT contient `user_id`, `organization_id` et le rôle dans l’organisation.
- Le JWT est stocké dans un cookie `HttpOnly`.
- Les mots de passe sont hashés avec bcrypt.
- Les jetons de vérification email et de réinitialisation sont hashés en base.
- Les analyses sont enregistrées dans `WorkspaceAnalysis` avec leur `organizationId`.

## Configuration locale

Copier les variables de `.env.example` dans `.env` et définir une clé JWT robuste :

```env
JWT_SECRET_KEY=une-cle-aleatoire-secrete-de-plus-de-32-caracteres
COOKIE_SECURE=false
AUTH_EXPOSE_DEV_TOKENS=true
```

`AUTH_EXPOSE_DEV_TOKENS=true` est réservé au développement local sans fournisseur email.
En production, utiliser `false`, configurer l’envoi email et activer `COOKIE_SECURE=true`.

## Initialiser PostgreSQL et Prisma

```powershell
docker compose up -d postgres redis

$env:PYTHONUTF8='1'
$env:PATH="$PWD\venv\Scripts;$env:PATH"
.\venv\Scripts\prisma.exe generate --schema prisma\schema.prisma
.\venv\Scripts\prisma.exe db push --schema prisma\schema.prisma
```

### Dépannage Docker local

Docker Desktop doit être démarré avant PostgreSQL et Redis. Si les conteneurs
`marotrade-postgres` et `marotrade-redis` existent déjà, les redémarrer sans les
supprimer afin de conserver leurs volumes :

```powershell
docker start marotrade-postgres marotrade-redis
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker exec marotrade-redis redis-cli ping
```

Une réponse Redis `PONG` confirme que le cache fonctionne. Après le démarrage
de PostgreSQL, redémarrer FastAPI pour qu'il relise `DATABASE_URL`.

Si Prisma retourne `P1000`, vérifier que `.env` contient exactement les
identifiants du conteneur :

```env
DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5433/marotrade_db?schema=public
```

Ne pas supprimer le volume PostgreSQL pour résoudre une erreur de mot de passe :
cela supprimerait les comptes et les analyses enregistrées.

### Mémoire du pipeline NLP

Le moteur réglementaire charge désormais XLM-RoBERTa au premier appel
`/api/alerts`, et non au démarrage de FastAPI. Le très lourd fallback BART est
désactivé par défaut. Sur une machine disposant de peu de mémoire virtuelle,
utiliser temporairement :

```env
NLP_LOCAL_MODEL_ENABLED=false
NLP_ZERO_SHOT_FALLBACK_ENABLED=false
```

Le système utilisera alors le fallback léger par règles sans bloquer l'API.

## Endpoints principaux

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`
- `POST /auth/verify-email`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `POST /api/score` : authentification obligatoire, résultat enregistré pour la PME
- `GET /api/me/analyses` : historique de la PME active
- `DELETE /api/me/analyses/{id}` : suppression limitée à la PME active

## Vérifications

```powershell
.\venv\Scripts\python.exe -B -m unittest discover -s tests -v
npm run build
```
