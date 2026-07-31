"""
Modèle Projet – CRUD complet avec associations many-to-many (étudiants, jury).
"""

from database.db_connection import execute_query, db_context


class Projet:
    """Représente un projet académique (PFE, PFA, Recherche…)."""

    TYPES = ["PFE", "PFA", "Académique", "Recherche"]
    STATUTS = ["En cours", "Terminé", "Suspendu"]
    MENTIONS = ["", "Passable", "Assez Bien", "Bien", "Très Bien", "Excellent"]

    def __init__(self, id=None, titre="", description="", type_projet="PFA",
                 semestre_id=None, annee_id=None, date_debut="", date_fin="",
                 statut="En cours", note=None, mention=""):
        self.id = id
        self.titre = titre
        self.description = description
        self.type_projet = type_projet
        self.semestre_id = semestre_id
        self.annee_id = annee_id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.statut = statut
        self.note = note
        self.mention = mention

    def __repr__(self):
        return f"<Projet #{self.id} – {self.titre}>"

    # ─── CREATE ───────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, titre, description="", type_projet="PFA", semestre_id=None,
               annee_id=None, date_debut="", date_fin="", statut="En cours"):
        query = """
            INSERT INTO projets (titre, description, type_projet, semestre_id, annee_id,
                date_debut, date_fin, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (titre, description, type_projet, semestre_id,
                                     annee_id, date_debut, date_fin, statut))

    # ─── READ ─────────────────────────────────────────────────────────────────

    @classmethod
    def get_all(cls):
        query = """
            SELECT p.*, au.libelle as annee_libelle,
                   s.numero as semestre_numero
            FROM projets p
            LEFT JOIN annees_universitaires au ON p.annee_id = au.id
            LEFT JOIN semestres s ON p.semestre_id = s.id
            ORDER BY p.date_debut DESC
        """
        return execute_query(query, fetchall=True)

    @classmethod
    def get_by_id(cls, projet_id):
        query = """
            SELECT p.*, au.libelle as annee_libelle, s.numero as semestre_numero
            FROM projets p
            LEFT JOIN annees_universitaires au ON p.annee_id = au.id
            LEFT JOIN semestres s ON p.semestre_id = s.id
            WHERE p.id = ?
        """
        return execute_query(query, (projet_id,), fetchone=True)

    @classmethod
    def get_etudiants(cls, projet_id):
        """Retourne les étudiants membres du projet."""
        query = """
            SELECT e.*, pe.role
            FROM etudiants e
            JOIN projet_etudiants pe ON e.id = pe.etudiant_id
            WHERE pe.projet_id = ?
        """
        return execute_query(query, (projet_id,), fetchall=True)

    @classmethod
    def get_jury(cls, projet_id):
        """Retourne les membres du jury du projet."""
        query = """
            SELECT p.*, pj.role as jury_role
            FROM professeurs p
            JOIN projet_jury pj ON p.id = pj.professeur_id
            WHERE pj.projet_id = ?
        """
        return execute_query(query, (projet_id,), fetchall=True)

    @classmethod
    def search(cls, terme="", type_projet="", statut="", annee_id=None):
        query = """
            SELECT p.*, au.libelle as annee_libelle, s.numero as semestre_numero
            FROM projets p
            LEFT JOIN annees_universitaires au ON p.annee_id = au.id
            LEFT JOIN semestres s ON p.semestre_id = s.id
            WHERE (p.titre LIKE ? OR p.description LIKE ?)
              AND (p.type_projet LIKE ? OR ? = '')
              AND (p.statut LIKE ? OR ? = '')
              AND (p.annee_id = ? OR ? IS NULL)
            ORDER BY p.date_debut DESC
        """
        t = f"%{terme}%"
        tp = f"%{type_projet}%" if type_projet else ""
        st = f"%{statut}%" if statut else ""
        return execute_query(query, (t, t, tp, type_projet, st, statut,
                                     annee_id, annee_id), fetchall=True)

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    @classmethod
    def update(cls, projet_id, **kwargs):
        allowed = {"titre", "description", "type_projet", "semestre_id", "annee_id",
                   "date_debut", "date_fin", "statut", "note", "mention"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [projet_id]
        return execute_query(f"UPDATE projets SET {set_clause} WHERE id=?", tuple(values))

    # ─── DELETE ───────────────────────────────────────────────────────────────

    @classmethod
    def delete(cls, projet_id):
        return execute_query("DELETE FROM projets WHERE id=?", (projet_id,))

    # ─── ASSOCIATIONS ─────────────────────────────────────────────────────────

    @classmethod
    def add_etudiant(cls, projet_id, etudiant_id, role="Membre"):
        """Ajoute un étudiant au projet."""
        query = "INSERT OR IGNORE INTO projet_etudiants (projet_id, etudiant_id, role) VALUES (?, ?, ?)"
        return execute_query(query, (projet_id, etudiant_id, role))

    @classmethod
    def remove_etudiant(cls, projet_id, etudiant_id):
        return execute_query(
            "DELETE FROM projet_etudiants WHERE projet_id=? AND etudiant_id=?",
            (projet_id, etudiant_id)
        )

    @classmethod
    def set_etudiants(cls, projet_id, etudiants):
        """Remplace la liste des étudiants du projet. etudiants = [(etudiant_id, role), ...]"""
        with db_context() as conn:
            conn.execute("DELETE FROM projet_etudiants WHERE projet_id=?", (projet_id,))
            conn.executemany(
                "INSERT INTO projet_etudiants (projet_id, etudiant_id, role) VALUES (?, ?, ?)",
                [(projet_id, eid, role) for eid, role in etudiants]
            )

    @classmethod
    def add_jury(cls, projet_id, professeur_id, role="Membre"):
        """Ajoute un professeur au jury du projet."""
        query = "INSERT OR IGNORE INTO projet_jury (projet_id, professeur_id, role) VALUES (?, ?, ?)"
        return execute_query(query, (projet_id, professeur_id, role))

    @classmethod
    def remove_jury(cls, projet_id, professeur_id):
        return execute_query(
            "DELETE FROM projet_jury WHERE projet_id=? AND professeur_id=?",
            (projet_id, professeur_id)
        )

    @classmethod
    def set_jury(cls, projet_id, jury):
        """Remplace le jury du projet. jury = [(professeur_id, role), ...]"""
        with db_context() as conn:
            conn.execute("DELETE FROM projet_jury WHERE projet_id=?", (projet_id,))
            conn.executemany(
                "INSERT INTO projet_jury (projet_id, professeur_id, role) VALUES (?, ?, ?)",
                [(projet_id, pid, role) for pid, role in jury]
            )

    # ─── STATS ────────────────────────────────────────────────────────────────

    @classmethod
    def count(cls):
        result = execute_query("SELECT COUNT(*) as total FROM projets", fetchone=True)
        return result["total"] if result else 0

    @classmethod
    def count_by_statut(cls):
        return execute_query(
            "SELECT statut, COUNT(*) as total FROM projets GROUP BY statut",
            fetchall=True
        )

    @classmethod
    def moyenne_notes(cls):
        result = execute_query(
            "SELECT AVG(note) as moyenne FROM projets WHERE note IS NOT NULL",
            fetchone=True
        )
        return round(result["moyenne"], 2) if result and result["moyenne"] else 0.0
