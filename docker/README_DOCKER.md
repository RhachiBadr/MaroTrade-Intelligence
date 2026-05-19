# 🚀 MaroTrade Intelligence — Docker Configuration

Configuration Docker complète pour MaroTrade Intelligence avec Redis, PostgreSQL, PgAdmin et l'application Streamlit.

## 📁 Structure des fichiers

```
docker/
├── .env                        # Variables d'environnement (secrets)
├── docker-compose.yml          # Production: Redis + PostgreSQL + App + Frontend
├── docker-compose.dev.yml      # Développement: Redis + PostgreSQL + PgAdmin (léger)
├── Dockerfile                  # Image multi-stage optimisée
├── docker-manage.ps1           # Script PowerShell de gestion
├── init-db.sql                 # Initialisation PostgreSQL
└── README.md                   # Cette documentation
```

## ⚡ Démarrage Rapide

### 1. Prérequis

- **Docker Desktop** installé (Windows 10+, WSL2)
- **Port libres** : 6379 (Redis), 5433 (PostgreSQL), 8501 (App), 5050 (PgAdmin)

### 2. Démarrer les services (choix)

#### Option A : Avec PowerShell (Recommandé Windows)

```powershell
cd docker
.\docker-manage.ps1 up

# Voir les logs
.\docker-manage.ps1 logs

# Arrêter
.\docker-manage.ps1 down
```

#### Option B : Avec Docker Compose directement

```bash
cd docker

# Développement (léger)
docker-compose -f docker-compose.dev.yml up -d

# Production (complet)
docker-compose up -d

# Arrêter
docker-compose down
```

## 🎯 Commandes Disponibles

### Services

| Commande | Pour |
|----------|------|
| `./docker-manage.ps1 up` | Démarrer tous les services |
| `./docker-manage.ps1 down` | Arrêter tous les services |
| `./docker-manage.ps1 restart` | Redémarrer tous les services |
| `./docker-manage.ps1 status` | Voir le statut des conteneurs |

### Logs et Monitoring

| Commande | Pour |
|----------|------|
| `./docker-manage.ps1 logs` | Voir les logs Redis + PostgreSQL |
| `./docker-manage.ps1 logs-app` | Voir les logs de l'application |
| `./docker-manage.ps1 ps` | Lister les conteneurs actifs |
| `./docker-manage.ps1 test` | Tester la connexion Redis |

### Connexions et Interfaces

| Commande | Pour | Accès |
|----------|------|-------|
| `./docker-manage.ps1 redis-cli` | Redis CLI interactif | redis-cli |
| `./docker-manage.ps1 psql` | PostgreSQL CLI interactif | psql |
| `./docker-manage.ps1 pgadmin` | Ouvrir PgAdmin | http://localhost:5050 |
| `./docker-manage.ps1 shell` | Shell du conteneur app | bash |

### Maintenance

| Commande | Pour |
|----------|------|
| `./docker-manage.ps1 clean` | Supprimer conteneurs + volumes (données) |
| `./docker-manage.ps1 rebuild` | Reconstruire les images |
| `./docker-manage.ps1 prune` | Nettoyer Docker globalement |

## 📊 Points d'Accès

Une fois les services démarrés :

| Service | URL / Host | Port | Identifiants |
|---------|-----------|------|-------------|
| **Redis** | localhost | 6379 | - |
| **PostgreSQL** | localhost | 5433 | postgres / postgrespassword |
| **PgAdmin** | http://localhost:5050 | 80 | admin@marotrade.ma / adminpassword |
| **Application** | http://localhost:8501 | 8501 | - |

## 🔧 Configuration

### .env (Variables d'environnement)

Le fichier `docker/.env` contient :

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_DB=marotrade_db
DATABASE_URL=postgresql://...

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API Keys (optionnels)
COMTRADE_API_KEY=
ITC_API_KEY=
FREIGHTOS_API_KEY=
ANTHROPIC_API_KEY=

# Application
LOG_LEVEL=INFO
ENVIRONMENT=docker
```

⚠️ **Sécurité** : Pour la production, changer les mots de passe !

### Dockerfile

Multi-stage build optimisé :
1. **Stage Builder** : Compilation des dépendances (build-essential, libpq-dev)
2. **Stage Runtime** : Image finale avec venv + code (utilisateur non-root)

Taille résultante : ~300MB (vs ~900MB avec python:3.11 full)

### docker-compose.yml vs .dev.yml

**docker-compose.yml** (Production)
- Redis + PostgreSQL + App + Frontend + PgAdmin
- Logging JSON avec rotation
- Healthchecks avancés
- Restart policies

**docker-compose.dev.yml** (Développement)
- Redis + PostgreSQL + PgAdmin uniquement
- Bootstrap rapide
- Logs console

## 📝 Exemples d'Utilisation

### Tester Redis

```powershell
.\docker-manage.ps1 redis-cli
# Une fois connecté :
PING        # Doit retourner PONG
SET key 1   # Créer une clé
GET key     # Lire la clé
```

### Voir les logs en temps réel

```powershell
.\docker-manage.ps1 logs-app
# Appuyez sur Ctrl+C pour arrêter
```

### Accéder à la base de données via PgAdmin

```powershell
.\docker-manage.ps1 pgadmin
# Ouvre http://localhost:5050 dans le navigateur
# Se connecter avec admin@marotrade.ma / adminpassword
```

### Nettoyer les données

```powershell
.\docker-manage.ps1 clean
# Confirmer avec "oui"
# Supprime TOUS les volumes Docker
```

## 🐛 Dépannage

### Redis n'est pas accessible

```powershell
# Vérifier si le conteneur tourne
.\docker-manage.ps1 status

# Vérifier les logs
.\docker-manage.ps1 logs

# Redémarrer
.\docker-manage.ps1 restart redis
```

### PostgreSQL ne démarre pas

```powershell
# Vérifier le statut
docker-compose -f docker-compose.dev.yml ps

# Voir les erreurs
docker-compose -f docker-compose.dev.yml logs postgres

# Nettoyer et recommencer
.\docker-manage.ps1 clean
.\docker-manage.ps1 up
```

### Port déjà utilisé

```powershell
# Trouver quel processus utilise le port (exemple: 6379)
netstat -ano | findstr :6379

# Arrêter le processus (remplacer PID)
taskkill /PID <PID> /F

# Redémarrer Docker
.\docker-manage.ps1 restart
```

### L'application démarre mais ne répond pas

```powershell
# Voir les logs de l'app
.\docker-manage.ps1 logs-app

# Accéder au shell
.\docker-manage.ps1 shell

# Une fois dans le shell
python start_services.py test  # Tester les services
```

## 🚀 Passage en Production

1. **Éditer `.env`** avec valeurs sécurisées
2. **Utiliser `docker-compose.yml`** au lieu de `.dev.yml`
3. **Ajouter un reverse proxy** (Nginx/Traefik)
4. **Configurer les backups** PostgreSQL
5. **Configurer le monitoring** (Prometheus + Grafana)

## 📚 Ressources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)

## 💡 Tips

- Les volumes Docker persisten les données même après arrêt
- Utiliser `docker system prune` pour libérer de l'espace disque
- Pour développement, garder `.dev.yml` actif (moins de ressources)
- Les logs sont limités à 20MB par conteneur pour éviter de saturer