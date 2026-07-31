# 🎓 EduTrack – Gestion des Projets et Stages Étudiants

Application desktop Python (Tkinter + SQLite) pour gérer les étudiants,
projets, stages, professeurs et statistiques d'un département universitaire.
§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
Aprés lancement: Login Information
Identifiant    Mot de passe    Rôle
admin            Admin@2025    superadmin
prof1            Prof@2025      professor
student1        Student@2025    student
viewer1          View@2025       viewer
§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§


---

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip

---

## ⚙️ Installation

### 1. Cloner ou décompresser le projet

```bash
cd EduTrack
```

### 2. (Optionnel) Créer un environnement virtuel

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

> **Tkinter** et **SQLite** sont inclus dans Python – aucune installation supplémentaire.
> Seul **ReportLab** (export PDF) est requis via pip.

---

## 🚀 Lancement

```bash
python main.py
```

Ou depuis **VS Code** : ouvrir le dossier `EduTrack`, puis appuyer sur **F5**
(la configuration `.vscode/launch.json` est fournie).

---

## 🗂️ Structure du Projet

```
EduTrack/
│
├── main.py                  # Point d'entrée
├── app.py                   # Fenêtre principale + navigation
├── requirements.txt
├── edutrack.db              # Base SQLite (créée automatiquement)
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py     # Connexion SQLite, execute_query
│   └── db_init.py           # Schéma SQL + données de démo
│
├── models/
│   ├── __init__.py
│   ├── etudiant.py          # CRUD Étudiant
│   ├── professeur.py        # CRUD Professeur
│   ├── projet.py            # CRUD Projet + associations
│   ├── stage.py             # CRUD Stage
│   ├── annee.py             # AnneeUniversitaire + Semestre
│   └── entreprise.py        # Entreprise + Note
│
├── controllers/
│   ├── __init__.py
│   ├── etudiant_controller.py
│   └── controllers.py       # Projet, Stage, Prof, Entreprise,
│                            # Recherche, Statistiques
│
├── views/
│   ├── __init__.py
│   ├── theme.py             # Palette, fonts, widgets réutilisables
│   ├── dashboard_view.py    # Tableau de bord
│   ├── etudiant_view.py     # Gestion étudiants
│   ├── projet_view.py       # Gestion projets + jury
│   ├── stage_view.py        # Gestion stages
│   ├── professeur_view.py   # Gestion professeurs
│   ├── entreprise_view.py   # Gestion entreprises
│   ├── recherche_view.py    # Recherche avancée
│   └── statistiques_view.py # Statistiques + graphiques
│
├── utils/
│   ├── __init__.py
│   └── pdf_export.py        # Export PDF (ReportLab)
│
├── exports/                 # PDFs générés (créé automatiquement)
│
└── .vscode/
    ├── launch.json
    └── settings.json
```

---

## ✨ Fonctionnalités

| Section | Fonctionnalités |
|---|---|
| **Dashboard** | KPI globaux, répartition par niveau/filière, statuts projets/stages |
| **Étudiants** | CRUD complet, recherche multicritères, fiche détaillée, export PDF |
| **Projets** | CRUD, association étudiants (many-to-many), jury de professeurs, notation |
| **Stages** | CRUD, association étudiant + entreprise + encadrant, notation |
| **Professeurs** | CRUD, historique projets & stages encadrés |
| **Entreprises** | CRUD, gestion contacts |
| **Recherche** | Recherche simultanée étudiants/projets/stages/professeurs avec filtres |
| **Statistiques** | Jauges, camemberts, barres horizontales, moyennes générales |
| **Export PDF** | Fiche étudiant, liste projets, liste stages, résultats recherche |

---

## 🗃️ Base de Données

La base **SQLite** (`edutrack.db`) est créée automatiquement au premier lancement
avec des **données de démonstration** (8 étudiants, 5 professeurs, 4 projets,
4 stages, 5 entreprises).

### Tables principales
- `etudiants` – informations personnelles et académiques
- `professeurs` – corps enseignant
- `projets` – projets académiques (PFE, PFA, Recherche…)
- `projet_etudiants` – relation M:N projets ↔ étudiants
- `projet_jury` – relation M:N projets ↔ professeurs (jury)
- `stages` – stages en entreprise
- `entreprises` – entreprises d'accueil
- `annees_universitaires` – gestion des années
- `semestres` – S1/S2 par année
- `notes` – évaluations détaillées

---

## 🖥️ Raccourcis VS Code

| Action | Raccourci |
|---|---|
| Lancer l'application | `F5` |
| Ouvrir le terminal | `Ctrl + `` ` |
| Formater le code | `Shift + Alt + F` |

---

## 📄 Export PDF

Les fichiers PDF sont générés dans le dossier `exports/`.
Nécessite ReportLab (`pip install reportlab`).

---

## 🛠️ Architecture MVC

```
Utilisateur → View (Tkinter)
                 ↓
            Controller (logique métier, validation)
                 ↓
            Model (requêtes SQL)
                 ↓
            Database (SQLite via db_connection)
```

---

*EduTrack v1.0.0 – Développé avec Python, Tkinter, SQLite et ReportLab*
