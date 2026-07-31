"""
EduTrack Auth Controller — Login, session, permissions, audit.
"""

import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from database.db_connection import execute_query, get_connection


# ══════════════════════════════════════════════════════════════════════════════
#  PASSWORD UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def _hash(password: str, salt: str) -> str:
    h = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 260000)
    return h.hex()


def _new_salt() -> str:
    return secrets.token_hex(32)


def _check_password_strength(pwd: str) -> tuple[bool, str]:
    """Returns (ok, message)."""
    if len(pwd) < 8:
        return False, "Minimum 8 caractères."
    if not any(c.isupper() for c in pwd):
        return False, "Au moins une majuscule."
    if not any(c.islower() for c in pwd):
        return False, "Au moins une minuscule."
    if not any(c.isdigit() for c in pwd):
        return False, "Au moins un chiffre."
    return True, "OK"


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH SESSION (in-memory singleton)
# ══════════════════════════════════════════════════════════════════════════════

class AuthSession:
    """Global auth session — singleton."""
    _current_user  = None
    _login_time    = None
    _permissions   = {}

    @classmethod
    def login(cls, user: dict, permissions: dict):
        cls._current_user = user
        cls._login_time   = datetime.now()
        cls._permissions  = permissions

    @classmethod
    def logout(cls):
        cls._current_user = None
        cls._login_time   = None
        cls._permissions  = {}

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._current_user is not None

    @classmethod
    def user(cls) -> dict:
        return cls._current_user or {}

    @classmethod
    def role(cls) -> str:
        return (cls._current_user or {}).get("role", "viewer")

    @classmethod
    def is_superadmin(cls) -> bool:
        return cls.role() == "superadmin"

    @classmethod
    def is_admin_or_above(cls) -> bool:
        return cls.role() in ("superadmin", "admin")

    @classmethod
    def can(cls, module: str, action: str = "read") -> bool:
        """Check permission: action = read | write | delete."""
        if cls.is_superadmin():
            return True
        key = f"{module}.{action}"
        # Check wildcard
        if cls._permissions.get("*"):
            return True
        perm = cls._permissions.get(module, {})
        return bool(perm.get(f"can_{action}", False))

    @classmethod
    def get_display_name(cls) -> str:
        u = cls._current_user or {}
        return u.get("full_name") or u.get("username", "Inconnu")

    @classmethod
    def get_avatar_color(cls) -> str:
        return (cls._current_user or {}).get("avatar_color", "#3B82F6")

    @classmethod
    def session_duration(cls) -> str:
        if not cls._login_time:
            return ""
        delta = datetime.now() - cls._login_time
        mins  = int(delta.total_seconds() // 60)
        if mins < 60:
            return f"{mins}min"
        return f"{mins//60}h{mins%60:02d}min"


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════

class AuthController:

    # ── Login / Logout ────────────────────────────────────────────────────────

    @staticmethod
    def login(username: str, password: str) -> tuple[bool, str]:
        """
        Attempt login.
        Returns (success: bool, message: str).
        """
        if not username.strip() or not password:
            return False, "Identifiant et mot de passe requis."

        user = execute_query(
            "SELECT * FROM users WHERE username=? AND is_active=1",
            (username.strip().lower(),), fetchone=True)

        if not user:
            AuthController._audit(None, username, "LOGIN_FAILED",
                                   detail="Utilisateur inconnu")
            return False, "Identifiant ou mot de passe incorrect."

        # Verify password
        expected = _hash(password, user["salt"])
        if expected != user["password_hash"]:
            AuthController._audit(user["id"], username, "LOGIN_FAILED",
                                   detail="Mauvais mot de passe")
            return False, "Identifiant ou mot de passe incorrect."

        # Load permissions
        perms = AuthController._load_permissions(user["role"])

        # Update last_login
        execute_query(
            "UPDATE users SET last_login=? WHERE id=?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user["id"]))

        # Set session
        AuthSession.login(dict(user), perms)
        AuthController._audit(user["id"], username, "LOGIN_SUCCESS")

        if user.get("must_change_pwd"):
            return True, "MUST_CHANGE_PWD"
        return True, "OK"

    @staticmethod
    def logout():
        u = AuthSession.user()
        AuthController._audit(u.get("id"), u.get("username","?"),
                               "LOGOUT")
        AuthSession.logout()

    @staticmethod
    def change_password(user_id: int, old_pwd: str,
                        new_pwd: str) -> tuple[bool, str]:
        user = execute_query(
            "SELECT * FROM users WHERE id=?",
            (user_id,), fetchone=True)
        if not user:
            return False, "Utilisateur introuvable."

        # Verify old password
        if _hash(old_pwd, user["salt"]) != user["password_hash"]:
            return False, "Ancien mot de passe incorrect."

        ok, msg = _check_password_strength(new_pwd)
        if not ok:
            return False, msg

        salt    = _new_salt()
        new_hash = _hash(new_pwd, salt)
        execute_query(
            "UPDATE users SET password_hash=?, salt=?, must_change_pwd=0 WHERE id=?",
            (new_hash, salt, user_id))
        AuthController._audit(user_id, user["username"],
                               "PASSWORD_CHANGED")
        return True, "Mot de passe modifié."

    # ── User CRUD ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_users() -> list:
        return execute_query(
            """SELECT u.*, 
               (SELECT username FROM users WHERE id=u.created_by) as created_by_name
               FROM users u ORDER BY role, username""",
            fetchall=True)

    @staticmethod
    def get_user(user_id: int) -> dict:
        return execute_query(
            "SELECT * FROM users WHERE id=?",
            (user_id,), fetchone=True)

    @staticmethod
    def create_user(username: str, password: str, role: str,
                    full_name: str, email: str = "",
                    avatar_color: str = "#3B82F6") -> tuple[bool, str]:
        if not username.strip():
            return False, "Nom d'utilisateur requis."
        ok, msg = _check_password_strength(password)
        if not ok:
            return False, msg
        existing = execute_query(
            "SELECT id FROM users WHERE username=?",
            (username.lower(),), fetchone=True)
        if existing:
            return False, f"L'identifiant '{username}' existe déjà."

        salt     = _new_salt()
        pwd_hash = _hash(password, salt)
        uid = execute_query(
            """INSERT INTO users
               (username, password_hash, salt, role, full_name,
                email, avatar_color, created_by)
               VALUES (?,?,?,?,?,?,?,?)""",
            (username.lower(), pwd_hash, salt, role,
             full_name, email, avatar_color,
             AuthSession.user().get("id")))

        AuthController._audit(
            AuthSession.user().get("id"),
            AuthSession.user().get("username","system"),
            "USER_CREATED", "users", uid,
            f"Créé: {username} ({role})")
        return True, "Utilisateur créé."

    @staticmethod
    def update_user(user_id: int, **kwargs) -> tuple[bool, str]:
        allowed = {"full_name", "email", "role",
                   "avatar_color", "is_active"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False, "Aucun champ à modifier."
        set_cl = ", ".join(f"{k}=?" for k in fields)
        vals   = list(fields.values()) + [user_id]
        execute_query(
            f"UPDATE users SET {set_cl} WHERE id=?", tuple(vals))
        AuthController._audit(
            AuthSession.user().get("id"),
            AuthSession.user().get("username","system"),
            "USER_UPDATED", "users", user_id)
        return True, "Utilisateur modifié."

    @staticmethod
    def reset_password(user_id: int,
                       new_pwd: str) -> tuple[bool, str]:
        ok, msg = _check_password_strength(new_pwd)
        if not ok:
            return False, msg
        salt     = _new_salt()
        pwd_hash = _hash(new_pwd, salt)
        execute_query(
            """UPDATE users SET password_hash=?, salt=?,
               must_change_pwd=1 WHERE id=?""",
            (pwd_hash, salt, user_id))
        AuthController._audit(
            AuthSession.user().get("id"),
            AuthSession.user().get("username","system"),
            "PASSWORD_RESET", "users", user_id)
        return True, "Mot de passe réinitialisé."

    @staticmethod
    def toggle_user(user_id: int) -> bool:
        user = execute_query(
            "SELECT is_active FROM users WHERE id=?",
            (user_id,), fetchone=True)
        if not user:
            return False
        new_state = 0 if user["is_active"] else 1
        execute_query(
            "UPDATE users SET is_active=? WHERE id=?",
            (new_state, user_id))
        action = "USER_ACTIVATED" if new_state else "USER_DEACTIVATED"
        AuthController._audit(
            AuthSession.user().get("id"),
            AuthSession.user().get("username","system"),
            action, "users", user_id)
        return bool(new_state)

    @staticmethod
    def delete_user(user_id: int) -> tuple[bool, str]:
        # Cannot delete superadmin or yourself
        user = execute_query(
            "SELECT * FROM users WHERE id=?",
            (user_id,), fetchone=True)
        if not user:
            return False, "Utilisateur introuvable."
        if user["role"] == "superadmin":
            return False, "Impossible de supprimer le superadmin."
        if user_id == AuthSession.user().get("id"):
            return False, "Impossible de vous supprimer vous-même."
        execute_query("DELETE FROM users WHERE id=?", (user_id,))
        AuthController._audit(
            AuthSession.user().get("id"),
            AuthSession.user().get("username","system"),
            "USER_DELETED", "users", user_id,
            f"Supprimé: {user['username']}")
        return True, "Utilisateur supprimé."

    # ── Permissions ───────────────────────────────────────────────────────────

    @staticmethod
    def _load_permissions(role: str) -> dict:
        if role == "superadmin":
            return {"*": True}
        rows = execute_query(
            "SELECT * FROM role_permissions WHERE role=?",
            (role,), fetchall=True)
        perms = {}
        for r in rows:
            perms[r["module"]] = {
                "can_read":   bool(r["can_read"]),
                "can_write":  bool(r["can_write"]),
                "can_delete": bool(r["can_delete"]),
            }
        return perms

    @staticmethod
    def get_all_permissions() -> list:
        return execute_query(
            "SELECT * FROM role_permissions ORDER BY role, module",
            fetchall=True)

    @staticmethod
    def update_permission(role: str, module: str,
                          can_read: int, can_write: int,
                          can_delete: int):
        execute_query("""
            INSERT OR REPLACE INTO role_permissions
              (role, module, can_read, can_write, can_delete)
            VALUES (?,?,?,?,?)""",
            (role, module, can_read, can_write, can_delete))

    # ── Audit ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _audit(user_id, username, action,
               entity=None, entity_id=None, detail=None):
        try:
            execute_query("""
                INSERT INTO audit_log
                  (user_id, username, action, entity, entity_id, detail)
                VALUES (?,?,?,?,?,?)""",
                (user_id, username, action,
                 entity, entity_id, detail))
        except Exception:
            pass  # Never crash on audit

    @staticmethod
    def get_audit_log(limit: int = 200) -> list:
        return execute_query(
            """SELECT * FROM audit_log
               ORDER BY created_at DESC LIMIT ?""",
            (limit,), fetchall=True)

    @staticmethod
    def get_audit_for_user(user_id: int) -> list:
        return execute_query(
            """SELECT * FROM audit_log WHERE user_id=?
               ORDER BY created_at DESC LIMIT 100""",
            (user_id,), fetchall=True)

    # ── System Settings ───────────────────────────────────────────────────────

    @staticmethod
    def get_settings() -> dict:
        rows = execute_query(
            "SELECT key, value, label, type FROM system_settings",
            fetchall=True)
        return {r["key"]: r for r in rows}

    @staticmethod
    def set_setting(key: str, value: str):
        execute_query(
            """INSERT OR REPLACE INTO system_settings (key, value)
               VALUES (?,?)""",
            (key, value))

    # ── Stats ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_user_stats() -> dict:
        total = execute_query(
            "SELECT COUNT(*) as n FROM users",
            fetchone=True)["n"]
        active = execute_query(
            "SELECT COUNT(*) as n FROM users WHERE is_active=1",
            fetchone=True)["n"]
        by_role = execute_query(
            "SELECT role, COUNT(*) as n FROM users GROUP BY role",
            fetchall=True)
        last_logins = execute_query(
            """SELECT username, full_name, role, last_login, avatar_color
               FROM users WHERE last_login IS NOT NULL
               ORDER BY last_login DESC LIMIT 5""",
            fetchall=True)
        return {
            "total":       total,
            "active":      active,
            "inactive":    total - active,
            "by_role":     by_role,
            "last_logins": last_logins,
        }


# Convenience roles list
ROLES = [
    ("superadmin", "Super Administrateur", "#EF4444"),
    ("admin",      "Administrateur",        "#F59E0B"),
    ("professor",  "Professeur",            "#3B82F6"),
    ("student",    "Étudiant",              "#10B981"),
    ("viewer",     "Observateur",           "#94A3B8"),
]

ROLE_LABELS = {r[0]: r[1] for r in ROLES}
ROLE_COLORS = {r[0]: r[2] for r in ROLES}
MODULES = ["etudiants","projets","stages","professeurs",
           "entreprises","stats","audit","users"]
