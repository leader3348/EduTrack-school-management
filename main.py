"""
EduTrack v3.0 — Entry Point
Run: python main.py
"""

import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── DB + Auth init ────────────────────────────────────────────────────────────
print("=" * 56)
print("  EduTrack v3.0  ·  Dark Corporate Premium")
print("=" * 56)

from database.db_init import init_database, init_auth
from database.db_connection import get_connection

try:
    init_database()
    conn = get_connection()
    init_auth(conn)
    conn.close()
    print("[OK] Base de données et authentification prêtes.")
except Exception as e:
    print(f"[ERR] Initialisation: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("=" * 56)

# ── Tkinter bootstrap ─────────────────────────────────────────────────────────
import tkinter as tk
from views.theme import DS, apply_theme

root = tk.Tk()
root.withdraw()
apply_theme(root)
root.configure(bg=DS["bg"])


def _start_app():
    """Launch the main app after successful login."""
    from controllers.auth_controller import AuthSession
    from app import EduTrackApp
    print(f"[AUTH] {AuthSession.get_display_name()} "
          f"[{AuthSession.role()}]")
    root.destroy()
    app = EduTrackApp()
    app.mainloop()


def _on_close():
    """If login window closed, exit everything."""
    root.destroy()
    sys.exit(0)


from views.login_view import LoginView
login = LoginView(root, on_success=_start_app)
login.protocol("WM_DELETE_WINDOW", _on_close)

root.mainloop()
