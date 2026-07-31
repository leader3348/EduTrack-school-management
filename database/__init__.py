"""Package database – connexion et initialisation SQLite."""
from .db_connection import get_connection, execute_query, execute_many, db_context, DatabaseError
from .db_init import init_database

__all__ = ["get_connection", "execute_query", "execute_many", "db_context", "DatabaseError", "init_database"]
