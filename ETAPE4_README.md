# MaroTrade Intelligence — Étape 4 : Migration Infrastructure

## Vue d'ensemble

L'Étape 4 migre MaroTrade Intelligence vers une infrastructure de production avec :
- **PostgreSQL** : Base de données persistante pour toutes les données
- **Redis** : Cache distribué haute performance
- **Authentification JWT** : Sécurité API avec utilisateurs et rôles
- **Rate Limiting** : Protection contre les abus API

## Prérequis

### Variables d'environnement

Créer/modifier `docker.env` :

```bash
# Base de données PostgreSQL
DATABASE_URL=postgresql://marotrade:password@localhost:5432/marotrade

# Cache Redis
REDIS_URL=redis://localhost:6379

# API externes (existantes)
ANTHROPIC_API_KEY=sk-ant-...
UN_COMTRADE_API_KEY=your_key
WORLD_BANK_API_KEY=your_key
GOOGLE_TRENDS_API_KEY=your_key

# Sécurité
JWT_SECRET_KEY=marotrade-secret-key-change-in-production-2024

# Cache
CACHE_DIR=.cache_marotrade
```

### Services externes

#### PostgreSQL
```bash
# Avec Docker
docker run --name marotrade-postgres \
  -e POSTGRES_DB=marotrade \
  -e POSTGRES_USER=marotrade \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Ou installer localement
```

#### Redis
```bash
# Avec Docker
docker run --name marotrade-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Ou installer localement
```

## Installation des dépendances

```bash
# Installer les nouvelles dépendances
pip install -r requirements.txt

# Générer le client Prisma
prisma generate
```

## Exécution de l'Étape 4

### Script automatisé (recommandé)

```bash
# Exécuter toutes les étapes automatiquement
python scripts/run_etape4.py
```

### Étapes manuelles

#### 1. Migration base de données

```bash
# Appliquer le schéma Prisma
prisma db push

# Migrer les données statiques
python scripts/migrate_static_data.py

# Migrer les données cache
python scripts/migrate_cache_data.py
```

#### 2. Mise à jour des services

```bash
# Mettre à jour les services pour Étape 4
python scripts/update_services_etape4.py
```

#### 3. Tests

```bash
# Tester les connexions
python -c "
import asyncio
from prisma import Prisma
import redis

# Test PostgreSQL
db = Prisma()
asyncio.run(db.connect())
print('✅ PostgreSQL OK')
asyncio.run(db.disconnect())

# Test Redis
r = redis.from_url('redis://localhost:6379')
r.ping()
print('✅ Redis OK')
"
```

#### 4. Création utilisateur admin

```bash
# Créer un administrateur
python -c "
import asyncio
from prisma import Prisma
from api import get_password_hash

async def create_admin():
    db = Prisma()
    await db.connect()
    hashed = get_password_hash('admin123')
    admin = await db.user.create(data={
        'email': 'admin@marotrade.ma',
        'hashedPassword': hashed,
        'companyName': 'MaroTrade Intelligence',
        'role': 'ADMIN',
        'isActive': True
    })
    print('✅ Admin créé: admin@marotrade.ma / admin123')
    await db.disconnect()

asyncio.run(create_admin())
"
```

## Démarrage des services

### API FastAPI (avec authentification)

```bash
# Démarrer l'API
python api.py

# Tester l'authentification
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@marotrade.ma", "password": "admin123"}'

# Utiliser l'API avec token
curl -X GET "http://localhost:8000/api/scoring?product_name=huile%20d%27argan&hs_code=151590" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Dashboard Streamlit

```bash
# Dashboard scoring
streamlit run dashboard.py

# Dashboard veille réglementaire
streamlit run dashboard_c02.py
```

### Interface Next.js

```bash
cd marotrade-frontend
npm install
npm run dev
```

## Structure mise à jour

### Base de données (25+ tables)

- `User` : Utilisateurs avec rôles
- `Country` : Pays avec indicateurs complets
- `Product` : Produits avec codes HS
- `TradeData` : Données commerciales UN Comtrade
- `GrowthIndicator` : Indicateurs de croissance calculés
- `Forecast` : Prévisions Prophet
- `Analysis` : Analyses de scoring sauvegardées
- `RegulatoryAlert` : Alertes réglementaires
- `LLMAnalysis` : Analyses Claude sauvegardées

### Cache multi-niveau

1. **Redis** : Cache haute performance (1h TTL)
2. **Filesystem** : Cache persistant (.cache_marotrade/)

### Authentification

- **JWT tokens** : Authentification stateless
- **Rôles** : ADMIN, USER, PREMIUM
- **Rate limiting** : 100 req/minute par utilisateur

## Tests et validation

### Tests automatisés

```bash
# Tests API
pytest tests/ -v

# Tests base de données
python -c "
from scripts.test_database import test_all
test_all()
"
```

### Validation manuelle

1. **Connexion admin** : Login avec admin@marotrade.ma
2. **Scoring complet** : Analyser un produit/marché
3. **Veille réglementaire** : Vérifier les alertes RSS
4. **Cache Redis** : Vérifier la persistance des données
5. **Performance** : Comparer temps de réponse

## Monitoring et logs

### Métriques clés

- **Temps de réponse API** : < 2 secondes
- **Taux de succès cache** : > 90%
- **Utilisation Redis** : Monitorer mémoire/débit
- **Erreurs base de données** : Logs Prisma

### Logs applicatifs

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Dépannage

### Problèmes courants

#### Erreur connexion PostgreSQL
```bash
# Vérifier le service
docker ps | grep postgres

# Logs du conteneur
docker logs marotrade-postgres

# Test connexion
psql postgresql://marotrade:password@localhost:5432/marotrade
```

#### Erreur connexion Redis
```bash
# Vérifier le service
docker ps | grep redis

# Test connexion
redis-cli ping
```

#### Erreur JWT
- Vérifier `JWT_SECRET_KEY` dans les variables d'environnement
- Régénérer les tokens si clé changée

### Rollback

En cas de problème majeur :

```bash
# Supprimer les migrations Prisma
prisma db push --force-reset

# Vider Redis
redis-cli FLUSHALL

# Restaurer backup filesystem cache
# (les données statiques sont recréées par migrate_static_data.py)
```

## Prochaines étapes

Après l'Étape 4 réussie :

1. **Étape 5** : Production et scaling
   - Déploiement Railway/Vercel
   - Monitoring Sentry
   - Tests de charge

2. **Étape 6** : Fonctionnalités avancées
   - Module recommandations IA
   - Alertes proactives email/SMS
   - Traçabilité blockchain

## Support

- **Documentation complète** : `claude.md`
- **Issues GitHub** : Pour bugs et améliorations
- **Contact** : admin@marotrade.ma

---

*Étape 4 — Migration Infrastructure — MaroTrade Intelligence v2.0*