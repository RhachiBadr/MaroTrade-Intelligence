# MaroTrade Intelligence - Docker Management Script
# Usage: .\docker-manage.ps1 [command]

param(
    [Parameter(Position = 0)]
    [ValidateSet(
        "up", "down", "logs", "logs-app", "ps", "redis-cli", "psql", "pgadmin",
        "shell", "test", "clean", "rebuild", "prune", "status", "help"
    )]
    [string]$command = "help"
)

$docker_dir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Title {
    param([string]$text)
    Write-Host ""
    Write-Host ('=' * 72) -ForegroundColor Cyan
    Write-Host $text -ForegroundColor Cyan
    Write-Host ('=' * 72) -ForegroundColor Cyan
}

function Write-Success {
    param([string]$text)
    Write-Host "SUCCESS: $text" -ForegroundColor Green
}

function Write-Error {
    param([string]$text)
    Write-Host "ERROR: $text" -ForegroundColor Red
}

function Write-Info {
    param([string]$text)
    Write-Host "INFO: $text" -ForegroundColor Yellow
}

function Show-Help {
    Write-Title "MaroTrade Docker Commands"
    Write-Host @"
Commandes disponibles:

  Services de base:
    up          Démarrer les services (Redis + PostgreSQL + PgAdmin)
    down        Arrêter les services
    restart     Redémarrer les services
    status      Afficher le statut des conteneurs

  Logs et monitoring:
    logs        Logs Redis + PostgreSQL
    logs-app    Logs de l'application
    ps          Lister les conteneurs

  Connexions:
    redis-cli   Interface Redis CLI
    psql        Interface PostgreSQL CLI
    pgadmin     Ouvrir PgAdmin (http://localhost:5050)
    shell       Ouvrir un shell dans le conteneur app

  Maintenance:
    clean       Supprimer conteneurs et volumes de dev
    rebuild     Reconstruire l'image et démarrer
    prune       Nettoyer les données Docker inutilisées
    test        Tester la connexion Redis

  Autres:
    help        Afficher cette aide

Exemples:
    .\docker-manage.ps1 up
    .\docker-manage.ps1 logs
    .\docker-manage.ps1 redis-cli
"@
}

function Start-Services {
    Write-Title "Démarrage des services"
    Push-Location $docker_dir
    docker version >$null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Docker n'est pas disponible"
        Pop-Location
        return
    }

    Write-Info "Démarrage des conteneurs"
    docker-compose -f docker-compose.dev.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services démarrés"
        Write-Host "  Redis       : localhost:6379"
        Write-Host "  PostgreSQL  : localhost:5433"
        Write-Host "  PgAdmin     : http://localhost:5050"
        Write-Host "  Application : http://localhost:8501"
    }
    Pop-Location
}

function Stop-Services {
    Write-Title "Arrêt des services"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services arrêtés"
    }
    Pop-Location
}

function Restart-Services {
    Write-Title "Redémarrage des services"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml restart
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services redémarrés"
    }
    Pop-Location
}

function Show-Status {
    Write-Title "Statut des services"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml ps
    Pop-Location
}

function Show-Logs {
    Write-Title "Logs Redis et PostgreSQL"
    Write-Info "Appuyez sur Ctrl+C pour arrêter"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml logs -f redis postgres
    Pop-Location
}

function Show-App-Logs {
    Write-Title "Logs application"
    Write-Info "Appuyez sur Ctrl+C pour arrêter"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml logs -f marotrade
    Pop-Location
}

function Show-Processes {
    Write-Title "Conteneurs actifs"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml ps
    Pop-Location
}

function Connect-Redis {
    Write-Title "Redis CLI"
    Write-Info "Tapez PING pour tester, puis exit pour quitter"
    docker exec -it marotrade-redis-dev redis-cli
}

function Connect-Postgres {
    Write-Title "PostgreSQL CLI"
    docker exec -it marotrade-postgres-dev psql -U postgres -d marotrade_db
}

function Open-PgAdmin {
    Write-Title "PgAdmin"
    Write-Info "Identifiant: admin@marotrade.ma"
    Write-Info "Mot de passe: adminpassword"
    Start-Process "http://localhost:5050"
    Write-Success "PgAdmin ouvert"
}

function Enter-Container {
    Write-Title "Shell conteneur app"
    docker exec -it marotrade-intelligence sh
}

function Test-Redis {
    Write-Title "Test Redis"
    Write-Info "Vérification de la connexion..."
    try {
        $result = docker exec marotrade-redis-dev redis-cli PING 2>&1
        if ($result -eq "PONG") {
            Write-Success "Redis répond correctement"
        } else {
            Write-Error "Redis ne répond pas"
        }
    } catch {
        Write-Error "Impossible de se connecter à Redis"
    }
}

function Clear-Containers {
    Write-Title "Nettoyage des conteneurs et volumes"
    Write-Host "ATTENTION: cela supprimera les conteneurs et volumes de dev" -ForegroundColor Yellow
    $confirm = Read-Host "Êtes-vous sûr? (oui/non)"
    if ($confirm -eq "oui") {
        Push-Location $docker_dir
        docker-compose -f docker-compose.dev.yml down -v
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Nettoyage terminé"
        }
        Pop-Location
    }
}

function Update-Services {
    Write-Title "Reconstruire et démarrer"
    Push-Location $docker_dir
    docker-compose -f docker-compose.dev.yml up --build -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Reconstruit et démarré"
    }
    Pop-Location
}

function Remove-Docker {
    Write-Title "Nettoyage Docker"
    Write-Host "ATTENTION: cela supprimera les images et volumes inutilisés" -ForegroundColor Yellow
    $confirm = Read-Host "Êtes-vous sûr? (oui/non)"
    if ($confirm -eq "oui") {
        docker system prune -a --volumes -f
        Write-Success "Nettoyage Docker terminé"
    }
}

switch ($command) {
    "up"          { Start-Services }
    "down"        { Stop-Services }
    "restart"     { Restart-Services }
    "status"      { Show-Status }
    "logs"        { Show-Logs }
    "logs-app"    { Show-App-Logs }
    "ps"          { Show-Processes }
    "redis-cli"   { Connect-Redis }
    "psql"        { Connect-Postgres }
    "pgadmin"     { Open-PgAdmin }
    "shell"       { Enter-Container }
    "test"        { Test-Redis }
    "clean"       { Clear-Containers }
    "rebuild"     { Update-Services }
    "prune"       { Remove-Docker }
    "help"        { Show-Help }
    default        { Show-Help }
}
