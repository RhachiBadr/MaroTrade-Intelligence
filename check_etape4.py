import os

print("=== VÉRIFICATION CONFIGURATION ÉTAPE 4 ===")
print()

# Variables d'environnement
print("Variables d'environnement :")
for key in ['DATABASE_URL', 'REDIS_URL', 'ANTHROPIC_API_KEY']:
    value = os.getenv(key, 'NON DÉFINIE')
    if len(value) > 20:
        masked = value[:20] + '...'
    else:
        masked = value
    print(f"  {key}: {masked}")

print()

# Vérifier si Prisma est installé
try:
    import prisma
    print("✅ Prisma client installé")
except ImportError:
    print("❌ Prisma client NON installé")

# Vérifier si Redis est disponible
try:
    import redis
    print("✅ Redis client installé")
except ImportError:
    print("❌ Redis client NON installé")

print()
print("=== PRÊT POUR ÉTAPE 4 ===")