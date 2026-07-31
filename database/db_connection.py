"""
Module de connexion à la base de données SQLite.
Gère la création, la connexion et l'exécution des requêtes.
"""

import sqlite3
import os
from contextlib import contextmanager

# Chemin vers le fichier de base de données
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "edutrack.db")


def get_connection():
    """Retourne une connexion SQLite avec support des clés étrangères."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permet l'accès par nom de colonne
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_context():
    """Context manager pour gérer automatiquement la connexion et les transactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Erreur base de données : {e}") from e
    finally:
        conn.close()


def execute_query(query, params=(), fetchall=False, fetchone=False):
    """
    Exécute une requête SQL et retourne les résultats.
    
    Args:
        query: La requête SQL
        params: Tuple de paramètres
        fetchall: Si True, retourne tous les résultats
        fetchone: Si True, retourne un seul résultat
    
    Returns:
        Résultats de la requête ou lastrowid pour INSERT
    """
    with db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetchall:
            return [dict(row) for row in cursor.fetchall()]
        if fetchone:
            row = cursor.fetchone()
            return dict(row) if row else None
        return cursor.lastrowid


def execute_many(query, params_list):
    """Exécute une requête SQL pour une liste de paramètres."""
    with db_context() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        return cursor.rowcount


class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass
