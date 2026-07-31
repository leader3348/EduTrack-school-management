"""
Script d'initialisation de la base de données EduTrack.
Crée toutes les tables et insère des données de démonstration.
"""

from database.db_connection import get_connection, DatabaseError


# ─────────────────────────────────────────────
# SCHÉMA SQL COMPLET
# ─────────────────────────────────────────────

SCHEMA = """
-- Table Années universitaires
CREATE TABLE IF NOT EXISTS annees_universitaires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL UNIQUE,          -- ex: "2023-2024"
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    est_active INTEGER DEFAULT 0           -- 1 = année en cours
);

-- Table Semestres
CREATE TABLE IF NOT EXISTS semestres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER NOT NULL,               -- 1 ou 2
    annee_id INTEGER NOT NULL,
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    FOREIGN KEY (annee_id) REFERENCES annees_universitaires(id) ON DELETE CASCADE,
    UNIQUE (numero, annee_id)
);

-- Table Étudiants
CREATE TABLE IF NOT EXISTS etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE,
    telephone TEXT,
    date_naissance TEXT,
    filiere TEXT,
    niveau TEXT,                           -- L1, L2, L3, M1, M2
    date_inscription TEXT NOT NULL,
    photo_path TEXT,
    actif INTEGER DEFAULT 1
);

-- Table Professeurs
CREATE TABLE IF NOT EXISTS professeurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE,
    telephone TEXT,
    specialite TEXT,
    grade TEXT,                            -- Assistant, MCA, MCB, Professeur
    actif INTEGER DEFAULT 1
);

-- Table Entreprises
CREATE TABLE IF NOT EXISTS entreprises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    secteur TEXT,
    adresse TEXT,
    telephone TEXT,
    email TEXT,
    site_web TEXT,
    contact_nom TEXT,
    contact_email TEXT
);

-- Table Projets
CREATE TABLE IF NOT EXISTS projets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    type_projet TEXT,                      -- PFE, PFA, Academique, Recherche
    semestre_id INTEGER,
    annee_id INTEGER NOT NULL,
    date_debut TEXT,
    date_fin TEXT,
    statut TEXT DEFAULT 'En cours',        -- En cours, Terminé, Suspendu
    note REAL,
    mention TEXT,                          -- Passable, AB, Bien, TB, Excellent
    FOREIGN KEY (semestre_id) REFERENCES semestres(id),
    FOREIGN KEY (annee_id) REFERENCES annees_universitaires(id)
);

-- Table de relation Projet ↔ Étudiant (many-to-many)
CREATE TABLE IF NOT EXISTS projet_etudiants (
    projet_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    role TEXT DEFAULT 'Membre',           -- Chef de projet, Membre
    PRIMARY KEY (projet_id, etudiant_id),
    FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE
);

-- Table de relation Projet ↔ Professeur (jury)
CREATE TABLE IF NOT EXISTS projet_jury (
    projet_id INTEGER NOT NULL,
    professeur_id INTEGER NOT NULL,
    role TEXT DEFAULT 'Membre',           -- Directeur, Rapporteur, Membre
    PRIMARY KEY (projet_id, professeur_id),
    FOREIGN KEY (projet_id) REFERENCES projets(id) ON DELETE CASCADE,
    FOREIGN KEY (professeur_id) REFERENCES professeurs(id) ON DELETE CASCADE
);

-- Table Stages
CREATE TABLE IF NOT EXISTS stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT,
    etudiant_id INTEGER NOT NULL,
    entreprise_id INTEGER,
    professeur_encadrant_id INTEGER,
    annee_id INTEGER NOT NULL,
    semestre_id INTEGER,
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL,
    duree_semaines INTEGER,
    statut TEXT DEFAULT 'En cours',       -- En cours, Terminé, Abandonné
    note REAL,
    mention TEXT,
    rapport_path TEXT,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (entreprise_id) REFERENCES entreprises(id),
    FOREIGN KEY (professeur_encadrant_id) REFERENCES professeurs(id),
    FOREIGN KEY (annee_id) REFERENCES annees_universitaires(id),
    FOREIGN KEY (semestre_id) REFERENCES semestres(id)
);

-- Table Notes (notes détaillées par évaluation)
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    type_evaluation TEXT NOT NULL,        -- Projet, Stage, Examen
    reference_id INTEGER,                 -- id du projet ou stage
    note REAL NOT NULL,
    coefficient REAL DEFAULT 1.0,
    commentaire TEXT,
    date_evaluation TEXT NOT NULL,
    semestre_id INTEGER,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (semestre_id) REFERENCES semestres(id)
);
"""

