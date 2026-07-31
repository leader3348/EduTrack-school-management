"""
EduTrack — User Profile & Quick Settings widget (topbar dropdown).
"""

import tkinter as tk
from views.theme import DS, FONTS, UIComponents, show_message, show_toast
from controllers.auth_controller import AuthController, AuthSession, ROLE_LABELS, ROLE_COLORS


class ProfileDropdown(tk.Toplevel):
    """Quick profile panel that drops from the topbar avatar."""

    def __init__(self, parent, anchor_widget, on_logout=None):
        super().__init__(parent)
        self.on_logout = on_logout
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg=DS["card"],
                    highlightbackground=DS["border_bright"],
                    highlightthickness=1)
        self._build()
        self._position(anchor_widget)
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_set()

    def _position(self, widget):
        self.update_idletasks()
        x = widget.winfo_rootx() + widget.winfo_width() - self.winfo_width()
        y = widget.winfo_rooty() + widget.winfo_height() + 4
        self.geometry(f"+{x}+{y}")

    def _build(self):
        u     = AuthSession.user()
        role  = AuthSession.role()
        rc    = ROLE_COLORS.get(role, DS["primary"])
        rl    = ROLE_LABELS.get(role, role)
        name  = AuthSession.get_display_name()
        dur   = AuthSession.session_duration()

        # ── Avatar + name ──────────────────────────────────────────────────
        top = tk.Frame(self, bg=DS["card"], padx=16, pady=14)
        top.pack(fill="x")

        av_cv = tk.Canvas(top, width=44, height=44,
                          bg=DS["card"], highlightthickness=0)
        av_cv.pack(side="left")
        av_cv.create_oval(2, 2, 42, 42,
                          fill=AuthSession.get_avatar_color(),
                          outline="")
        initials = name[:2].upper() if name else "?"
        av_cv.create_text(22, 22, text=initials,
                          font=("Segoe UI", 13, "bold"),
                          fill=DS["white"])

        info = tk.Frame(top, bg=DS["card"], padx=(10))
        info.pack(side="left")
        tk.Label(info, text=name,
                 font=FONTS["h4"],
                 bg=DS["card"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(info, text=u.get("email",""),
                 font=FONTS["caption"],
                 bg=DS["card"],
                 fg=DS["text_muted"]).pack(anchor="w")

        # Role badge
        badge = tk.Frame(top, bg=rc)
        badge.pack(side="right", anchor="center")
        tk.Label(badge, text=f"  {rl}  ",
                 font=FONTS["badge"],
                 bg=rc, fg=DS["white"]).pack(padx=4, pady=3)

        # ── Session info ───────────────────────────────────────────────────
        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x")
        si = tk.Frame(self, bg=DS["bg_3"], padx=16, pady=8)
        si.pack(fill="x")
        tk.Label(si, text="⏱  Session active",
                 font=FONTS["caption"],
                 bg=DS["bg_3"], fg=DS["text_muted"]).pack(side="left")
        tk.Label(si, text=dur,
                 font=FONTS["caption"],
                 bg=DS["bg_3"], fg=DS["success"]).pack(side="right")

        # ── Last login ────────────────────────────────────────────────────
        ll = u.get("last_login","—") or "—"
        ll_row = tk.Frame(self, bg=DS["bg_3"], padx=16, pady=2)
        ll_row.pack(fill="x")
        tk.Label(ll_row, text="Dernière connexion :",
                 font=FONTS["caption"],
                 bg=DS["bg_3"], fg=DS["text_muted"]).pack(side="left")
        tk.Label(ll_row, text=str(ll)[:16],
                 font=FONTS["caption"],
                 bg=DS["bg_3"], fg=DS["text_secondary"]).pack(side="right")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x")

        # ── Actions ────────────────────────────────────────────────────────
        actions = [
            ("🔐  Changer le mot de passe", self._change_pwd),
        ]
        for label, cmd in actions:
            btn = tk.Button(self, text=label,
                            font=FONTS["body_sm"],
                            bg=DS["card"], fg=DS["text_secondary"],
                            relief="flat", bd=0,
                            padx=16, pady=9,
                            cursor="hand2",
                            anchor="w",
                            command=cmd,
                            activebackground=DS["bg_3"])
            btn.pack(fill="x")
            btn.bind("<Enter>",
                lambda e, b=btn: b.config(
                    bg=DS["bg_3"], fg=DS["text_primary"]))
            btn.bind("<Leave>",
                lambda e, b=btn: b.config(
                    bg=DS["card"], fg=DS["text_secondary"]))

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x")

        # Logout
        logout_btn = tk.Button(
            self, text="  ⎋  Déconnexion",
            font=FONTS["btn"],
            bg=DS["danger_light"], fg=DS["danger"],
            relief="flat", bd=0,
            padx=16, pady=10,
            cursor="hand2",
            anchor="w",
            command=self._logout,
            activebackground=DS["danger_mid"])
        logout_btn.pack(fill="x")
        logout_btn.bind("<Enter>",
            lambda e: logout_btn.config(bg=DS["danger_mid"]))
        logout_btn.bind("<Leave>",
            lambda e: logout_btn.config(bg=DS["danger_light"]))

    def _change_pwd(self):
        self.destroy()
        from views.login_view import ChangePasswordDialog
        uid = AuthSession.user().get("id")
        ChangePasswordDialog(
            self.master, uid,
            on_success=lambda: show_toast(
                self.master, "Mot de passe modifié.", "success")
        ).grab_set()

    def _logout(self):
        self.destroy()
        if self.on_logout:
            self.on_logout()
