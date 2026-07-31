"""
Controllers Projet, Stage, Professeur, Entreprise, Statistiques.
"""

from models import Projet, Stage, Professeur, Entreprise, AnneeUniversitaire, Semestre, Note, Etudiant
from database.db_connection import DatabaseError


# ══════════════════════════════════════════════════════════════════════════════
#  PROJET CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class ProjetController:
    """Gère toutes les opérations métier liées aux projets."""

    @staticmethod
    def ajouter(titre, annee_id, description="", type_projet="PFA",
                semestre_id=None, date_debut="", date_fin="", statut="En cours"):
        if not titre.strip():
            raise ValueError("Le titre du projet est obligatoire.")
        if not annee_id:
            raise ValueError("L'année universitaire est obligatoire.")
        return Projet.create(titre.strip(), description, type_projet,
                             semestre_id, annee_id, date_debut, date_fin, statut)

    @staticmethod
    def modifier(projet_id, **kwargs):
        if not Projet.get_by_id(projet_id):
            raise ValueError("Projet introuvable.")
        return Projet.update(projet_id, **kwargs)

    @staticmethod
    def supprimer(projet_id):
        if not Projet.get_by_id(projet_id):
            raise ValueError("Projet introuvable.")
        return Projet.delete(projet_id)

    @staticmethod
    def get_liste():
        return Projet.get_all()

    @staticmethod
    def get_detail(projet_id):
        projet = Projet.get_by_id(projet_id)
        if not projet:
            raise ValueError("Projet introuvable.")
        etudiants = Projet.get_etudiants(projet_id)
        jury = Projet.get_jury(projet_id)
        return {"projet": projet, "etudiants": etudiants, "jury": jury}

    @staticmethod
    def associer_etudiants(projet_id, etudiants):
        """etudiants = [(etudiant_id, role), ...]"""
        Projet.set_etudiants(projet_id, etudiants)

    @staticmethod
    def associer_jury(projet_id, jury):
        """jury = [(professeur_id, role), ...]"""
        Projet.set_jury(projet_id, jury)

    @staticmethod
    def noter(projet_id, note, mention=""):
        if not (0 <= float(note) <= 20):
            raise ValueError("La note doit être entre 0 et 20.")
        return Projet.update(projet_id, note=float(note), mention=mention,
                             statut="Terminé")

    @staticmethod
    def rechercher(terme="", type_projet="", statut="", annee_id=None):
        return Projet.search(terme, type_projet, statut, annee_id)

    @staticmethod
    def get_statistiques():
        return {
            "total": Projet.count(),
            "par_statut": Projet.count_by_statut(),
            "moyenne_notes": Projet.moyenne_notes(),
        }


# ══════════════════════════════════════════════════════════════════════════════
#  STAGE CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class StageController:
    """Gère toutes les opérations métier liées aux stages."""

    @staticmethod
    def ajouter(titre, etudiant_id, annee_id, date_debut, date_fin,
                description="", entreprise_id=None, professeur_encadrant_id=None,
                semestre_id=None, duree_semaines=None):
        if not titre.strip():
            raise ValueError("Le titre du stage est obligatoire.")
        if not etudiant_id:
            raise ValueError("L'étudiant est obligatoire.")
        if not annee_id:
            raise ValueError("L'année universitaire est obligatoire.")
        if not date_debut or not date_fin:
            raise ValueError("Les dates de début et fin sont obligatoires.")
        return Stage.create(titre.strip(), etudiant_id, annee_id, date_debut, date_fin,
                            description, entreprise_id, professeur_encadrant_id,
                            semestre_id, duree_semaines)

    @staticmethod
    def modifier(stage_id, **kwargs):
        if not Stage.get_by_id(stage_id):
            raise ValueError("Stage introuvable.")
        return Stage.update(stage_id, **kwargs)

    @staticmethod
    def supprimer(stage_id):
        if not Stage.get_by_id(stage_id):
            raise ValueError("Stage introuvable.")
        return Stage.delete(stage_id)

    @staticmethod
    def get_liste():
        return Stage.get_all()

    @staticmethod
    def get_detail(stage_id):
        stage = Stage.get_by_id(stage_id)
        if not stage:
            raise ValueError("Stage introuvable.")
        return stage

    @staticmethod
    def noter(stage_id, note, mention=""):
        if not (0 <= float(note) <= 20):
            raise ValueError("La note doit être entre 0 et 20.")
        return Stage.update(stage_id, note=float(note), mention=mention, statut="Terminé")

    @staticmethod
    def rechercher(terme="", statut="", annee_id=None, etudiant_id=None):
        return Stage.search(terme, statut, annee_id, etudiant_id)

    @staticmethod
    def get_statistiques():
        return {
            "total": Stage.count(),
            "par_statut": Stage.count_by_statut(),
            "moyenne_notes": Stage.moyenne_notes(),
        }


