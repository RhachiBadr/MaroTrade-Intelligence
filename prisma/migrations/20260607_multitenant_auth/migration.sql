-- CreateEnum
CREATE TYPE "AlertLevel" AS ENUM ('CRITIQUE', 'ATTENTION', 'INFO');

-- CreateEnum
CREATE TYPE "AccordType" AS ENUM ('ALE', 'PREF', 'NPF', 'DOM');

-- CreateEnum
CREATE TYPE "MarketTrend" AS ENUM ('FORTE_CROISSANCE', 'CROISSANCE_STABLE', 'CROISSANCE_MODEREE', 'STAGNATION', 'DECLIN');

-- CreateEnum
CREATE TYPE "GrowthLabel" AS ENUM ('FUSEE', 'FORT', 'STABLE', 'LENT', 'DECLIN');

-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('PME', 'AGENT_PORT', 'ADMIN');

-- CreateEnum
CREATE TYPE "OrganizationType" AS ENUM ('PME', 'COOPERATIVE', 'EXPORTER');

-- CreateEnum
CREATE TYPE "MembershipRole" AS ENUM ('OWNER', 'ADMIN', 'MEMBER', 'VIEWER');

-- CreateEnum
CREATE TYPE "AnalysisStatus" AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED');

-- CreateEnum
CREATE TYPE "ProjectPipelineStage" AS ENUM ('PROSPECTION', 'NEGOTIATION', 'COMMANDE', 'EXPEDITION', 'LIVRAISON');

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "role" "UserRole" NOT NULL DEFAULT 'PME',
    "password" TEXT NOT NULL,
    "emailVerified" BOOLEAN NOT NULL DEFAULT false,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "lastLoginAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "organizations" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "type" "OrganizationType" NOT NULL DEFAULT 'PME',
    "country" TEXT NOT NULL DEFAULT 'Maroc',
    "city" TEXT,
    "sector" TEXT,
    "size" TEXT,
    "products" TEXT[],
    "targetMarkets" TEXT[],
    "exportExperience" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "organizations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "memberships" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "organizationId" TEXT NOT NULL,
    "role" "MembershipRole" NOT NULL DEFAULT 'MEMBER',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "memberships_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "refresh_tokens" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "tokenHash" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "revokedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "email_verification_tokens" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "tokenHash" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "usedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "email_verification_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "password_reset_tokens" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "tokenHash" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "usedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "password_reset_tokens_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "products" (
    "id" TEXT NOT NULL,
    "hsCode" TEXT NOT NULL,
    "hsCode6" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "nameAr" TEXT,
    "category" TEXT NOT NULL,
    "sector" TEXT NOT NULL,
    "description" TEXT,
    "emoji" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "products_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "countries" (
    "id" TEXT NOT NULL,
    "isoCode" TEXT NOT NULL,
    "isoCode2" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "nameAr" TEXT,
    "flag" TEXT,
    "region" TEXT NOT NULL,
    "accordLabel" TEXT NOT NULL,
    "accordType" "AccordType" NOT NULL,
    "droitsDouane" DOUBLE PRECISION NOT NULL,
    "easeBusiness" DOUBLE PRECISION NOT NULL,
    "politicalStability" DOUBLE PRECISION NOT NULL,
    "ruleOfLaw" DOUBLE PRECISION NOT NULL,
    "regulatoryQuality" DOUBLE PRECISION NOT NULL,
    "wbUpdatedAt" TIMESTAMP(3),
    "ocdeRiskCategory" INTEGER NOT NULL,
    "ocdeRiskScore" DOUBLE PRECISION NOT NULL,
    "ocdeRiskLabel" TEXT NOT NULL,
    "ocdeUpdatedAt" TIMESTAMP(3),
    "distanceKm" INTEGER NOT NULL,
    "lpi" DOUBLE PRECISION NOT NULL,
    "coutConteneur" INTEGER NOT NULL,
    "portPrincipal" TEXT,
    "freightLive" BOOLEAN NOT NULL DEFAULT false,
    "diasporaPopulation" INTEGER NOT NULL DEFAULT 0,
    "diasporaTransferts" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "countries_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analyses" (
    "id" TEXT NOT NULL,
    "userId" TEXT,
    "organizationId" TEXT,
    "productId" TEXT NOT NULL,
    "productName" TEXT NOT NULL,
    "hsCode" TEXT NOT NULL,
    "topN" INTEGER NOT NULL DEFAULT 5,
    "status" "AnalysisStatus" NOT NULL DEFAULT 'PENDING',
    "durationMs" INTEGER,
    "errorMessage" TEXT,
    "weightMarche" DOUBLE PRECISION NOT NULL DEFAULT 0.28,
    "weightAccord" DOUBLE PRECISION NOT NULL DEFAULT 0.22,
    "weightBusiness" DOUBLE PRECISION NOT NULL DEFAULT 0.18,
    "weightStabilite" DOUBLE PRECISION NOT NULL DEFAULT 0.12,
    "weightDiaspora" DOUBLE PRECISION NOT NULL DEFAULT 0.10,
    "weightLogistique" DOUBLE PRECISION NOT NULL DEFAULT 0.10,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "analyses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workspace_analyses" (
    "id" TEXT NOT NULL,
    "organizationId" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "productName" TEXT NOT NULL,
    "hsCode" TEXT NOT NULL,
    "topN" INTEGER NOT NULL,
    "results" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workspace_analyses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "scoring_results" (
    "id" TEXT NOT NULL,
    "analysisId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "rank" INTEGER NOT NULL,
    "scoreFinal" DOUBLE PRECISION NOT NULL,
    "scoreWeighted" DOUBLE PRECISION NOT NULL,
    "scoreXgboost" DOUBLE PRECISION NOT NULL,
    "shapValues" JSONB NOT NULL,
    "topAtouts" TEXT[],
    "topRisques" TEXT[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "scoring_results_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "dimension_scores" (
    "id" TEXT NOT NULL,
    "scoringResultId" TEXT NOT NULL,
    "nom" TEXT NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "poids" DOUBLE PRECISION NOT NULL,
    "contribution" DOUBLE PRECISION NOT NULL,
    "detail" JSONB NOT NULL,
    "interpretation" TEXT NOT NULL,

    CONSTRAINT "dimension_scores_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "trade_data" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "year" INTEGER NOT NULL,
    "valueUsd" DOUBLE PRECISION NOT NULL,
    "weightKg" DOUBLE PRECISION NOT NULL,
    "priceUsdKg" DOUBLE PRECISION NOT NULL,
    "source" TEXT NOT NULL DEFAULT 'UN_COMTRADE',
    "fetchedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "trade_data_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "historical_trade_data" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "year" INTEGER NOT NULL,
    "valueUsd" DOUBLE PRECISION NOT NULL,
    "source" TEXT NOT NULL DEFAULT 'UN_COMTRADE',

    CONSTRAINT "historical_trade_data_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "growth_metrics" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "cagr" DOUBLE PRECISION NOT NULL,
    "velocity" DOUBLE PRECISION NOT NULL,
    "momentum" DOUBLE PRECISION NOT NULL,
    "label" "GrowthLabel" NOT NULL,
    "interpretation" TEXT NOT NULL,
    "computedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "sourceYears" TEXT NOT NULL DEFAULT '2020-2022',

    CONSTRAINT "growth_metrics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "market_forecasts" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "historicalValues" JSONB NOT NULL,
    "historicalYears" JSONB NOT NULL,
    "forecastValues" JSONB NOT NULL,
    "forecastYears" JSONB NOT NULL,
    "lowerBound" JSONB NOT NULL,
    "upperBound" JSONB NOT NULL,
    "cagrHistorique" DOUBLE PRECISION NOT NULL,
    "cagrPrevu" DOUBLE PRECISION NOT NULL,
    "acceleration" DOUBLE PRECISION NOT NULL,
    "scoreFutur" DOUBLE PRECISION NOT NULL,
    "tendance" "MarketTrend" NOT NULL,
    "confiance" DOUBLE PRECISION NOT NULL,
    "valeur2022" DOUBLE PRECISION NOT NULL,
    "valeur2026" DOUBLE PRECISION NOT NULL,
    "modelVersion" TEXT NOT NULL DEFAULT 'prophet-1.1',
    "computedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "market_forecasts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "regulatory_alerts" (
    "id" TEXT NOT NULL,
    "externalId" TEXT,
    "titre" TEXT NOT NULL,
    "titreFr" TEXT NOT NULL,
    "niveau" "AlertLevel" NOT NULL,
    "source" TEXT NOT NULL,
    "sourceUrl" TEXT,
    "produitsHs" TEXT[],
    "produitsNoms" TEXT[],
    "resumeFr" TEXT NOT NULL,
    "impactExport" TEXT NOT NULL,
    "actionRequise" TEXT NOT NULL,
    "dateVigueur" TIMESTAMP(3),
    "datePublication" TIMESTAMP(3),
    "impactScore" DOUBLE PRECISION NOT NULL,
    "sourceFilable" BOOLEAN NOT NULL DEFAULT true,
    "llmConfiance" DOUBLE PRECISION,
    "llmEnhanced" BOOLEAN NOT NULL DEFAULT false,
    "delaiJours" INTEGER,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "regulatory_alerts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "regulatory_alert_countries" (
    "alertId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,

    CONSTRAINT "regulatory_alert_countries_pkey" PRIMARY KEY ("alertId","countryId")
);

-- CreateTable
CREATE TABLE "alert_subscriptions" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "organizationId" TEXT,
    "countryId" TEXT,
    "hsCode" TEXT,
    "minLevel" "AlertLevel" NOT NULL DEFAULT 'ATTENTION',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "alert_subscriptions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "saved_markets" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "organizationId" TEXT,
    "countryId" TEXT NOT NULL,
    "hsCode" TEXT NOT NULL,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "saved_markets_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "api_cache" (
    "id" TEXT NOT NULL,
    "cacheKey" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "payload" JSONB NOT NULL,
    "fetchedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "api_cache_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ports" (
    "id" TEXT NOT NULL,
    "unlocode" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "countryCode" TEXT NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "ports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "escales" (
    "id" TEXT NOT NULL,
    "portId" TEXT NOT NULL,
    "navireNom" TEXT NOT NULL,
    "navireImo" TEXT,
    "dateArrivee" TIMESTAMP(3) NOT NULL,
    "dateDepart" TIMESTAMP(3),
    "statut" TEXT NOT NULL,
    "imoDataRaw" JSONB,
    "imoDataNorm" JSONB,
    "validationErrors" TEXT[],
    "isNormalized" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "escales_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "manifestes" (
    "id" TEXT NOT NULL,
    "escaleId" TEXT NOT NULL,
    "hsCode" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "poidsKg" DOUBLE PRECISION NOT NULL,
    "valeurUsd" DOUBLE PRECISION NOT NULL,
    "exportateur" TEXT,
    "paysDest" TEXT,
    "imoCodeMarchandise" TEXT,
    "isValide" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "manifestes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "export_readiness_scores" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "scoreTotal" DOUBLE PRECISION NOT NULL,
    "certificationsScore" DOUBLE PRECISION,
    "capaciteProduction" DOUBLE PRECISION,
    "packagingNormes" DOUBLE PRECISION,
    "tracabilite" DOUBLE PRECISION,
    "actionPlan" JSONB,
    "lastEvaluatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "export_readiness_scores_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "profitability_simulations" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "prixVenteCible" DOUBLE PRECISION NOT NULL,
    "coutProduction" DOUBLE PRECISION NOT NULL,
    "volumeEstime" DOUBLE PRECISION NOT NULL,
    "coutFret" DOUBLE PRECISION,
    "droitsDouane" DOUBLE PRECISION,
    "fraisCertif" DOUBLE PRECISION,
    "margeNette" DOUBLE PRECISION,
    "roi" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "profitability_simulations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "b2b_buyers" (
    "id" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "companyName" TEXT NOT NULL,
    "contactName" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "website" TEXT,
    "platformSource" TEXT,
    "credibilityScore" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "b2b_buyers_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "export_projects" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "countryId" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "stage" "ProjectPipelineStage" NOT NULL DEFAULT 'PROSPECTION',
    "targetVolume" DOUBLE PRECISION,
    "expectedRevenue" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "export_projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "export_tasks" (
    "id" TEXT NOT NULL,
    "projectId" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "dueDate" TIMESTAMP(3),
    "isCompleted" BOOLEAN NOT NULL DEFAULT false,
    "documentRequired" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "export_tasks_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "competitor_prices" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "competitorCountry" TEXT NOT NULL,
    "platform" TEXT NOT NULL,
    "priceUsd" DOUBLE PRECISION NOT NULL,
    "priceChangePct" DOUBLE PRECISION,
    "url" TEXT,
    "detectedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "competitor_prices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_AlertSubscriptionToRegulatoryAlert" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "organizations_slug_key" ON "organizations"("slug");

-- CreateIndex
CREATE INDEX "organizations_slug_idx" ON "organizations"("slug");

-- CreateIndex
CREATE INDEX "memberships_organizationId_idx" ON "memberships"("organizationId");

-- CreateIndex
CREATE UNIQUE INDEX "memberships_userId_organizationId_key" ON "memberships"("userId", "organizationId");

-- CreateIndex
CREATE UNIQUE INDEX "refresh_tokens_tokenHash_key" ON "refresh_tokens"("tokenHash");

-- CreateIndex
CREATE INDEX "refresh_tokens_userId_idx" ON "refresh_tokens"("userId");

-- CreateIndex
CREATE INDEX "refresh_tokens_expiresAt_idx" ON "refresh_tokens"("expiresAt");

-- CreateIndex
CREATE UNIQUE INDEX "email_verification_tokens_tokenHash_key" ON "email_verification_tokens"("tokenHash");

-- CreateIndex
CREATE INDEX "email_verification_tokens_userId_idx" ON "email_verification_tokens"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "password_reset_tokens_tokenHash_key" ON "password_reset_tokens"("tokenHash");

-- CreateIndex
CREATE INDEX "password_reset_tokens_userId_idx" ON "password_reset_tokens"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "products_hsCode_key" ON "products"("hsCode");

-- CreateIndex
CREATE INDEX "products_hsCode6_idx" ON "products"("hsCode6");

-- CreateIndex
CREATE INDEX "products_category_idx" ON "products"("category");

-- CreateIndex
CREATE UNIQUE INDEX "countries_isoCode_key" ON "countries"("isoCode");

-- CreateIndex
CREATE UNIQUE INDEX "countries_isoCode2_key" ON "countries"("isoCode2");

-- CreateIndex
CREATE INDEX "countries_region_idx" ON "countries"("region");

-- CreateIndex
CREATE INDEX "countries_accordType_idx" ON "countries"("accordType");

-- CreateIndex
CREATE INDEX "analyses_userId_idx" ON "analyses"("userId");

-- CreateIndex
CREATE INDEX "analyses_organizationId_idx" ON "analyses"("organizationId");

-- CreateIndex
CREATE INDEX "analyses_productId_idx" ON "analyses"("productId");

-- CreateIndex
CREATE INDEX "analyses_createdAt_idx" ON "analyses"("createdAt");

-- CreateIndex
CREATE INDEX "workspace_analyses_organizationId_createdAt_idx" ON "workspace_analyses"("organizationId", "createdAt");

-- CreateIndex
CREATE INDEX "workspace_analyses_userId_idx" ON "workspace_analyses"("userId");

-- CreateIndex
CREATE INDEX "scoring_results_analysisId_idx" ON "scoring_results"("analysisId");

-- CreateIndex
CREATE INDEX "scoring_results_scoreFinal_idx" ON "scoring_results"("scoreFinal");

-- CreateIndex
CREATE UNIQUE INDEX "scoring_results_analysisId_countryId_key" ON "scoring_results"("analysisId", "countryId");

-- CreateIndex
CREATE INDEX "dimension_scores_scoringResultId_idx" ON "dimension_scores"("scoringResultId");

-- CreateIndex
CREATE INDEX "trade_data_productId_year_idx" ON "trade_data"("productId", "year");

-- CreateIndex
CREATE UNIQUE INDEX "trade_data_productId_countryId_year_key" ON "trade_data"("productId", "countryId", "year");

-- CreateIndex
CREATE INDEX "historical_trade_data_productId_countryId_idx" ON "historical_trade_data"("productId", "countryId");

-- CreateIndex
CREATE UNIQUE INDEX "historical_trade_data_productId_countryId_year_key" ON "historical_trade_data"("productId", "countryId", "year");

-- CreateIndex
CREATE INDEX "growth_metrics_productId_idx" ON "growth_metrics"("productId");

-- CreateIndex
CREATE UNIQUE INDEX "growth_metrics_productId_countryId_key" ON "growth_metrics"("productId", "countryId");

-- CreateIndex
CREATE INDEX "market_forecasts_productId_idx" ON "market_forecasts"("productId");

-- CreateIndex
CREATE INDEX "market_forecasts_scoreFutur_idx" ON "market_forecasts"("scoreFutur");

-- CreateIndex
CREATE UNIQUE INDEX "market_forecasts_productId_countryId_key" ON "market_forecasts"("productId", "countryId");

-- CreateIndex
CREATE UNIQUE INDEX "regulatory_alerts_externalId_key" ON "regulatory_alerts"("externalId");

-- CreateIndex
CREATE INDEX "regulatory_alerts_niveau_idx" ON "regulatory_alerts"("niveau");

-- CreateIndex
CREATE INDEX "regulatory_alerts_impactScore_idx" ON "regulatory_alerts"("impactScore");

-- CreateIndex
CREATE INDEX "regulatory_alerts_dateVigueur_idx" ON "regulatory_alerts"("dateVigueur");

-- CreateIndex
CREATE INDEX "alert_subscriptions_organizationId_idx" ON "alert_subscriptions"("organizationId");

-- CreateIndex
CREATE UNIQUE INDEX "alert_subscriptions_userId_countryId_hsCode_key" ON "alert_subscriptions"("userId", "countryId", "hsCode");

-- CreateIndex
CREATE INDEX "saved_markets_organizationId_idx" ON "saved_markets"("organizationId");

-- CreateIndex
CREATE UNIQUE INDEX "saved_markets_userId_countryId_hsCode_key" ON "saved_markets"("userId", "countryId", "hsCode");

-- CreateIndex
CREATE UNIQUE INDEX "api_cache_cacheKey_key" ON "api_cache"("cacheKey");

-- CreateIndex
CREATE INDEX "api_cache_expiresAt_idx" ON "api_cache"("expiresAt");

-- CreateIndex
CREATE INDEX "api_cache_source_idx" ON "api_cache"("source");

-- CreateIndex
CREATE UNIQUE INDEX "ports_unlocode_key" ON "ports"("unlocode");

-- CreateIndex
CREATE INDEX "escales_portId_idx" ON "escales"("portId");

-- CreateIndex
CREATE INDEX "escales_dateArrivee_idx" ON "escales"("dateArrivee");

-- CreateIndex
CREATE INDEX "manifestes_escaleId_idx" ON "manifestes"("escaleId");

-- CreateIndex
CREATE INDEX "manifestes_hsCode_idx" ON "manifestes"("hsCode");

-- CreateIndex
CREATE UNIQUE INDEX "export_readiness_scores_userId_key" ON "export_readiness_scores"("userId");

-- CreateIndex
CREATE INDEX "b2b_buyers_countryId_productId_idx" ON "b2b_buyers"("countryId", "productId");

-- CreateIndex
CREATE INDEX "competitor_prices_productId_idx" ON "competitor_prices"("productId");

-- CreateIndex
CREATE UNIQUE INDEX "_AlertSubscriptionToRegulatoryAlert_AB_unique" ON "_AlertSubscriptionToRegulatoryAlert"("A", "B");

-- CreateIndex
CREATE INDEX "_AlertSubscriptionToRegulatoryAlert_B_index" ON "_AlertSubscriptionToRegulatoryAlert"("B");

-- AddForeignKey
ALTER TABLE "memberships" ADD CONSTRAINT "memberships_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "memberships" ADD CONSTRAINT "memberships_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "refresh_tokens" ADD CONSTRAINT "refresh_tokens_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "email_verification_tokens" ADD CONSTRAINT "email_verification_tokens_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "password_reset_tokens" ADD CONSTRAINT "password_reset_tokens_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_analyses" ADD CONSTRAINT "workspace_analyses_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workspace_analyses" ADD CONSTRAINT "workspace_analyses_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "scoring_results" ADD CONSTRAINT "scoring_results_analysisId_fkey" FOREIGN KEY ("analysisId") REFERENCES "analyses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "scoring_results" ADD CONSTRAINT "scoring_results_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "dimension_scores" ADD CONSTRAINT "dimension_scores_scoringResultId_fkey" FOREIGN KEY ("scoringResultId") REFERENCES "scoring_results"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "trade_data" ADD CONSTRAINT "trade_data_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "trade_data" ADD CONSTRAINT "trade_data_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "historical_trade_data" ADD CONSTRAINT "historical_trade_data_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "historical_trade_data" ADD CONSTRAINT "historical_trade_data_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "growth_metrics" ADD CONSTRAINT "growth_metrics_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "growth_metrics" ADD CONSTRAINT "growth_metrics_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "market_forecasts" ADD CONSTRAINT "market_forecasts_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "market_forecasts" ADD CONSTRAINT "market_forecasts_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "regulatory_alert_countries" ADD CONSTRAINT "regulatory_alert_countries_alertId_fkey" FOREIGN KEY ("alertId") REFERENCES "regulatory_alerts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "regulatory_alert_countries" ADD CONSTRAINT "regulatory_alert_countries_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alert_subscriptions" ADD CONSTRAINT "alert_subscriptions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alert_subscriptions" ADD CONSTRAINT "alert_subscriptions_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alert_subscriptions" ADD CONSTRAINT "alert_subscriptions_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "saved_markets" ADD CONSTRAINT "saved_markets_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "saved_markets" ADD CONSTRAINT "saved_markets_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES "organizations"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "saved_markets" ADD CONSTRAINT "saved_markets_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "escales" ADD CONSTRAINT "escales_portId_fkey" FOREIGN KEY ("portId") REFERENCES "ports"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "manifestes" ADD CONSTRAINT "manifestes_escaleId_fkey" FOREIGN KEY ("escaleId") REFERENCES "escales"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "export_readiness_scores" ADD CONSTRAINT "export_readiness_scores_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "profitability_simulations" ADD CONSTRAINT "profitability_simulations_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "profitability_simulations" ADD CONSTRAINT "profitability_simulations_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "profitability_simulations" ADD CONSTRAINT "profitability_simulations_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "b2b_buyers" ADD CONSTRAINT "b2b_buyers_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "b2b_buyers" ADD CONSTRAINT "b2b_buyers_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "export_projects" ADD CONSTRAINT "export_projects_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "export_projects" ADD CONSTRAINT "export_projects_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "countries"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "export_projects" ADD CONSTRAINT "export_projects_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "export_tasks" ADD CONSTRAINT "export_tasks_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "export_projects"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "competitor_prices" ADD CONSTRAINT "competitor_prices_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_AlertSubscriptionToRegulatoryAlert" ADD CONSTRAINT "_AlertSubscriptionToRegulatoryAlert_A_fkey" FOREIGN KEY ("A") REFERENCES "alert_subscriptions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_AlertSubscriptionToRegulatoryAlert" ADD CONSTRAINT "_AlertSubscriptionToRegulatoryAlert_B_fkey" FOREIGN KEY ("B") REFERENCES "regulatory_alerts"("id") ON DELETE CASCADE ON UPDATE CASCADE;
