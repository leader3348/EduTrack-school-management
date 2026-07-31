"""Package controllers – logique métier."""
from .etudiant_controller import EtudiantController
from .controllers import (ProjetController, StageController, ProfesseurController,
                          EntrepriseController, AnneeController,
                          RechercheController, StatistiquesController)

__all__ = ["EtudiantController", "ProjetController", "StageController",
           "ProfesseurController", "EntrepriseController", "AnneeController",
           "RechercheController", "StatistiquesController"]

# Auth controller
try:
    from .auth_controller import AuthController, AuthSession, ROLES, ROLE_LABELS, ROLE_COLORS, MODULES
except Exception:
    pass
