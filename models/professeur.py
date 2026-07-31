"""
Modèle Professeur – CRUD complet sur la table `professeurs`.
"""

from database.db_connection import execute_query


class Professeur:
    """Représente un professeur (directeur de projet, jury, encadrant de stage)."""

    def __init__(self, id=None, matricule="", nom="", prenom="", email="",
                 telephone="", specialite="", grade="", actif=1):
        self.id = id
        self.matricule = matricule
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.specialite = specialite
        self.grade = grade
        self.actif = actif

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def __repr__(self):
        return f"<Professeur {self.matricule} – {self.nom_complet}>"

    # ─── CREATE ───────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, matricule, nom, prenom, email="", telephone="",
               specialite="", grade="Assistant"):
        query = """
            INSERT INTO professeurs (matricule, nom, prenom, email, telephone, specialite, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (matricule, nom, prenom, email, telephone, specialite, grade))

    # ─── READ ─────────────────────────────────────────────────────────────────

    @classmethod
    def get_all(cls):
        return execute_query(
            "SELECT * FROM professeurs WHERE actif=1 ORDER BY nom, prenom",
            fetchall=True
        )

    @classmethod
    def get_by_id(cls, prof_id):
        return execute_query("SELECT * FROM professeurs WHERE id=?", (prof_id,), fetchone=True)

    @classmethod
    def search(cls, terme="", grade=""):
        query = """
            SELECT * FROM professeurs
            WHERE actif=1
              AND (nom LIKE ? OR prenom LIKE ? OR matricule LIKE ? OR specialite LIKE ?)
              AND (grade LIKE ? OR ? = '')
            ORDER BY nom, prenom
        """
        t = f"%{terme}%"
        g_val = f"%{grade}%" if grade else ""
        return execute_query(query, (t, t, t, t, g_val, grade), fetchall=True)

    @classmethod
    def get_projets(cls, prof_id):
        """Retourne tous les projets où ce professeur est jury."""
        query = """
            SELECT p.*, pj.role as jury_role, au.libelle as annee_libelle
            FROM projets p
            JOIN projet_jury pj ON p.id = pj.projet_id
            JOIN annees_universitaires au ON p.annee_id = au.id
            WHERE pj.professeur_id = ?
            ORDER BY p.date_debut DESC
        """
        return execute_query(query, (prof_id,), fetchall=True)

    @classmethod
    def get_stages_encadres(cls, prof_id):
        """Retourne tous les stages encadrés par ce professeur."""
        query = """
            SELECT s.*, e.nom as entreprise_nom,
                   et.nom || ' ' || et.prenom as etudiant_nom,
                   au.libelle as annee_libelle
            FROM stages s
            LEFT JOIN entreprises e ON s.entreprise_id = e.id
            LEFT JOIN etudiants et ON s.etudiant_id = et.id
            LEFT JOIN annees_universitaires au ON s.annee_id = au.id
            WHERE s.professeur_encadrant_id = ?
            ORDER BY s.date_debut DESC
        """
        return execute_query(query, (prof_id,), fetchall=True)

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    @classmethod
    def update(cls, prof_id, **kwargs):
        allowed = {"matricule", "nom", "prenom", "email", "telephone", "specialite", "grade", "actif"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [prof_id]
        return execute_query(f"UPDATE professeurs SET {set_clause} WHERE id=?", tuple(values))

    # ─── DELETE ───────────────────────────────────────────────────────────────

    @classmethod
    def delete(cls, prof_id):
        return execute_query("UPDATE professeurs SET actif=0 WHERE id=?", (prof_id,))

    @classmethod
    def hard_delete(cls, prof_id):
        return execute_query("DELETE FROM professeurs WHERE id=?", (prof_id,))

    # ─── STATS ────────────────────────────────────────────────────────────────

    @classmethod
    def count(cls):
        result = execute_query("SELECT COUNT(*) as total FROM professeurs WHERE actif=1", fetchone=True)
        return result["total"] if result else 0
