"""
Controller Étudiant – logique métier pour la gestion des étudiants.
"""

from models import Etudiant, Note
from database.db_connection import DatabaseError


class EtudiantController:
    """Gère toutes les opérations métier liées aux étudiants."""

    # ─── CRUD ─────────────────────────────────────────────────────────────────

    @staticmethod
    def ajouter(matricule, nom, prenom, email="", telephone="",
                date_naissance="", filiere="", niveau="", date_inscription=""):
        """Ajoute un nouvel étudiant après validation."""
        # Validation
        if not matricule.strip():
            raise ValueError("Le matricule est obligatoire.")
        if not nom.strip() or not prenom.strip():
            raise ValueError("Le nom et le prénom sont obligatoires.")
        if Etudiant.get_by_matricule(matricule):
            raise ValueError(f"Le matricule '{matricule}' existe déjà.")
        return Etudiant.create(matricule.strip(), nom.strip(), prenom.strip(),
                               email.strip(), telephone.strip(), date_naissance,
                               filiere, niveau, date_inscription)

    @staticmethod
    def modifier(etudiant_id, **kwargs):
        """Modifie les informations d'un étudiant."""
        if not Etudiant.get_by_id(etudiant_id):
            raise ValueError("Étudiant introuvable.")
        # Vérif unicité matricule si fourni
        if "matricule" in kwargs:
            existing = Etudiant.get_by_matricule(kwargs["matricule"])
            if existing and existing["id"] != etudiant_id:
                raise ValueError(f"Le matricule '{kwargs['matricule']}' est déjà utilisé.")
        return Etudiant.update(etudiant_id, **kwargs)

    @staticmethod
    def supprimer(etudiant_id):
        """Suppression logique de l'étudiant."""
        if not Etudiant.get_by_id(etudiant_id):
            raise ValueError("Étudiant introuvable.")
        return Etudiant.delete(etudiant_id)

    @staticmethod
    def get_liste(actif_only=True):
        """Retourne la liste complète des étudiants."""
        return Etudiant.get_all(actif_only)

    @staticmethod
    def get_detail(etudiant_id):
        """Retourne le détail complet d'un étudiant (fiche complète)."""
        etudiant = Etudiant.get_by_id(etudiant_id)
        if not etudiant:
            raise ValueError("Étudiant introuvable.")
        projets = Etudiant.get_projets(etudiant_id)
        stages = Etudiant.get_stages(etudiant_id)
        notes = Etudiant.get_notes(etudiant_id)
        moyenne = Note.get_moyenne_etudiant(etudiant_id)
        return {
            "etudiant": etudiant,
            "projets": projets,
            "stages": stages,
            "notes": notes,
            "moyenne": moyenne,
        }

    # ─── RECHERCHE ────────────────────────────────────────────────────────────

    @staticmethod
    def rechercher(terme="", filiere="", niveau=""):
        """Recherche multicritères."""
        return Etudiant.search(terme, filiere, niveau)

    # ─── STATISTIQUES ─────────────────────────────────────────────────────────

    @staticmethod
    def get_statistiques():
        """Retourne les statistiques globales des étudiants."""
        return {
            "total": Etudiant.count(),
            "par_niveau": Etudiant.count_by_niveau(),
            "par_filiere": Etudiant.count_by_filiere(),
            "moyenne_generale": Note.get_moyenne_generale(),
        }

    # ─── NOTES ────────────────────────────────────────────────────────────────

    @staticmethod
    def ajouter_note(etudiant_id, type_evaluation, note_val, coefficient=1.0,
                     reference_id=None, commentaire="", semestre_id=None):
        """Ajoute une note à un étudiant."""
        if not (0 <= float(note_val) <= 20):
            raise ValueError("La note doit être comprise entre 0 et 20.")
        if not Etudiant.get_by_id(etudiant_id):
            raise ValueError("Étudiant introuvable.")
        return Note.create(etudiant_id, type_evaluation, float(note_val),
                           float(coefficient), reference_id, commentaire, semestre_id)

    @staticmethod
    def get_niveaux():
        return ["L1", "L2", "L3", "M1", "M2", "Doctorat"]

    @staticmethod
    def get_filieres():
        return ["Informatique", "Télécommunication", "Génie Logiciel",
                "Systèmes Embarqués", "Réseaux", "Intelligence Artificielle"]
