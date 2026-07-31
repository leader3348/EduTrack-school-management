"""
Modèles Entreprise et Note – CRUD complet.
"""

from database.db_connection import execute_query
from datetime import date


class Entreprise:
    """Représente une entreprise d'accueil de stage."""

    @classmethod
    def create(cls, nom, secteur="", adresse="", telephone="", email="",
               site_web="", contact_nom="", contact_email=""):
        query = """
            INSERT INTO entreprises (nom, secteur, adresse, telephone, email,
                site_web, contact_nom, contact_email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (nom, secteur, adresse, telephone, email,
                                     site_web, contact_nom, contact_email))

    @classmethod
    def get_all(cls):
        return execute_query("SELECT * FROM entreprises ORDER BY nom", fetchall=True)

    @classmethod
    def get_by_id(cls, entreprise_id):
        return execute_query("SELECT * FROM entreprises WHERE id=?", (entreprise_id,), fetchone=True)

    @classmethod
    def search(cls, terme=""):
        t = f"%{terme}%"
        return execute_query(
            "SELECT * FROM entreprises WHERE nom LIKE ? OR secteur LIKE ? ORDER BY nom",
            (t, t), fetchall=True
        )

    @classmethod
    def update(cls, entreprise_id, **kwargs):
        allowed = {"nom", "secteur", "adresse", "telephone", "email",
                   "site_web", "contact_nom", "contact_email"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [entreprise_id]
        return execute_query(f"UPDATE entreprises SET {set_clause} WHERE id=?", tuple(values))

    @classmethod
    def delete(cls, entreprise_id):
        return execute_query("DELETE FROM entreprises WHERE id=?", (entreprise_id,))

    @classmethod
    def count(cls):
        result = execute_query("SELECT COUNT(*) as total FROM entreprises", fetchone=True)
        return result["total"] if result else 0


class Note:
    """Représente une note d'évaluation."""

    @classmethod
    def create(cls, etudiant_id, type_evaluation, note, coefficient=1.0,
               reference_id=None, commentaire="", semestre_id=None,
               date_evaluation=None):
        date_eval = date_evaluation or str(date.today())
        query = """
            INSERT INTO notes (etudiant_id, type_evaluation, reference_id, note,
                coefficient, commentaire, date_evaluation, semestre_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (etudiant_id, type_evaluation, reference_id,
                                     note, coefficient, commentaire,
                                     date_eval, semestre_id))

    @classmethod
    def get_by_etudiant(cls, etudiant_id, semestre_id=None):
        if semestre_id:
            return execute_query(
                "SELECT * FROM notes WHERE etudiant_id=? AND semestre_id=? ORDER BY date_evaluation DESC",
                (etudiant_id, semestre_id), fetchall=True
            )
        return execute_query(
            "SELECT * FROM notes WHERE etudiant_id=? ORDER BY date_evaluation DESC",
            (etudiant_id,), fetchall=True
        )

    @classmethod
    def get_moyenne_etudiant(cls, etudiant_id):
        result = execute_query(
            "SELECT SUM(note*coefficient)/SUM(coefficient) as moy FROM notes WHERE etudiant_id=?",
            (etudiant_id,), fetchone=True
        )
        return round(result["moy"], 2) if result and result["moy"] else 0.0

    @classmethod
    def get_moyenne_generale(cls):
        result = execute_query(
            "SELECT AVG(note) as moy FROM notes",
            fetchone=True
        )
        return round(result["moy"], 2) if result and result["moy"] else 0.0

    @classmethod
    def update(cls, note_id, **kwargs):
        allowed = {"note", "coefficient", "commentaire", "semestre_id"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [note_id]
        return execute_query(f"UPDATE notes SET {set_clause} WHERE id=?", tuple(values))

    @classmethod
    def delete(cls, note_id):
        return execute_query("DELETE FROM notes WHERE id=?", (note_id,))