DEMO_DATA = """
-- Données de démonstration

-- Années universitaires
INSERT OR IGNORE INTO annees_universitaires (libelle, date_debut, date_fin, est_active) VALUES
('2022-2023', '2022-09-01', '2023-06-30', 0),
('2023-2024', '2023-09-01', '2024-06-30', 0),
('2024-2025', '2024-09-01', '2025-06-30', 1);

-- Semestres pour 2024-2025 (id=3)
INSERT OR IGNORE INTO semestres (numero, annee_id, date_debut, date_fin) VALUES
(1, 3, '2024-09-01', '2025-01-31'),
(2, 3, '2025-02-01', '2025-06-30');

-- Semestres pour 2023-2024 (id=2)
INSERT OR IGNORE INTO semestres (numero, annee_id, date_debut, date_fin) VALUES
(1, 2, '2023-09-01', '2024-01-31'),
(2, 2, '2024-02-01', '2024-06-30');

-- Professeurs
INSERT OR IGNORE INTO professeurs (matricule, nom, prenom, email, telephone, specialite, grade) VALUES
('PR001', 'Benali', 'Ahmed', 'a.benali@univ.dz', '0550001111', 'Intelligence Artificielle', 'Professeur'),
('PR002', 'Hadj', 'Fatima', 'f.hadj@univ.dz', '0550002222', 'Génie Logiciel', 'MCA'),
('PR003', 'Meziane', 'Karim', 'k.meziane@univ.dz', '0550003333', 'Réseaux et Sécurité', 'MCB'),
('PR004', 'Slimani', 'Nadia', 'n.slimani@univ.dz', '0550004444', 'Base de données', 'MCA'),
('PR005', 'Khelil', 'Youcef', 'y.khelil@univ.dz', '0550005555', 'Systèmes Embarqués', 'Assistant');

-- Étudiants
INSERT OR IGNORE INTO etudiants (matricule, nom, prenom, email, telephone, date_naissance, filiere, niveau, date_inscription) VALUES
('ET001', 'Amrani', 'Sofiane', 's.amrani@etud.dz', '0660001111', '2001-03-15', 'Informatique', 'M2', '2023-09-15'),
('ET002', 'Boudiaf', 'Lina', 'l.boudiaf@etud.dz', '0660002222', '2001-07-22', 'Informatique', 'M2', '2023-09-15'),
('ET003', 'Cherif', 'Riad', 'r.cherif@etud.dz', '0660003333', '2002-01-10', 'Télécommunication', 'M1', '2024-09-10'),
('ET004', 'Djerbi', 'Amina', 'a.djerbi@etud.dz', '0660004444', '2002-11-05', 'Informatique', 'L3', '2024-09-10'),
('ET005', 'El-Hadi', 'Omar', 'o.elhadi@etud.dz', '0660005555', '2003-06-18', 'Télécommunication', 'L3', '2024-09-10'),
('ET006', 'Ferrahi', 'Sara', 's.ferrahi@etud.dz', '0660006666', '2001-09-30', 'Génie Logiciel', 'M2', '2023-09-15'),
('ET007', 'Ghennam', 'Tarek', 't.ghennam@etud.dz', '0660007777', '2002-04-12', 'Informatique', 'M1', '2024-09-10'),
('ET008', 'Hamdi', 'Yasmine', 'y.hamdi@etud.dz', '0660008888', '2003-12-25', 'Génie Logiciel', 'L3', '2024-09-10');

-- Entreprises
INSERT OR IGNORE INTO entreprises (nom, secteur, adresse, telephone, email, contact_nom) VALUES
('Sonatrach', 'Énergie', 'Alger', '021000001', 'rh@sonatrach.dz', 'M. Touati'),
('Ooredoo Algérie', 'Télécommunication', 'Alger', '021000002', 'stage@ooredoo.dz', 'Mme. Kaci'),
('Djezzy', 'Télécommunication', 'Alger', '021000003', 'hr@djezzy.dz', 'M. Saadi'),
('CERIST', 'Recherche', 'Alger', '021000004', 'info@cerist.dz', 'Dr. Mebarki'),
('NCA Rouiba', 'Agroalimentaire', 'Rouiba', '021000005', 'rh@nca.dz', 'Mme. Aïssaoui');

-- Projets
INSERT OR IGNORE INTO projets (titre, description, type_projet, semestre_id, annee_id, date_debut, date_fin, statut, note, mention) VALUES
('Système de Gestion Scolaire', 'Application web de gestion des notes et présences', 'PFE', 2, 3, '2025-02-01', '2025-06-15', 'En cours', NULL, NULL),
('Plateforme E-Learning', 'Développement d une plateforme d apprentissage en ligne avec IA', 'PFA', 1, 3, '2024-10-01', '2025-01-20', 'Terminé', 16.5, 'Bien'),
('Détection d intrusion réseau', 'Système IDS basé sur le machine learning', 'Recherche', 2, 2, '2024-03-01', '2024-06-30', 'Terminé', 17.0, 'Très Bien'),
('Application Mobile Santé', 'App Android de suivi médical', 'PFE', 2, 3, '2025-02-15', '2025-06-20', 'En cours', NULL, NULL);

-- Associations Projet ↔ Étudiant
INSERT OR IGNORE INTO projet_etudiants (projet_id, etudiant_id, role) VALUES
(1, 1, 'Chef de projet'), (1, 2, 'Membre'),
(2, 3, 'Chef de projet'), (2, 4, 'Membre'),
(3, 5, 'Chef de projet'), (3, 6, 'Membre'),
(4, 7, 'Chef de projet'), (4, 8, 'Membre');

-- Jury Projets
INSERT OR IGNORE INTO projet_jury (projet_id, professeur_id, role) VALUES
(1, 1, 'Directeur'), (1, 2, 'Rapporteur'),
(2, 2, 'Directeur'), (2, 3, 'Rapporteur'),
(3, 3, 'Directeur'), (3, 4, 'Rapporteur'),
(4, 4, 'Directeur'), (4, 5, 'Rapporteur');

-- Stages
INSERT OR IGNORE INTO stages (titre, description, etudiant_id, entreprise_id, professeur_encadrant_id, annee_id, semestre_id, date_debut, date_fin, duree_semaines, statut, note, mention) VALUES
('Stage Développement Web', 'Développement d une application interne', 1, 2, 1, 3, 1, '2024-10-01', '2024-12-31', 12, 'Terminé', 15.5, 'Bien'),
('Stage Réseau', 'Administration réseau et sécurité', 3, 3, 3, 3, 1, '2024-10-15', '2025-01-10', 12, 'Terminé', 14.0, 'Assez Bien'),
('Stage Base de données', 'Optimisation des requêtes SQL', 5, 4, 4, 2, 2, '2024-04-01', '2024-06-30', 12, 'Terminé', 16.0, 'Bien'),
('Stage Développement Mobile', 'Application Android interne', 7, 1, 5, 3, 2, '2025-03-01', '2025-06-30', 16, 'En cours', NULL, NULL);
"""


