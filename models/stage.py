"""
Modèle Stage – CRUD complet sur la table `stages`.
"""

from database.db_connection import execute_query


class Stage:
    """Représente un stage étudiant en entreprise."""

    STATUTS = ["En cours", "Terminé", "Abandonné"]
    MENTIONS = ["", "Passable", "Assez Bien", "Bien", "Très Bien", "Excellent"]

    def __init__(self, id=None, titre="", description="", etudiant_id=None,
                 entreprise_id=None, professeur_encadrant_id=None, annee_id=None,
                 semestre_id=None, date_debut="", date_fin="", duree_semaines=None,
                 statut="En cours", note=None, mention="", rapport_path=None):
        self.id = id
        self.titre = titre
        self.description = description
        self.etudiant_id = etudiant_id
        self.entreprise_id = entreprise_id
        self.professeur_encadrant_id = professeur_encadrant_id
        self.annee_id = annee_id
        self.semestre_id = semestre_id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.duree_semaines = duree_semaines
        self.statut = statut
        self.note = note
        self.mention = mention
        self.rapport_path = rapport_path

    # ─── CREATE ───────────────────────────────────────────────────────────────

    @classmethod
    def create(cls, titre, etudiant_id, annee_id, date_debut, date_fin,
               description="", entreprise_id=None, professeur_encadrant_id=None,
               semestre_id=None, duree_semaines=None, statut="En cours"):
        query = """
            INSERT INTO stages (titre, description, etudiant_id, entreprise_id,
                professeur_encadrant_id, annee_id, semestre_id, date_debut,
                date_fin, duree_semaines, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return execute_query(query, (titre, description, etudiant_id, entreprise_id,
                                     professeur_encadrant_id, annee_id, semestre_id,
                                     date_debut, date_fin, duree_semaines, statut))

    # ─── READ ─────────────────────────────────────────────────────────────────

    @classmethod
    def get_all(cls):
        query = """
            SELECT s.*,
                   et.nom || ' ' || et.prenom as etudiant_nom,
                   et.matricule as etudiant_matricule,
                   en.nom as entreprise_nom,
                   p.nom || ' ' || p.prenom as encadrant_nom,
                   au.libelle as annee_libelle,
                   sem.numero as semestre_numero
            FROM stages s
            LEFT JOIN etudiants et ON s.etudiant_id = et.id
            LEFT JOIN entreprises en ON s.entreprise_id = en.id
            LEFT JOIN professeurs p ON s.professeur_encadrant_id = p.id
            LEFT JOIN annees_universitaires au ON s.annee_id = au.id
            LEFT JOIN semestres sem ON s.semestre_id = sem.id
            ORDER BY s.date_debut DESC
        """
        return execute_query(query, fetchall=True)

    @classmethod
    def get_by_id(cls, stage_id):
        query = """
            SELECT s.*,
                   et.nom || ' ' || et.prenom as etudiant_nom,
                   et.matricule as etudiant_matricule,
                   en.nom as entreprise_nom, en.secteur as entreprise_secteur,
                   en.adresse as entreprise_adresse, en.telephone as entreprise_tel,
                   p.nom || ' ' || p.prenom as encadrant_nom,
                   au.libelle as annee_libelle,
                   sem.numero as semestre_numero
            FROM stages s
            LEFT JOIN etudiants et ON s.etudiant_id = et.id
            LEFT JOIN entreprises en ON s.entreprise_id = en.id
            LEFT JOIN professeurs p ON s.professeur_encadrant_id = p.id
            LEFT JOIN annees_universitaires au ON s.annee_id = au.id
            LEFT JOIN semestres sem ON s.semestre_id = sem.id
            WHERE s.id = ?
        """
        return execute_query(query, (stage_id,), fetchone=True)

    @classmethod
    def search(cls, terme="", statut="", annee_id=None, etudiant_id=None):
        query = """
            SELECT s.*,
                   et.nom || ' ' || et.prenom as etudiant_nom,
                   en.nom as entreprise_nom,
                   p.nom || ' ' || p.prenom as encadrant_nom,
                   au.libelle as annee_libelle
            FROM stages s
            LEFT JOIN etudiants et ON s.etudiant_id = et.id
            LEFT JOIN entreprises en ON s.entreprise_id = en.id
            LEFT JOIN professeurs p ON s.professeur_encadrant_id = p.id
            LEFT JOIN annees_universitaires au ON s.annee_id = au.id
            WHERE (s.titre LIKE ? OR et.nom LIKE ? OR et.prenom LIKE ? OR en.nom LIKE ?)
              AND (s.statut LIKE ? OR ? = '')
              AND (s.annee_id = ? OR ? IS NULL)
              AND (s.etudiant_id = ? OR ? IS NULL)
            ORDER BY s.date_debut DESC
        """
        t = f"%{terme}%"
        st = f"%{statut}%" if statut else ""
        return execute_query(query, (t, t, t, t, st, statut,
                                     annee_id, annee_id,
                                     etudiant_id, etudiant_id), fetchall=True)

    # ─── UPDATE ───────────────────────────────────────────────────────────────

    @classmethod
    def update(cls, stage_id, **kwargs):
        allowed = {"titre", "description", "etudiant_id", "entreprise_id",
                   "professeur_encadrant_id", "annee_id", "semestre_id",
                   "date_debut", "date_fin", "duree_semaines", "statut",
                   "note", "mention", "rapport_path"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return 0
        set_clause = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [stage_id]
        return execute_query(f"UPDATE stages SET {set_clause} WHERE id=?", tuple(values))

    # ─── DELETE ───────────────────────────────────────────────────────────────

    @classmethod
    def delete(cls, stage_id):
        return execute_query("DELETE FROM stages WHERE id=?", (stage_id,))

    # ─── STATS ────────────────────────────────────────────────────────────────

    @classmethod
    def count(cls):
        result = execute_query("SELECT COUNT(*) as total FROM stages", fetchone=True)
        return result["total"] if result else 0

    @classmethod
    def count_by_statut(cls):
        return execute_query(
            "SELECT statut, COUNT(*) as total FROM stages GROUP BY statut",
            fetchall=True
        )

    @classmethod
    def moyenne_notes(cls):
        result = execute_query(
            "SELECT AVG(note) as moyenne FROM stages WHERE note IS NOT NULL",
            fetchone=True
        )
        return round(result["moyenne"], 2) if result and result["moyenne"] else 0.0