# ══════════════════════════════════════════════════════════════════════════════
#  PROFESSEUR CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class ProfesseurController:
    """Gère les professeurs."""

    @staticmethod
    def ajouter(matricule, nom, prenom, email="", telephone="",
                specialite="", grade="Assistant"):
        if not matricule.strip() or not nom.strip() or not prenom.strip():
            raise ValueError("Matricule, nom et prénom sont obligatoires.")
        existing = Professeur.get_all()
        for p in existing:
            if p["matricule"] == matricule:
                raise ValueError(f"Matricule '{matricule}' déjà utilisé.")
        return Professeur.create(matricule, nom, prenom, email, telephone, specialite, grade)

    @staticmethod
    def modifier(prof_id, **kwargs):
        return Professeur.update(prof_id, **kwargs)

    @staticmethod
    def supprimer(prof_id):
        return Professeur.delete(prof_id)

    @staticmethod
    def get_liste():
        return Professeur.get_all()

    @staticmethod
    def rechercher(terme="", grade=""):
        return Professeur.search(terme, grade)

    @staticmethod
    def get_detail(prof_id):
        prof = Professeur.get_by_id(prof_id)
        if not prof:
            raise ValueError("Professeur introuvable.")
        projets = Professeur.get_projets(prof_id)
        stages = Professeur.get_stages_encadres(prof_id)
        return {"professeur": prof, "projets": projets, "stages": stages}

    @staticmethod
    def get_grades():
        return ["Assistant", "MCB", "MCA", "Professeur"]


# ══════════════════════════════════════════════════════════════════════════════
#  ENTREPRISE CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class EntrepriseController:
    """Gère les entreprises."""

    @staticmethod
    def ajouter(nom, secteur="", adresse="", telephone="", email="",
                site_web="", contact_nom="", contact_email=""):
        if not nom.strip():
            raise ValueError("Le nom de l'entreprise est obligatoire.")
        return Entreprise.create(nom, secteur, adresse, telephone, email,
                                 site_web, contact_nom, contact_email)

    @staticmethod
    def modifier(entreprise_id, **kwargs):
        return Entreprise.update(entreprise_id, **kwargs)

    @staticmethod
    def supprimer(entreprise_id):
        return Entreprise.delete(entreprise_id)

    @staticmethod
    def get_liste():
        return Entreprise.get_all()

    @staticmethod
    def rechercher(terme=""):
        return Entreprise.search(terme)


# ══════════════════════════════════════════════════════════════════════════════
#  ANNEE / SEMESTRE CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class AnneeController:
    """Gère les années universitaires et les semestres."""

    @staticmethod
    def get_annees():
        return AnneeUniversitaire.get_all()

    @staticmethod
    def get_annee_active():
        return AnneeUniversitaire.get_active()

    @staticmethod
    def ajouter_annee(libelle, date_debut, date_fin):
        return AnneeUniversitaire.create(libelle, date_debut, date_fin)

    @staticmethod
    def get_semestres(annee_id):
        return Semestre.get_by_annee(annee_id)

    @staticmethod
    def get_semestres_all():
        return Semestre.get_all()


# ══════════════════════════════════════════════════════════════════════════════
#  RECHERCHE AVANCÉE
# ══════════════════════════════════════════════════════════════════════════════

class RechercheController:
    """Recherche avancée multi-entités."""

    @staticmethod
    def recherche_globale(terme):
        """Recherche simultanée dans étudiants, projets, stages."""
        return {
            "etudiants": Etudiant.search(terme),
            "projets": Projet.search(terme),
            "stages": Stage.search(terme),
            "professeurs": Professeur.search(terme),
        }

    @staticmethod
    def recherche_avancee(terme="", type_entite="Tout", annee_id=None,
                          filiere="", niveau="", statut=""):
        """Recherche avancée avec filtres."""
        results = {}
        if type_entite in ("Tout", "Étudiants"):
            results["etudiants"] = Etudiant.search(terme, filiere, niveau)
        if type_entite in ("Tout", "Projets"):
            results["projets"] = Projet.search(terme, statut=statut, annee_id=annee_id)
        if type_entite in ("Tout", "Stages"):
            results["stages"] = Stage.search(terme, statut=statut, annee_id=annee_id)
        if type_entite in ("Tout", "Professeurs"):
            results["professeurs"] = Professeur.search(terme)
        return results


# ══════════════════════════════════════════════════════════════════════════════
#  STATISTIQUES GLOBALES
# ══════════════════════════════════════════════════════════════════════════════

class StatistiquesController:
    """Calcule et retourne les statistiques globales de l'application."""

    @staticmethod
    def get_dashboard():
        """Retourne toutes les données du tableau de bord."""
        from database.db_connection import execute_query

        total_etudiants = Etudiant.count()
        total_projets = Projet.count()
        total_stages = Stage.count()
        total_professeurs = Professeur.count()
        total_entreprises = Entreprise.count()

        moyenne_generale = Note.get_moyenne_generale()

        par_niveau = Etudiant.count_by_niveau()
        par_filiere = Etudiant.count_by_filiere()
        projets_par_statut = Projet.count_by_statut()
        stages_par_statut = Stage.count_by_statut()

        moy_projets = Projet.moyenne_notes()
        moy_stages = Stage.moyenne_notes()

        return {
            "total_etudiants": total_etudiants,
            "total_projets": total_projets,
            "total_stages": total_stages,
            "total_professeurs": total_professeurs,
            "total_entreprises": total_entreprises,
            "moyenne_generale": moyenne_generale,
            "par_niveau": par_niveau,
            "par_filiere": par_filiere,
            "projets_par_statut": projets_par_statut,
            "stages_par_statut": stages_par_statut,
            "moy_projets": moy_projets,
            "moy_stages": moy_stages,
        }
