"""
Modèles AnneeUniversitaire et Semestre – CRUD complet.
"""

from database.db_connection import execute_query


class AnneeUniversitaire:
    """Représente une année universitaire (ex: 2024-2025)."""

    @classmethod
    def create(cls, libelle, date_debut, date_fin, est_active=0):
        query = """
            INSERT INTO annees_universitaires (libelle, date_debut, date_fin, est_active)
            VALUES (?, ?, ?, ?)
        """
        return execute_query(query, (libelle, date_debut, date_fin, est_active))

    @classmethod
    def get_all(cls):
        return execute_query(
            "SELECT * FROM annees_universitaires ORDER BY date_debut DESC",
            fetchall=True
        )

    @classmethod
    def get_active(cls):
        return execute_query(
            "SELECT * FROM annees_universitaires WHERE est_active=1",
            fetchone=True
        )

    @classmethod
    def get_by_id(cls, annee_id):
        return execute_query(
            "SELECT * FROM annees_universitaires WHERE id=?",
            (annee_id,), fetchone=True
        )

    @classmethod
    def set_active(cls, annee_id):
        """Définit une année comme active (désactive les autres)."""
        execute_query("UPDATE annees_universitaires SET est_active=0")
        execute_query("UPDATE annees_universitaires SET est_active=1 WHERE id=?", (annee_id,))

    @classmethod
    def update(cls, annee_id, **kwargs):
        allowed = {"libelle", "date_debut", "date_fin", "est_active"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [annee_id]
        return execute_query(f"UPDATE annees_universitaires SET {set_clause} WHERE id=?", tuple(values))

    @classmethod
    def delete(cls, annee_id):
        return execute_query("DELETE FROM annees_universitaires WHERE id=?", (annee_id,))


class Semestre:
    """Représente un semestre (S1 ou S2) d'une année universitaire."""

    @classmethod
    def create(cls, numero, annee_id, date_debut, date_fin):
        query = """
            INSERT INTO semestres (numero, annee_id, date_debut, date_fin)
            VALUES (?, ?, ?, ?)
        """
        return execute_query(query, (numero, annee_id, date_debut, date_fin))

    @classmethod
    def get_all(cls):
        query = """
            SELECT s.*, au.libelle as annee_libelle
            FROM semestres s
            JOIN annees_universitaires au ON s.annee_id = au.id
            ORDER BY au.date_debut DESC, s.numero
        """
        return execute_query(query, fetchall=True)

    @classmethod
    def get_by_annee(cls, annee_id):
        return execute_query(
            "SELECT * FROM semestres WHERE annee_id=? ORDER BY numero",
            (annee_id,), fetchall=True
        )

    @classmethod
    def get_by_id(cls, semestre_id):
        return execute_query("SELECT * FROM semestres WHERE id=?", (semestre_id,), fetchone=True)

    @classmethod
    def update(cls, semestre_id, **kwargs):
        allowed = {"numero", "date_debut", "date_fin"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [semestre_id]
        return execute_query(f"UPDATE semestres SET {set_clause} WHERE id=?", tuple(values))

    @classmethod
    def delete(cls, semestre_id):
        return execute_query("DELETE FROM semestres WHERE id=?", (semestre_id,))
