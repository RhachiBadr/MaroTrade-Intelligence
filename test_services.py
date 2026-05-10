#!/usr/bin/env python3
"""Test script pour valider les imports des services."""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_service_imports():
    """Test des imports de base des services."""
    print("Testing services...")

    try:
        import services.scoring
        print("✓ Scoring service module imported successfully")
    except Exception as e:
        print(f"✗ Scoring service failed: {e}")

    try:
        import services.watch
        print("✓ Watch service module imported successfully")
    except Exception as e:
        print(f"✗ Watch service failed: {e}")

    try:
        import services.nlp
        print("✓ NLP service module imported successfully")
    except Exception as e:
        print(f"✗ NLP service failed: {e}")

    print("Test completed.")

if __name__ == "__main__":
    test_service_imports()