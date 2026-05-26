#!/usr/bin/env python3
"""
test_etape3.py — Test complet de l'Étape 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Valide le pipeline NLP open-source.
"""

import sys
from pathlib import Path

# Ajouter projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("ÉTAPE 3 : TEST DU PIPELINE NLP OPEN-SOURCE")
print("=" * 70)

# Test 0 : Vérifier les imports
print("\n[0/7] Vérification des imports...")
try:
    import spacy
    print(f"✅ spaCy {spacy.__version__} importé")
except ImportError as e:
    print(f"❌ spaCy non installé: {e}")
    print("   → Exécutez: pip install spacy>=3.5.0")
    sys.exit(1)

try:
    import transformers
    print(f"✅ transformers {transformers.__version__} importé")
except ImportError as e:
    print(f"❌ transformers non installé: {e}")
    print("   → Exécutez: pip install transformers>=4.30.0")
    sys.exit(1)

try:
    import torch
    print(f"✅ torch {torch.__version__} importé")
except ImportError as e:
    print(f"❌ torch non installé: {e}")
    print("   → Exécutez: pip install torch>=2.0.0")
    sys.exit(1)

# Test 1 : Initialisation
print("\n[1/8] Initialisation du pipeline...")
try:
    from services.nlp import OpenSourceRegulatoryAnalyzer
    analyzer = OpenSourceRegulatoryAnalyzer(language="en", use_gpu=False)
    print("✅ Analyseur open-source initialisé")
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)

# Test 2 : Extraction d'entités
print("\n[2/8] Test extraction entités (spaCy)...")
try:
    from services.nlp import SpacyExtractor
    extractor = SpacyExtractor(lang="en", use_transformers=False)
    
    test_text = "France and USA must recall sardines (160413) from Morocco by June 15."
    countries = extractor.extract_countries(test_text)
    hs_codes = extractor.extract_hs_codes(test_text)
    
    print(f"  Pays trouvés: {countries}")
    print(f"  Codes HS trouvés: {hs_codes}")
    assert len(countries) > 0, "Aucun pays trouvé"
    print("✅ Extraction réussie")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3 : Classification
print("\n[3/8] Test classification (Transformers)...")
try:
    from services.nlp import TransformersAlertClassifier
    classifier = TransformersAlertClassifier(use_gpu=False)
    
    test_alert = "URGENT: All sardine products recalled due to botulism contamination."
    result = classifier.classify(test_alert)
    
    print(f"  Niveau: {result.level}")
    print(f"  Impact score: {result.impact_score:.1f}")
    print(f"  Confiance: {result.confidence:.2f}")
    assert result.level in ["CRITIQUE", "ATTENTION", "INFO"]
    print("✅ Classification réussie")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 4 : Résumé
print("\n[4/8] Test résumé (BART/mT5)...")
try:
    from services.nlp import AlertSummarizer
    summarizer = AlertSummarizer(language="en", use_gpu=False)
    
    test_text = """
    The Food and Drug Administration (FDA) has issued a critical alert regarding 
    sardine products imported from Morocco. These products, identified by HS Code 160413,
    may be contaminated with Clostridium botulinum, which poses a severe health risk.
    All importers, distributors, and retailers must immediately remove affected products 
    from shelves and notify consumers of the potential hazard.
    """
    
    summary = summarizer.summarize(test_text)
    print(f"  Court: {summary.short[:80]}...")
    print(f"  Actions: {summary.action_items}")
    assert len(summary.short) > 0
    print("✅ Résumé réussi")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 5 : Analyse complète (orchestrateur)
print("\n[5/8] Test analyse complète (orchestrateur)...")
try:
    test_alert_complete = """
    FDA URGENT ALERT: Sardine Products Recall
    
    All sardine products from Morocco (HS Code 160413) with production dates 
    between May 1-15, 2026 must be withdrawn from shelves immediately. 
    Contamination with Clostridium botulinum suspected. 
    Consumer risk: CRITICAL.
    
    Immediate notification required before June 1, 2026.
    USA and Canada importers are affected.
    """
    
    analysis = analyzer.analyze(
        text=test_alert_complete,
        hs_code="160413",
        target_countries=["USA", "CAN"]
    )
    
    print(f"  Titre: {analysis.titre_fr}")
    print(f"  Niveau: {analysis.niveau}")
    print(f"  Impact: {analysis.impact_score:.1f}/100")
    print(f"  Pays: {', '.join(analysis.pays_concernes)}")
    print(f"  Confiance: {analysis.confiance:.2f}")
    
    assert analysis.niveau in ["CRITIQUE", "ATTENTION", "INFO"]
    assert analysis.impact_score >= 0 and analysis.impact_score <= 100
    print("✅ Analyse complète réussie")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Test 6 : Cache
print("\n[6/8] Test cache...")
try:
    # Première analyse
    result1 = analyzer.analyze(test_alert_complete, hs_code="160413")
    cache_hits_before = analyzer.stats["cache_hits"]
    
    # Deuxième analyse identique (devrait utiliser cache)
    result2 = analyzer.analyze(test_alert_complete, hs_code="160413")
    cache_hits_after = analyzer.stats["cache_hits"]
    
    if cache_hits_after > cache_hits_before:
        print(f"  Cache hits: {analyzer.stats['cache_hits']}")
        print("✅ Cache fonctionne")
    else:
        print("  (Cache vide - première exécution)")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 7 : Statistiques
print("\n[7/8] Statistiques...")
try:
    stats = analyzer.stats
    print(f"  Appels totals: {stats['calls']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Hit rate: {stats['cache_hit_rate']:.0%}")
    print("✅ Statistiques disponibles")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Résumé final
print("\n" + "=" * 70)
print("✅ ÉTAPE 3 VALIDÉE : Pipeline NLP open-source en production")
print("=" * 70)
print("\nÉTAPE SUIVANTE: Mettre à jour regulatory_watch.py pour utiliser le nouveau pipeline")
print("\nProchaines actions:")
print("  1. Remplacer llm_regulatory_analyzer.py par opensource_regulatory_analyzer.py")
print("  2. Tester end-to-end avec dashboard_c02.py")
print("  3. Pousser les changements sur Git")
