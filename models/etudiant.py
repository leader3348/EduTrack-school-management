"""
Modèle Étudiant – CRUD complet sur la table `etudiants`.
"""

from database.db_connection import execute_query, DatabaseError
from datetime import date


class Etudiant:
    """Représente un étudiant avec toutes ses opérations CRUD."""

    def __init__(self, id=None, matricule="", nom="", prenom="", email="",
                 telephone="", date_naissance="", filiere="", niveau="",
                 date_inscription="", photo_path=None, actif=1):
        self.id = id
        self.matricule = matricule
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.date_naissance = date_naissance
        self.filiere = filiere
        self.niveau = niveau
        self.date_inscription = date_inscription or str(date.today())
        self.photo_path = photo_path
        self.actif = actif

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f"<Etudiant {self.matricule} – {self.nom_complet}>"

    # ─── CREATE ───────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, matricule, nom, prenom, email="", telephone="",
               date_naissance="", filiere="", niveau="", date_inscription=None):
        """Crée un nouvel étudiant et retourne son id."""
        date_inscription = date_inscription or str(date.today())
        query = """
            INSERT INTO etudiants (matricule, nom, prenom, email, telephone,
                date_naissance, filiere, niveau, date_inscription)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (matricule, nom, prenom, email, telephone,
                                     date_naissance, filiere, niveau, date_inscription))

    # ─── READ ─────────────────────────────────────────────────────────────────

    @classmethod
    def get_all(cls, actif_only=True):
        """Retourne la liste de tous les étudiants."""
        if actif_only:
            return execute_query("SELECT * FROM etudiants WHERE actif=1 ORDER BY nom, prenom",
                                 fetchall=True)
        return execute_query("SELECT * FROM etudiants ORDER BY nom, prenom", fetchall=True)

    @classmethod
    def get_by_id(cls, etudiant_id):
        """Retourne un étudiant par son id."""
        return execute_query("SELECT * FROM etudiants WHERE id=?",
                             (etudiant_id,), fetchone=True)

    @classmethod
    def get_by_matricule(cls, matricule):
        """Retourne un étudiant par son matricule."""
        return execute_query("SELECT * FROM etudiants WHERE matricule=?",
                             (matricule,), fetchone=True)

    @classmethod
    def search(cls, terme="", filiere="", niveau=""):
        """Recherche multicritères sur les étudiants."""
        query = """
            SELECT * FROM etudiants
            WHERE actif=1
              AND (nom LIKE ? OR prenom LIKE ? OR matricule LIKE ? OR email LIKE ?)
              AND (filiere LIKE ? OR ? = '')
              AND (niveau LIKE ? OR ? = '')
            ORDER BY nom, prenom
        """
        t = f"%{terme}%"
        f_val = f"%{filiere}%" if filiere else ""
        n_val = f"%{niveau}%" if niveau else ""
        return execute_query(query, (t, t, t, t, f_val, filiere, n_val, niveau), fetchall=True)

    @classmethod
    def get_projets(cls, etudiant_id):
        """Retourne tous les projets d'un étudiant."""
        query = """
            SELECT p.*, pe.role, au.libelle as annee_libelle
            FROM projets p
            JOIN projet_etudiants pe ON p.id = pe.projet_id
            JOIN annees_universitaires au ON p.annee_id = au.id
            WHERE pe.etudiant_id = ?
            ORDER BY p.date_debut DESC
        """
        return execute_query(query, (etudiant_id,), fetchall=True)

    @classmethod
    def get_stages(cls, etudiant_id):
        """Retourne tous les stages d'un étudiant."""
        query = """
            SELECT s.*, e.nom as entreprise_nom, au.libelle as annee_libelle,
                   p.nom || ' ' || p.prenom as encadrant_nom
            FROM stages s
            LEFT JOIN entreprises e ON s.entreprise_id = e.id
            LEFT JOIN annees_universitaires au ON s.annee_id = au.id
            LEFT JOIN professeurs p ON s.professeur_encadrant_id = p.id
            WHERE s.etudiant_id = ?
            ORDER BY s.date_debut DESC
        """
        return execute_query(query, (etudiant_id,), fetchall=True)

    @classmethod
    def get_notes(cls, etudiant_id):
        """Retourne toutes les notes d'un étudiant."""
        query = """
            SELECT n.*, s.numero as semestre_numero
            FROM notes n
            LEFT JOIN semestres s ON n.semestre_id = s.id
            WHERE n.etudiant_id = ?
            ORDER BY n.date_evaluation DESC
        """
        return execute_query(query, (etudiant_id,), fetchall=True)

    @classmethod
    def get_moyenne(cls, etudiant_id):
        """Calcule la moyenne générale pondérée d'un étudiant."""
        query = """
            SELECT SUM(note * coefficient) / SUM(coefficient) as moyenne
            FROM notes
            WHERE etudiant_id = ?
        """
        result = execute_query(query, (etudiant_id,), fetchone=True)
        return result["moyenne"] if result and result["moyenne"] else 0.0

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    @classmethod
    def update(cls, etudiant_id, **kwargs):
        """Met à jour les champs spécifiés d'un étudiant."""
        allowed = {"matricule", "nom", "prenom", "email", "telephone",
                   "date_naissance", "filiere", "niveau", "photo_path", "actif"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [etudiant_id]
        query = f"UPDATE etudiants SET {set_clause} WHERE id=?"
        return execute_query(query, tuple(values))

    # ─── DELETE ───────────────────────────────────────────────────────────────

    @classmethod
    def delete(cls, etudiant_id):
        """Supprime logiquement un étudiant (actif=0)."""
        return execute_query("UPDATE etudiants SET actif=0 WHERE id=?", (etudiant_id,))

    @classmethod
    def hard_delete(cls, etudiant_id):
        """Supprime définitivement un étudiant."""
        return execute_query("DELETE FROM etudiants WHERE id=?", (etudiant_id,))

    # ─── STATISTIQUES ─────────────────────────────────────────────────────────

    @classmethod
    def count(cls):
        """Retourne le nombre total d'étudiants actifs."""
        result = execute_query("SELECT COUNT(*) as total FROM etudiants WHERE actif=1", fetchone=True)
        return result["total"] if result else 0

    @classmethod
    def count_by_niveau(cls):
        """Retourne la répartition des étudiants par niveau."""
        return execute_query(
            "SELECT niveau, COUNT(*) as total FROM etudiants WHERE actif=1 GROUP BY niveau",
            fetchall=True
        )

    @classmethod
    def count_by_filiere(cls):
        """Retourne la répartition des étudiants par filière."""
        return execute_query(
            "SELECT filiere, COUNT(*) as total FROM etudiants WHERE actif=1 GROUP BY filiere",
            fetchall=True
        )
