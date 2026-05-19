-- ════════════════════════════════════════════════════════════════════════════
-- MaroTrade Intelligence — Initialisation PostgreSQL
-- ════════════════════════════════════════════════════════════════════════════
-- Ce fichier s'exécute automatiquement au démarrage du conteneur PostgreSQL

-- 1. Créer les schémas
CREATE SCHEMA IF NOT EXISTS marotrade;
CREATE SCHEMA IF NOT EXISTS cache;
CREATE SCHEMA IF NOT EXISTS logs;

-- 2. Extension UUID pour les IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 3. Permissions
GRANT ALL PRIVILEGES ON SCHEMA marotrade TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA cache TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA logs TO postgres;

-- 4. Commentaires
COMMENT ON SCHEMA marotrade IS 'Schéma principal — données de scoring et alertes';
COMMENT ON SCHEMA cache IS 'Cache distribué pour les résultats API (optionnel si Redis)';
COMMENT ON SCHEMA logs IS 'Logs structurés de l'application';

-- 5. Création des tables de base (optionnel - à adapter selon vos besoins)

-- Table : Analyses (résultats de scoring)
CREATE TABLE IF NOT EXISTS marotrade.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_name VARCHAR(255) NOT NULL,
    hs_code VARCHAR(20) NOT NULL,
    market_results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table : Alertes réglementaires
CREATE TABLE IF NOT EXISTS marotrade.regulatory_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hs_code VARCHAR(20),
    product_name VARCHAR(255),
    alert_level VARCHAR(50),
    alert_text TEXT,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Indexes pour performance
CREATE INDEX IF NOT EXISTS idx_analyses_hs_code ON marotrade.analyses(hs_code);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON marotrade.analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_level ON marotrade.regulatory_alerts(alert_level);

-- 7. Afficher le statut
\echo '═══════════════════════════════════════════════════════════════════════════'
\echo 'MaroTrade Intelligence — Base de données initialisée'
\echo '═══════════════════════════════════════════════════════════════════════════'
\echo 'Schémas créés : marotrade, cache, logs'
\echo 'Tables créées : analyses, regulatory_alerts'
\echo '═══════════════════════════════════════════════════════════════════════════'