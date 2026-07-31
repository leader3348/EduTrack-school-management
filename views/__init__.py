"""Package views – toutes les interfaces Tkinter."""
from .dashboard_view import DashboardView
from .etudiant_view import EtudiantView
from .projet_view import ProjetView
from .stage_view import StageView
from .professeur_view import ProfesseurView
from .recherche_view import RechercheView
from .statistiques_view import StatistiquesView
from .entreprise_view import EntrepriseView

__all__ = [
    "DashboardView", "EtudiantView", "ProjetView", "StageView",
    "ProfesseurView", "RechercheView", "StatistiquesView", "EntrepriseView",
]
