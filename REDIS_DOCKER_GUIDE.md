# Guide Redis en Docker pour MaroTrade Intelligence

## ✅ Avant de commencer

- **Docker Desktop instalé** : https://www.docker.com/products/docker-desktop
- **Windows 11+ recommandé** (WSL2 intégré)
- **Ports libres** : 6379 (Redis), 5433 (PostgreSQL), 8501 (App)

## 🚀 Démarrage Rapide

### Option 1 : Avec docker-compose simple (Recommandé)

```bash
cd docker
docker-compose -f docker-compose.dev.yml up -d
```

### Option 2 : Avec le script PowerShell (Facile)

```powershell
# Donner les permissions d'exécution
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# Démarrer les services
./docker/docker-manage.ps1 up

# Consulter les logs
./docker/docker-manage.ps1 logs
```

### Option 3 : Commandes manuelles

```bash
# Démarrer
docker-compose -f docker/docker-compose.dev.yml up -d

# Arrêter
docker-compose -f docker/docker-compose.dev.yml down

# Supprimer les volumes (données persistantes)
docker-compose -f docker/docker-compose.dev.yml down -v
```

## 🔍 Vérification du Status

### Voir les conteneurs

```bash
docker ps
```

Vous devriez voir :
```
CONTAINER ID   IMAGE              STATUS          PORTS
xxx            redis:7-alpine     Up 2 mins       0.0.0.0:6379->6379/tcp
xxx            postgres:15-alpine Up 2 mins       0.0.0.0:5433->5432/tcp
```

### Tester Redis

```bash
# Via PowerShell
./docker/docker-manage.ps1 redis-cli

# Ou directement
docker exec -it marotrade-redis-dev redis-cli

# Une fois connecté :
PING        # Doit répondre "PONG"
SET test 1  # Tester une écriture
GET test    # Doit retourner "1"
```

### Tester PostgreSQL

```bash
./docker/docker-manage.ps1 psql

# Ou directement
docker exec -it marotrade-postgres-dev psql -U postgres -d marotrade_db
```

## 🐍 Lancer l'Application avec Redis (Local Python)

### 1. Vérifier que Docker est actif

```bash
docker ps  # Voir les conteneurs
```

### 2. Installer les dépendances locales

```bash
cd c:\Users\HP\Desktop\MaroTrade Intelligence
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Lancer l'app (elle se connectera auto à Redis)

```bash
# Les variables d'environnement sont automatiquement utilisées
python start_services.py test    # Test rapide
streamlit run dashboard.py       # Lancer dashboard
```

## 📊 Commandes Utiles

| Commande | Description |
|----------|-------------|
| `docker-compose -f docker/docker-compose.dev.yml up -d` | Démarrer les services en arrière-plan |
| `docker-compose -f docker/docker-compose.dev.yml down` | Arrêter les services |
| `docker-compose -f docker/docker-compose.dev.yml logs -f` | Voir les logs en temps réel |
| `docker exec -it marotrade-redis-dev redis-cli` | CLI Redis |
| `docker exec -it marotrade-postgres-dev psql -U postgres` | CLI PostgreSQL |
| `docker volumes ls` | Lister les volumes persistants |
| `docker system prune` | Nettoyer les images/conteneurs inutilisés |

## 🔧 Variables d'Environnement

L'app utilise automatiquement :
- `REDIS_HOST=redis` (depuis Docker Compose)
- `REDIS_PORT=6379`
- `DATABASE_URL=postgresql://...@postgres:5432/...`

Modifications dans `docker/.env` ou via les variables d'environnement.

## ⚠️ Dépannage

### Redis ne démarre pas

```bash
# Vérifier la disponibilité du port
netstat -ano | findstr :6379

# Libérer le port si occupé
taskkill /PID <PID> /F

# Redémarrer
docker-compose -f docker/docker-compose.dev.yml restart redis
```

### PostgreSQL impossible de se connecter

```bash
# Vérifier la santé
docker-compose -f docker/docker-compose.dev.yml ps

# Voir les erreurs
docker-compose -f docker/docker-compose.dev.yml logs postgres
```

### Cache ne fonctionne pas

```bash
# Vérifier la connexion
python -c "
from services.cache import CacheService
cache = CacheService()
cache.set('test', {'msg': 'ok'})
print(cache.get('test'))
"
```

## 🎯 Avantages Redis en Docker

✅ **Installation zéro config** - Une ligne Docker  
✅ **Portable** - Fonctionne sur Windows/Mac/Linux  
✅ **Prêt pour le cloud** - Déployer sur AWS/GCP sans changera  
✅ **Persistant** - Les données survivent aux redémarrages  
✅ **Isolé** - Aucun impact sur votre système Windows  
✅ **Facilement supprimable** - `docker-compose down -v` récupère l'espace disque