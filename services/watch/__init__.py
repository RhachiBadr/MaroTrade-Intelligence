"""Module de service de veille réglementaire.

Ce package encapsule le moteur de veille et ses exports.
"""

# Import différé
def __getattr__(name):
    if name == "RegulatoryWatchEngine":
        from services.watch.regulatory_watch import RegulatoryWatchEngine
        return RegulatoryWatchEngine
    elif name == "LEVEL_CRITICAL":
        from services.watch.regulatory_watch import LEVEL_CRITICAL
        return LEVEL_CRITICAL
    elif name == "LEVEL_WARNING":
        from services.watch.regulatory_watch import LEVEL_WARNING
        return LEVEL_WARNING
    elif name == "LEVEL_INFO":
        from services.watch.regulatory_watch import LEVEL_INFO
        return LEVEL_INFO
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = ["RegulatoryWatchEngine", "LEVEL_CRITICAL", "LEVEL_WARNING", "LEVEL_INFO"]
