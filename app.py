"""
EduTrack v3.0 — Main Application Window
Full dark corporate UI with admin panel integration and user session bar.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.theme import DS, FONTS, apply_theme, UIComponents
from views.dashboard_view    import DashboardView
from views.etudiant_view     import EtudiantView
from views.projet_view       import ProjetView
from views.stage_view        import StageView
from views.professeur_view   import ProfesseurView
from views.entreprise_view   import EntrepriseView
from views.recherche_view    import RechercheView
from views.statistiques_view import StatistiquesView
from views.admin_view        import AdminView
from controllers.auth_controller import (
    AuthSession, AuthController,
    ROLE_LABELS, ROLE_COLORS)


# ── Navigation map ────────────────────────────────────────────────────────────
NAV = [
    # (key, icon, label, min_role, section_label)
    ("dashboard",    "⊞",  "Vue d'ensemble",  None,          "NAVIGATION"),
    ("---",          "",   "GESTION",         None,          ""),
    ("etudiants",    "◈",  "Étudiants",       None,          "GESTION"),
    ("projets",      "◉",  "Projets",         None,          "GESTION"),
    ("stages",       "◎",  "Stages",          None,          "GESTION"),
    ("professeurs",  "◆",  "Professeurs",     None,          "GESTION"),
    ("entreprises",  "◇",  "Entreprises",     None,          "GESTION"),
    ("---",          "",   "OUTILS",          None,          ""),
    ("recherche",    "⊕",  "Recherche",       None,          "OUTILS"),
    ("statistiques", "⊜",  "Statistiques",    None,          "OUTILS"),
    ("---",          "",   "ADMINISTRATION",  "admin",       ""),
    ("admin",        "⚙",  "Admin Panel",     "admin",       "ADMINISTRATION"),
]

TITLES = {
    "dashboard":    ("Vue d'ensemble",       "Tableau de bord académique"),
    "etudiants":    ("Étudiants",            "Gestion du registre étudiant"),
    "projets":      ("Projets",              "Suivi des projets académiques"),
    "stages":       ("Stages",              "Gestion des stages professionnels"),
    "professeurs":  ("Corps Enseignant",     "Professeurs et encadrants"),
    "entreprises":  ("Entreprises",          "Entreprises partenaires"),
    "recherche":    ("Recherche Avancée",    "Recherche multicritères"),
    "statistiques": ("Statistiques",         "Analyses et indicateurs"),
    "admin":        ("Administration",       "Gestion des accès et paramètres"),
}

VIEW_MAP = {
    "dashboard":    DashboardView,
    "etudiants":    EtudiantView,
    "projets":      ProjetView,
    "stages":       StageView,
    "professeurs":  ProfesseurView,
    "entreprises":  EntrepriseView,
    "recherche":    RechercheView,
    "statistiques": StatistiquesView,
    "admin":        AdminView,
}


class EduTrackApp(tk.Tk):

    VERSION = "3.0"
    W, H    = 1360, 820
    SW      = 228   # sidebar width

    def __init__(self):
        super().__init__()
        self.title("EduTrack — Academic Management System")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(1100, 680)
        self.configure(bg=DS["sidebar_bg"])

        apply_theme(self)

        self._active  = None
        self._views   = {}
        self._btns    = {}
        self._notifs  = []

        self._build()
        self._navigate("dashboard")
        self._center()
        self.protocol("WM_DELETE_WINDOW", self._quit)

        # Refresh session clock every minute
        self._tick_session()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

    # ══════════════════════════════════════════════════════════════════════════
    #  LAYOUT BUILDER
    # ══════════════════════════════════════════════════════════════════════════

    def _build(self):
        # Sidebar
        self.sidebar = tk.Frame(
            self, bg=DS["sidebar_bg"], width=self.SW)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main content
        self.main = tk.Frame(self, bg=DS["bg"])
        self.main.pack(side="left", fill="both", expand=True)
        self._build_topbar()

        self.view_area = tk.Frame(self.main, bg=DS["bg"])
        self.view_area.pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════

    def _build_sidebar(self):
        # ── Brand block ───────────────────────────────────────────────────────
        brand = tk.Frame(
            self.sidebar, bg=DS["sidebar_bg"], pady=22)
        brand.pack(fill="x")

        logo_row = tk.Frame(brand, bg=DS["sidebar_bg"])
        logo_row.pack(padx=18)

        # Logo canvas
        lc = tk.Canvas(logo_row, width=40, height=40,
                       bg=DS["sidebar_bg"],
                       highlightthickness=0)
        lc.pack(side="left")
        lc.create_rectangle(
            0, 0, 40, 40,
            fill=DS["primary"], outline="")
        lc.create_rectangle(
            0, 0, 40, 4,
            fill=DS["accent"], outline="")
        lc.create_text(
            20, 21, text="E",
            font=("Segoe UI", 19, "bold"),
            fill=DS["white"])

        name_f = tk.Frame(logo_row, bg=DS["sidebar_bg"])
        name_f.pack(side="left", padx=(12, 0))
        tk.Label(name_f, text="EduTrack",
                 font=("Segoe UI", 14, "bold"),
                 bg=DS["sidebar_bg"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(name_f, text="Academic Platform",
                 font=FONTS["caption"],
                 bg=DS["sidebar_bg"],
                 fg=DS["sidebar_text"]).pack(anchor="w")

        # Separator
        tk.Frame(self.sidebar, bg=DS["border"],
                 height=1).pack(
            fill="x", padx=16, pady=(4, 10))

        # ── Navigation items ──────────────────────────────────────────────────
        for item in NAV:
            key, icon, label, min_role, _ = item

            if key == "---":
                # Check if section should show
                if min_role and not self._has_role(min_role):
                    continue
                tk.Label(self.sidebar,
                         text=f"  {label}",
                         font=("Segoe UI", 7, "bold"),
                         bg=DS["sidebar_bg"],
                         fg=DS["text_dim"],
                         anchor="w").pack(
                    fill="x", padx=18,
                    pady=(12, 4))
                continue

            # Permission gate
            if min_role and not self._has_role(min_role):
                continue

            btn = self._make_nav_btn(key, icon, label)
            btn.pack(fill="x", padx=8, pady=1)
            self._btns[key] = btn

        # ── User block (bottom) ───────────────────────────────────────────────
        tk.Frame(self.sidebar, bg=DS["border"],
                 height=1).pack(
            fill="x", padx=16, side="bottom",
            pady=(0, 4))

        user_block = tk.Frame(
            self.sidebar, bg=DS["sidebar_bg"],
            padx=14, pady=12)
        user_block.pack(side="bottom", fill="x")

        # Avatar + name row
        av_row = tk.Frame(user_block, bg=DS["sidebar_bg"])
        av_row.pack(fill="x", pady=(0, 8))

        # Small avatar circle
        av_cv = tk.Canvas(av_row, width=32, height=32,
                          bg=DS["sidebar_bg"],
                          highlightthickness=0)
        av_cv.pack(side="left")
        av_color = AuthSession.get_avatar_color()
        av_cv.create_oval(0, 0, 32, 32,
                          fill=av_color, outline="")
        initials = "".join(
            p[0].upper() for p in
            AuthSession.get_display_name().split()[:2])
        av_cv.create_text(16, 16, text=initials,
                          font=("Segoe UI", 10, "bold"),
                          fill=DS["white"])

        name_col = tk.Frame(av_row, bg=DS["sidebar_bg"],
                            padx=8)
        name_col.pack(side="left", fill="x", expand=True)
        tk.Label(name_col,
                 text=AuthSession.get_display_name(),
                 font=FONTS["sidebar_h"],
                 bg=DS["sidebar_bg"],
                 fg=DS["text_primary"],
                 anchor="w").pack(fill="x")

        role_color = ROLE_COLORS.get(
            AuthSession.role(), DS["primary"])
        tk.Label(name_col,
                 text=ROLE_LABELS.get(
                     AuthSession.role(), ""),
                 font=FONTS["caption"],
                 bg=DS["sidebar_bg"],
                 fg=role_color,
                 anchor="w").pack(fill="x")

        # Session timer
        self._session_lbl = tk.Label(
            user_block,
            text="",
            font=FONTS["caption"],
            bg=DS["sidebar_bg"],
            fg=DS["text_dim"],
            anchor="w")
        self._session_lbl.pack(fill="x", pady=(0, 8))

        # Logout button
        logout_btn = tk.Button(
            user_block,
            text="  ⏻  Déconnexion",
            font=FONTS["btn_sm"],
            bg=DS["bg_3"],
            fg=DS["danger"],
            relief="flat", bd=0,
            cursor="hand2",
            padx=10, pady=6,
            command=self._logout,
            activebackground=DS["danger_light"],
            activeforeground=DS["danger"])
        logout_btn.pack(fill="x")
        logout_btn.bind(
            "<Enter>",
            lambda e: logout_btn.config(
                bg=DS["danger_light"]))
        logout_btn.bind(
            "<Leave>",
            lambda e: logout_btn.config(
                bg=DS["bg_3"]))

    def _make_nav_btn(self, key, icon, label):
        frame = tk.Frame(self.sidebar,
                         bg=DS["sidebar_bg"],
                         cursor="hand2")

        # Active indicator strip (left)
        ind = tk.Frame(frame, bg=DS["sidebar_bg"], width=3)
        ind.pack(side="left", fill="y")

        inner = tk.Frame(frame, bg=DS["sidebar_bg"],
                         padx=12, pady=9)
        inner.pack(side="left", fill="x", expand=True)

        row = tk.Frame(inner, bg=DS["sidebar_bg"])
        row.pack(fill="x")

        icon_lbl = tk.Label(row, text=icon,
                            font=("Segoe UI", 12),
                            bg=DS["sidebar_bg"],
                            fg=DS["sidebar_text"],
                            width=2, anchor="w")
        icon_lbl.pack(side="left")

        text_lbl = tk.Label(row, text=label,
                            font=FONTS["sidebar"],
                            bg=DS["sidebar_bg"],
                            fg=DS["sidebar_text"],
                            anchor="w")
        text_lbl.pack(side="left", padx=(8, 0))

        # Store widget refs
        frame._ind      = ind
        frame._inner    = inner
        frame._row      = row
        frame._icon     = icon_lbl
        frame._text     = text_lbl
        frame._key      = key

        # Hover bindings
        def _on_enter(e, f=frame, k=key):
            if self._active != k:
                for w in [f, f._inner, f._row]:
                    w.config(bg=DS["sidebar_hover"])
                f._icon.config(bg=DS["sidebar_hover"],
                               fg=DS["text_secondary"])
                f._text.config(bg=DS["sidebar_hover"],
                               fg=DS["text_secondary"])

        def _on_leave(e, f=frame, k=key):
            if self._active != k:
                for w in [f, f._inner, f._row]:
                    w.config(bg=DS["sidebar_bg"])
                f._icon.config(bg=DS["sidebar_bg"],
                               fg=DS["sidebar_text"])
                f._text.config(bg=DS["sidebar_bg"],
                               fg=DS["sidebar_text"])

        def _on_click(e, k=key):
            self._navigate(k)

        for w in [frame, inner, row, icon_lbl, text_lbl]:
            w.bind("<Enter>",    _on_enter)
            w.bind("<Leave>",    _on_leave)
            w.bind("<Button-1>", _on_click)

        return frame

    def _activate_btn(self, key):
        btn = self._btns.get(key)
        if not btn:
            return
        for w in [btn, btn._inner, btn._row]:
            w.config(bg=DS["sidebar_active"])
        btn._icon.config(bg=DS["sidebar_active"],
                         fg=DS["accent"])
        btn._text.config(bg=DS["sidebar_active"],
                         fg=DS["sidebar_text_act"],
                         font=FONTS["sidebar_h"])
        btn._ind.config(bg=DS["sidebar_indicator"])

    def _deactivate_btn(self, key):
        btn = self._btns.get(key)
        if not btn:
            return
        for w in [btn, btn._inner, btn._row]:
            w.config(bg=DS["sidebar_bg"])
        btn._icon.config(bg=DS["sidebar_bg"],
                         fg=DS["sidebar_text"])
        btn._text.config(bg=DS["sidebar_bg"],
                         fg=DS["sidebar_text"],
                         font=FONTS["sidebar"])
        btn._ind.config(bg=DS["sidebar_bg"])

    # ══════════════════════════════════════════════════════════════════════════
    #  TOPBAR
    # ══════════════════════════════════════════════════════════════════════════

    def _build_topbar(self):
        self.topbar = tk.Frame(
            self.main,
            bg=DS["topbar_bg"],
            height=54,
            highlightbackground=DS["border"],
            highlightthickness=1)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        # Left: breadcrumb
        left = tk.Frame(self.topbar, bg=DS["topbar_bg"])
        left.pack(side="left", padx=22, fill="y")

        self._tb_title = tk.Label(
            left, text="",
            font=FONTS["h3"],
            bg=DS["topbar_bg"],
            fg=DS["text_primary"])
        self._tb_title.pack(side="left", anchor="center")

        self._tb_sep = tk.Label(
            left, text="  /  ",
            font=FONTS["body_sm"],
            bg=DS["topbar_bg"],
            fg=DS["border_bright"])
        self._tb_sep.pack(side="left", anchor="center")

        self._tb_sub = tk.Label(
            left, text="",
            font=FONTS["body_sm"],
            bg=DS["topbar_bg"],
            fg=DS["text_muted"])
        self._tb_sub.pack(side="left", anchor="center")

        # Right: status indicators
        right = tk.Frame(self.topbar, bg=DS["topbar_bg"])
        right.pack(side="right", padx=20, fill="y")

        from datetime import datetime
        date_str = datetime.now().strftime(
            "%a %d %b %Y").capitalize()

        # Permission badge
        role = AuthSession.role()
        rc   = ROLE_COLORS.get(role, DS["primary"])
        role_badge = tk.Label(
            right,
            text=f"  {ROLE_LABELS.get(role, role)}  ",
            font=FONTS["badge"],
            bg=DS["bg_3"], fg=rc,
            highlightbackground=rc,
            highlightthickness=1)
        role_badge.pack(side="right", padx=(6, 0),
                        anchor="center", pady=16)

        # Separator
        tk.Frame(right, bg=DS["border"],
                 width=1).pack(
            side="right", fill="y",
            pady=14, padx=8)

        # Date
        tk.Label(right, text=f"📅  {date_str}",
                 font=FONTS["body_sm"],
                 bg=DS["topbar_bg"],
                 fg=DS["text_muted"]).pack(
            side="right", anchor="center", pady=16)

        # Separator
        tk.Frame(right, bg=DS["border"],
                 width=1).pack(
            side="right", fill="y",
            pady=14, padx=8)

        # Online indicator
        status_f = tk.Frame(right, bg=DS["topbar_bg"])
        status_f.pack(side="right", anchor="center",
                      pady=16)
        tk.Label(status_f, text="●",
                 font=("Segoe UI", 9),
                 bg=DS["topbar_bg"],
                 fg=DS["success"]).pack(side="left")
        tk.Label(status_f, text="  Connecté",
                 font=FONTS["caption"],
                 bg=DS["topbar_bg"],
                 fg=DS["text_muted"]).pack(side="left")

    # ══════════════════════════════════════════════════════════════════════════
    #  NAVIGATION
    # ══════════════════════════════════════════════════════════════════════════

    def _navigate(self, key):
        if self._active == key:
            return

        # Permission check
        if key not in ("dashboard",) and not AuthSession.can(key, "read"):
            from views.theme import show_message
            show_message(
                self, "Accès refusé",
                f"Vous n'avez pas la permission d'accéder à «{key}».",
                "warning")
            return

        # Deactivate old button
        if self._active:
            self._deactivate_btn(self._active)

        self._active = key
        self._activate_btn(key)

        # Update topbar
        title, sub = TITLES.get(key, (key.title(), ""))
        self._tb_title.config(text=title)
        self._tb_sub.config(text=sub)

        # Hide all views
        for v in self._views.values():
            v.pack_forget()

        # Create or reuse view
        if key not in self._views:
            cls = VIEW_MAP.get(key)
            if cls:
                self._views[key] = cls(self.view_area)
            else:
                placeholder = tk.Frame(
                    self.view_area, bg=DS["bg"])
                tk.Label(
                    placeholder,
                    text=f"Module '{key}' introuvable.",
                    font=FONTS["body"],
                    bg=DS["bg"],
                    fg=DS["text_muted"]).pack(pady=40)
                self._views[key] = placeholder

        self._views[key].pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  AUTH HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _has_role(self, min_role: str) -> bool:
        """Check if current user has at least the given role tier."""
        hierarchy = ["viewer", "student", "professor",
                     "admin", "superadmin"]
        user_role = AuthSession.role()
        try:
            return (hierarchy.index(user_role)
                    >= hierarchy.index(min_role))
        except ValueError:
            return False

    def _tick_session(self):
        """Update session duration label every 60s."""
        dur = AuthSession.session_duration()
        if hasattr(self, "_session_lbl"):
            self._session_lbl.config(
                text=f"Session : {dur}")
        self.after(60_000, self._tick_session)

    def _logout(self):
        if messagebox.askokcancel(
                "Déconnexion",
                "Voulez-vous vous déconnecter ?",
                parent=self):
            AuthController.logout()
            self.destroy()
            # Relaunch login
            _relaunch()

    def _quit(self):
        if messagebox.askokcancel(
                "Quitter EduTrack",
                "Fermer l'application ?",
                parent=self):
            self.destroy()


def _relaunch():
    """Restart the login flow without re-importing."""
    import importlib
    import subprocess
    import sys
    subprocess.Popen([sys.executable, __file__])