def init_database():
    """Initialise la base de données : crée les tables et insère les données de démo."""
    conn = get_connection()
    try:
        # Création des tables
        conn.executescript(SCHEMA)
        conn.commit()
        print("[DB] Tables créées avec succès.")

        # Données de démonstration (uniquement si les tables sont vides)
        cursor = conn.execute("SELECT COUNT(*) FROM etudiants")
        count = cursor.fetchone()[0]
        if count == 0:
            conn.executescript(DEMO_DATA)
            conn.commit()
            print("[DB] Données de démonstration insérées.")
        else:
            print("[DB] Base de données déjà initialisée.")

    except Exception as e:
        conn.rollback()
        print(f"[DB] Erreur lors de l'initialisation : {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH & ADMIN SCHEMA — appended on upgrade
# ══════════════════════════════════════════════════════════════════════════════

AUTH_SCHEMA = """
-- ── Users table ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    salt          TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'viewer',
    -- roles: superadmin | admin | professor | student | viewer
    full_name     TEXT    NOT NULL DEFAULT '',
    email         TEXT    UNIQUE,
    avatar_color  TEXT    DEFAULT '#3B82F6',
    is_active     INTEGER DEFAULT 1,
    must_change_pwd INTEGER DEFAULT 0,
    last_login    TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    created_by    INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ── Sessions table (remember-me tokens) ────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    token      TEXT    NOT NULL UNIQUE,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT    NOT NULL,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Audit log table ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    username   TEXT,
    action     TEXT    NOT NULL,
    entity     TEXT,
    entity_id  INTEGER,
    detail     TEXT,
    ip_address TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ── Role permissions table ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS role_permissions (
    role       TEXT NOT NULL,
    module     TEXT NOT NULL,
    can_read   INTEGER DEFAULT 1,
    can_write  INTEGER DEFAULT 0,
    can_delete INTEGER DEFAULT 0,
    PRIMARY KEY (role, module)
);

-- ── System settings ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_settings (
    key   TEXT PRIMARY KEY,
    value TEXT,
    label TEXT,
    type  TEXT DEFAULT 'text'
);
"""

AUTH_SEED = """
-- Default role permissions
INSERT OR IGNORE INTO role_permissions VALUES
  ('superadmin','*',1,1,1),
  ('admin','etudiants',1,1,1),('admin','projets',1,1,1),
  ('admin','stages',1,1,1),('admin','professeurs',1,1,1),
  ('admin','entreprises',1,1,1),('admin','users',1,1,0),
  ('admin','stats',1,0,0),('admin','audit',1,0,0),
  ('professor','etudiants',1,0,0),('professor','projets',1,1,0),
  ('professor','stages',1,1,0),('professor','professeurs',1,0,0),
  ('professor','entreprises',1,0,0),('professor','stats',1,0,0),
  ('student','etudiants',1,0,0),('student','projets',1,0,0),
  ('student','stages',1,0,0),('student','stats',1,0,0),
  ('viewer','etudiants',1,0,0),('viewer','projets',1,0,0),
  ('viewer','stages',1,0,0);

-- System settings defaults
INSERT OR IGNORE INTO system_settings VALUES
  ('app_name',       'EduTrack',           'Nom de l''application', 'text'),
  ('institution',    'Université',          'Établissement',         'text'),
  ('session_timeout','30',                  'Timeout session (min)', 'number'),
  ('max_login_attempts','5',               'Tentatives max login',  'number'),
  ('theme',          'dark',               'Thème',                 'select'),
  ('language',       'fr',                 'Langue',                'select');
"""

import hashlib, secrets as _secrets

def _hash_password(password: str, salt: str = None):
    if salt is None:
        salt = _secrets.token_hex(32)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
    return h.hex(), salt


def init_auth(conn):
    """Initialize auth tables and create default superadmin."""
    conn.executescript(AUTH_SCHEMA)
    conn.commit()

    # Check if superadmin exists
    cur = conn.execute("SELECT COUNT(*) FROM users WHERE role='superadmin'")
    if cur.fetchone()[0] == 0:
        conn.executescript(AUTH_SEED)
        conn.commit()
        # Create default superadmin
        pwd_hash, salt = _hash_password("Admin@2025")
        conn.execute("""
            INSERT OR IGNORE INTO users
              (username, password_hash, salt, role, full_name, email, avatar_color)
            VALUES (?,?,?,?,?,?,?)
        """, ("admin", pwd_hash, salt, "superadmin",
              "Administrateur Système", "admin@edutrack.dz", "#3B82F6"))
        # Demo users
        for uname, pwd, role, name, color in [
            ("prof1",    "Prof@2025",    "professor", "Dr. Ahmed Benali",   "#F59E0B"),
            ("student1", "Student@2025", "student",   "Sofiane Amrani",     "#10B981"),
            ("viewer1",  "View@2025",    "viewer",    "Invité Consultation", "#94A3B8"),
        ]:
            ph, sl = _hash_password(pwd)
            conn.execute("""
                INSERT OR IGNORE INTO users
                  (username, password_hash, salt, role, full_name, avatar_color)
                VALUES (?,?,?,?,?,?)
            """, (uname, ph, sl, role, name, color))
        conn.commit()
        print("[AUTH] Utilisateurs créés — admin / Admin@2025")
    else:
        print("[AUTH] Auth déjà initialisé.")
