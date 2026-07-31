"""
EduTrack Login Screen v3.0 — Dark Corporate Premium
Cinematic login with animated elements and role-based access.
"""

import tkinter as tk
from tkinter import ttk
import math
import time
import threading
from views.theme import DS, FONTS, show_message
from controllers.auth_controller import AuthController, ROLE_LABELS, ROLE_COLORS


class LoginView(tk.Toplevel):
    """
    Full-screen cinematic login window.
    Blocks until authenticated. Returns via on_success callback.
    """

    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success   = on_success
        self._attempt     = 0
        self._max_attempts = 5
        self._locked_until = None
        self._anim_running = True
        self._particles    = []

        self.title("EduTrack — Authentification")
        self.configure(bg=DS["bg"])
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Full screen
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{sw}x{sh}+0+0")
        self.state("zoomed")

        self.lift()
        self.focus_force()
        self.grab_set()

        self._build()
        self._start_animations()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        # Background canvas with particle effect
        self.bg_canvas = tk.Canvas(
            self, bg=DS["bg"], highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)

        # Draw grid lines (Bloomberg-style)
        self._draw_grid()

        # Split layout: left brand panel + right form panel
        self._build_left_panel()
        self._build_right_panel()

    def _draw_grid(self):
        """Draw subtle grid lines on background canvas."""
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        grid_color = "#0F1629"
        step = 60
        for x in range(0, w + step, step):
            self.bg_canvas.create_line(
                x, 0, x, h, fill=grid_color, width=1)
        for y in range(0, h + step, step):
            self.bg_canvas.create_line(
                0, y, w, y, fill=grid_color, width=1)
        # Accent diagonal lines
        for i in range(0, w + h, 200):
            self.bg_canvas.create_line(
                i, 0, i - h, h,
                fill="#0D1526", width=1)

    def _build_left_panel(self):
        """Left: animated brand identity panel."""
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        panel_w = int(sw * 0.46)

        left = tk.Frame(
            self, bg="#080C17",
            highlightbackground=DS["border"],
            highlightthickness=1)
        left.place(x=0, y=0, width=panel_w, relheight=1)

        # Animated accent bar
        accent = tk.Frame(left, bg=DS["primary"], width=4)
        accent.pack(side="right", fill="y")

        inner = tk.Frame(left, bg="#080C17")
        inner.place(relx=0.5, rely=0.5, anchor="center",
                    width=panel_w - 80)

        # Large E logo
        logo_canvas = tk.Canvas(
            inner, width=90, height=90,
            bg="#080C17", highlightthickness=0)
        logo_canvas.pack(pady=(0, 28))

        # Outer ring
        logo_canvas.create_oval(
            4, 4, 86, 86,
            outline=DS["primary"], width=2, fill="#0D1526")
        # Inner fill
        logo_canvas.create_oval(
            14, 14, 76, 76,
            outline="", fill=DS["primary"])
        # E letter
        logo_canvas.create_text(
            45, 45, text="E",
            font=("Segoe UI", 36, "bold"),
            fill=DS["white"])

        # App name
        tk.Label(inner, text="EduTrack",
                 font=("Segoe UI", 34, "bold"),
                 bg="#080C17",
                 fg=DS["text_primary"]).pack()
        tk.Label(inner,
                 text="Academic Management System",
                 font=("Segoe UI", 11),
                 bg="#080C17",
                 fg=DS["text_muted"]).pack(pady=(4, 40))

        # Divider
        tk.Frame(inner, bg=DS["border"], height=1).pack(
            fill="x", pady=(0, 32))

        # Feature bullets
        features = [
            (DS["primary"],  "⊞",  "Gestion des étudiants & projets"),
            (DS["teal"],     "◎",  "Suivi des stages professionnels"),
            (DS["purple"],   "◉",  "Analyses & statistiques avancées"),
            (DS["success"],  "◈",  "Export PDF professionnel"),
            (DS["warning"],  "⊜",  "Administration & sécurité"),
        ]
        for color, icon, text in features:
            row = tk.Frame(inner, bg="#080C17")
            row.pack(fill="x", pady=5)
            # Icon badge
            badge = tk.Frame(row, bg=color,
                             width=28, height=28)
            badge.pack(side="left")
            badge.pack_propagate(False)
            tk.Label(badge, text=icon,
                     font=("Segoe UI", 10),
                     bg=color,
                     fg=DS["white"]).pack(
                expand=True)
            tk.Label(row, text=f"  {text}",
                     font=FONTS["body"],
                     bg="#080C17",
                     fg=DS["text_secondary"]).pack(
                side="left", pady=1)

        # Version tag at bottom
        ver_f = tk.Frame(left, bg="#080C17")
        ver_f.place(relx=0.5, rely=0.96, anchor="center")
        tk.Label(ver_f, text="v3.0  ·  Production  ·  © 2025",
                 font=FONTS["caption"],
                 bg="#080C17",
                 fg=DS["text_dim"]).pack()

    def _build_right_panel(self):
        """Right: login form panel."""
        sw = self.winfo_screenwidth()
        panel_w = int(sw * 0.46)

        right = tk.Frame(self, bg=DS["bg"])
        right.place(x=panel_w, y=0,
                    width=sw - panel_w, relheight=1)

        # Center form
        form_container = tk.Frame(right, bg=DS["bg"])
        form_container.place(
            relx=0.5, rely=0.5, anchor="center",
            width=420)

        # Welcome text
        tk.Label(form_container,
                 text="Connexion",
                 font=("Segoe UI", 28, "bold"),
                 bg=DS["bg"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(form_container,
                 text="Entrez vos identifiants pour accéder à EduTrack",
                 font=FONTS["body"],
                 bg=DS["bg"],
                 fg=DS["text_muted"]).pack(
            anchor="w", pady=(4, 32))

        # Form card
        card = tk.Frame(
            form_container, bg=DS["card"],
            highlightbackground=DS["border_bright"],
            highlightthickness=1)
        card.pack(fill="x")

        # Top accent
        tk.Frame(card, bg=DS["primary"], height=2).pack(fill="x")

        form = tk.Frame(card, bg=DS["card"],
                        padx=32, pady=28)
        form.pack(fill="x")

        # Username
        tk.Label(form, text="Identifiant",
                 font=FONTS["label"],
                 bg=DS["card"],
                 fg=DS["text_muted"],
                 anchor="w").pack(fill="x", pady=(0, 4))

        user_frame = tk.Frame(
            form, bg=DS["bg_3"],
            highlightbackground=DS["border_bright"],
            highlightthickness=1)
        user_frame.pack(fill="x", pady=(0, 16))

        tk.Label(user_frame, text="◈",
                 font=("Segoe UI", 11),
                 bg=DS["bg_3"],
                 fg=DS["text_muted"],
                 padx=12).pack(side="left")

        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            user_frame,
            textvariable=self.username_var,
            font=FONTS["body_lg"],
            bg=DS["bg_3"],
            fg=DS["text_primary"],
            insertbackground=DS["primary"],
            relief="flat", bd=0)
        self.username_entry.pack(
            side="left", fill="x", expand=True,
            pady=12, padx=(0, 12))
        self.username_entry.bind(
            "<FocusIn>",
            lambda e: user_frame.config(
                highlightbackground=DS["primary"]))
        self.username_entry.bind(
            "<FocusOut>",
            lambda e: user_frame.config(
                highlightbackground=DS["border_bright"]))

        # Password
        tk.Label(form, text="Mot de passe",
                 font=FONTS["label"],
                 bg=DS["card"],
                 fg=DS["text_muted"],
                 anchor="w").pack(fill="x", pady=(0, 4))

        pwd_frame = tk.Frame(
            form, bg=DS["bg_3"],
            highlightbackground=DS["border_bright"],
            highlightthickness=1)
        pwd_frame.pack(fill="x", pady=(0, 8))

        tk.Label(pwd_frame, text="◉",
                 font=("Segoe UI", 11),
                 bg=DS["bg_3"],
                 fg=DS["text_muted"],
                 padx=12).pack(side="left")

        self.pwd_var = tk.StringVar()
        self.pwd_entry = tk.Entry(
            pwd_frame,
            textvariable=self.pwd_var,
            font=FONTS["body_lg"],
            bg=DS["bg_3"],
            fg=DS["text_primary"],
            insertbackground=DS["primary"],
            show="●",
            relief="flat", bd=0)
        self.pwd_entry.pack(
            side="left", fill="x", expand=True,
            pady=12, padx=(0, 4))
        pwd_frame.bind(
            "<FocusIn>",
            lambda e: pwd_frame.config(
                highlightbackground=DS["primary"]))

        # Show/hide password toggle
        self._show_pwd = False
        self.eye_btn = tk.Label(
            pwd_frame, text="👁",
            font=("Segoe UI Emoji", 11),
            bg=DS["bg_3"],
            fg=DS["text_muted"],
            cursor="hand2", padx=10)
        self.eye_btn.pack(side="right")
        self.eye_btn.bind("<Button-1>",
                          self._toggle_pwd_visibility)

        pwd_frame.bind(
            "<FocusIn>",
            lambda e: pwd_frame.config(
                highlightbackground=DS["primary"]))
        self.pwd_entry.bind(
            "<FocusIn>",
            lambda e: pwd_frame.config(
                highlightbackground=DS["primary"]))
        self.pwd_entry.bind(
            "<FocusOut>",
            lambda e: pwd_frame.config(
                highlightbackground=DS["border_bright"]))

        # Remember me
        opt_row = tk.Frame(form, bg=DS["card"])
        opt_row.pack(fill="x", pady=(0, 20))
        self.remember_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            opt_row,
            text="  Rester connecté",
            variable=self.remember_var,
            font=FONTS["body_sm"],
            bg=DS["card"],
            fg=DS["text_secondary"],
            selectcolor=DS["bg_3"],
            activebackground=DS["card"],
            activeforeground=DS["text_primary"],
            cursor="hand2",
            relief="flat",
            bd=0).pack(side="left")

        # Status label
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(
            form,
            textvariable=self.status_var,
            font=FONTS["body_sm"],
            bg=DS["card"],
            fg=DS["danger"],
            anchor="w",
            wraplength=340)
        self.status_lbl.pack(fill="x", pady=(0, 16))

        # Login button
        self.login_btn = tk.Button(
            form,
            text="  Connexion  →",
            font=("Segoe UI", 12, "bold"),
            bg=DS["primary"],
            fg=DS["white"],
            relief="flat", bd=0,
            cursor="hand2",
            padx=20, pady=12,
            command=self._attempt_login,
            activebackground=DS["primary_hover"],
            activeforeground=DS["white"])
        self.login_btn.pack(fill="x")
        self.login_btn.bind(
            "<Enter>",
            lambda e: self.login_btn.config(
                bg=DS["primary_hover"]))
        self.login_btn.bind(
            "<Leave>",
            lambda e: self.login_btn.config(
                bg=DS["primary"]))

        # Demo credentials hint
        hint_frame = tk.Frame(form, bg=DS["card"])
        hint_frame.pack(fill="x", pady=(20, 0))
        tk.Frame(hint_frame, bg=DS["border"],
                 height=1).pack(fill="x", pady=(0, 12))
        tk.Label(hint_frame,
                 text="Comptes de démonstration :",
                 font=FONTS["caption"],
                 bg=DS["card"],
                 fg=DS["text_dim"]).pack(anchor="w")

        demos = [
            ("admin",    "Admin@2025",    "superadmin", DS["danger"]),
            ("prof1",    "Prof@2025",     "professor",  DS["warning"]),
            ("student1", "Student@2025",  "student",    DS["success"]),
        ]
        for uname, pwd, role, color in demos:
            row = tk.Frame(hint_frame, bg=DS["card"],
                           cursor="hand2")
            row.pack(fill="x", pady=2)
            tk.Label(row, text="▸",
                     font=FONTS["body_sm"],
                     bg=DS["card"],
                     fg=color).pack(side="left")
            lbl = tk.Label(
                row,
                text=f"  {uname}  ·  {pwd}",
                font=FONTS["mono_sm"],
                bg=DS["card"],
                fg=DS["text_dim"],
                cursor="hand2")
            lbl.pack(side="left")
            role_lbl = tk.Label(
                row,
                text=f"  [{role}]",
                font=FONTS["caption"],
                bg=DS["card"],
                fg=color)
            role_lbl.pack(side="left")

            # Click to autofill
            def autofill(u=uname, p=pwd):
                self.username_var.set(u)
                self.pwd_var.set(p)
                self.username_entry.focus_set()
            for w in [row, lbl, role_lbl]:
                w.bind("<Button-1>",
                       lambda e, f=autofill: f())

        # Keyboard shortcut
        self.bind("<Return>", lambda e: self._attempt_login())
        self.username_entry.focus_set()

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _toggle_pwd_visibility(self, event=None):
        self._show_pwd = not self._show_pwd
        self.pwd_entry.config(
            show="" if self._show_pwd else "●")
        self.eye_btn.config(
            fg=DS["primary"] if self._show_pwd
            else DS["text_muted"])

    def _attempt_login(self):
        # Check lockout
        if self._locked_until:
            remaining = (self._locked_until
                         - time.time())
            if remaining > 0:
                self.status_var.set(
                    f"⚠  Compte verrouillé. Attendez "
                    f"{int(remaining)}s.")
                return
            else:
                self._locked_until = None
                self._attempt = 0

        username = self.username_var.get().strip()
        password = self.pwd_var.get()

        if not username or not password:
            self._shake_form()
            self.status_var.set(
                "⚠  Veuillez remplir tous les champs.")
            return

        # Show loading state
        self.login_btn.config(
            text="  Vérification…",
            state="disabled",
            bg=DS["bg_3"])
        self.update()

        ok, msg = AuthController.login(username, password)

        if ok:
            self._anim_running = False
            self.status_var.set("")
            self._success_animation(msg)
        else:
            self._attempt += 1
            remaining_att = self._max_attempts - self._attempt

            self.login_btn.config(
                text="  Connexion  →",
                state="normal",
                bg=DS["primary"])

            if self._attempt >= self._max_attempts:
                self._locked_until = time.time() + 30
                self.status_var.set(
                    f"⛔  Trop de tentatives. "
                    f"Verrouillé 30 secondes.")
                self._start_lockout_countdown()
            else:
                self.status_var.set(
                    f"✗  {msg}  "
                    f"({remaining_att} tentative(s) restante(s))")
                self._shake_form()

    def _shake_form(self):
        """Horizontal shake animation on error."""
        orig_x = self.winfo_x()
        shake = [8, -8, 6, -6, 4, -4, 2, -2, 0]
        def _do_shake(steps):
            if not steps:
                return
            self.geometry(
                f"+{orig_x + steps[0]}+"
                f"{self.winfo_y()}")
            self.after(25,
                       lambda: _do_shake(steps[1:]))
        _do_shake(shake)

    def _success_animation(self, msg):
        """Flash success state before closing."""
        self.login_btn.config(
            text="  ✓  Accès autorisé",
            bg=DS["success"],
            state="disabled")
        self.status_var.set("")
        self.update()

        if msg == "MUST_CHANGE_PWD":
            self.after(600, self._open_change_pwd)
        else:
            self.after(700, self._finish_login)

    def _finish_login(self):
        self._anim_running = False
        self.grab_release()
        self.destroy()
        self.on_success()

    def _open_change_pwd(self):
        from controllers.auth_controller import AuthSession
        ChangePwdDialog(
            self,
            AuthSession.user()["id"],
            on_done=self._finish_login).grab_set()

    def _start_lockout_countdown(self):
        def _tick():
            if (self._locked_until
                    and time.time() < self._locked_until):
                rem = int(self._locked_until - time.time())
                self.status_var.set(
                    f"⛔  Verrouillé — {rem}s restantes")
                self.login_btn.config(
                    text=f"  Verrouillé ({rem}s)",
                    state="disabled",
                    bg=DS["danger"])
                self.after(1000, _tick)
            else:
                self._locked_until = None
                self._attempt = 0
                self.login_btn.config(
                    text="  Connexion  →",
                    state="normal",
                    bg=DS["primary"])
                self.status_var.set("")
        self.after(1000, _tick)

    # ── Animations ────────────────────────────────────────────────────────────

    def _start_animations(self):
        """Start floating particle animation."""
        import random
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        # Create particles
        for _ in range(28):
            x = random.randint(0, sw)
            y = random.randint(0, sh)
            r = random.uniform(1, 4)
            dx = random.uniform(-0.4, 0.4)
            dy = random.uniform(-0.4, 0.4)
            colors = [DS["primary"],
                      DS["accent"],
                      DS["border_bright"]]
            color = random.choice(colors)
            oid = self.bg_canvas.create_oval(
                x-r, y-r, x+r, y+r,
                fill=color, outline="")
            self._particles.append(
                [oid, x, y, dx, dy, r, sw, sh])

        self._animate_particles()

    def _animate_particles(self):
        if not self._anim_running:
            return
        for p in self._particles:
            oid, x, y, dx, dy, r, sw, sh = p
            x += dx
            y += dy
            # Bounce
            if x < 0 or x > sw:
                dx = -dx
            if y < 0 or y > sh:
                dy = -dy
            p[1], p[2], p[3], p[4] = x, y, dx, dy
            self.bg_canvas.coords(
                oid, x-r, y-r, x+r, y+r)
        self.after(30, self._animate_particles)

    def _on_close(self):
        """Prevent closing without auth."""
        import tkinter.messagebox as mb
        if mb.askokcancel(
                "Quitter EduTrack",
                "Voulez-vous fermer l'application ?",
                parent=self):
            self._anim_running = False
            self.master.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  CHANGE PASSWORD DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class ChangePwdDialog(tk.Toplevel):
    def __init__(self, parent, user_id, on_done=None):
        super().__init__(parent)
        self.user_id = user_id
        self.on_done = on_done
        self.title("Changer le mot de passe")
        self.geometry("440x420")
        self.resizable(False, False)
        self.configure(bg=DS["bg"])
        x = (self.winfo_screenwidth() - 440) // 2
        y = (self.winfo_screenheight() - 420) // 2
        self.geometry(f"440x420+{x}+{y}")
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=DS["card"],
                       highlightbackground=DS["border"],
                       highlightthickness=1,
                       padx=28, pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔐  Changement obligatoire",
                 font=FONTS["h2"], bg=DS["card"],
                 fg=DS["warning"]).pack(anchor="w")
        tk.Label(hdr,
                 text="Votre mot de passe doit être modifié.",
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["text_muted"]).pack(anchor="w", pady=(4,0))

        body = tk.Frame(self, bg=DS["bg"], padx=28, pady=20)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)

        self.vars = {}
        for r, lbl in enumerate([
                "Ancien mot de passe",
                "Nouveau mot de passe",
                "Confirmer le nouveau"]):
            tk.Label(body, text=lbl, font=FONTS["label"],
                     bg=DS["bg"], fg=DS["text_muted"],
                     anchor="w").grid(row=r*2, column=0,
                                      sticky="w", pady=(8,2))
            var = tk.StringVar()
            entry = tk.Entry(
                body, textvariable=var, show="●",
                font=FONTS["body"],
                bg=DS["bg_3"], fg=DS["text_primary"],
                insertbackground=DS["primary"],
                relief="flat", bd=0,
                highlightbackground=DS["border_bright"],
                highlightthickness=1)
            entry.grid(row=r*2+1, column=0,
                       sticky="ew", ipady=7)
            entry.bind("<FocusIn>",
                lambda e, w=entry: w.config(
                    highlightbackground=DS["primary"]))
            entry.bind("<FocusOut>",
                lambda e, w=entry: w.config(
                    highlightbackground=DS["border_bright"]))
            key = ["old", "new", "confirm"][r]
            self.vars[key] = var

        # Rules
        rules = tk.Frame(body, bg=DS["bg"])
        rules.grid(row=7, column=0, sticky="w", pady=(8,0))
        tk.Label(rules, text="Règles : 8+ caractères · majuscule · "
                              "minuscule · chiffre",
                 font=FONTS["caption"],
                 bg=DS["bg"], fg=DS["text_dim"]).pack()

        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["danger"],
                 anchor="w").grid(row=8, column=0,
                                   sticky="w", pady=(8,0))

        footer = tk.Frame(self, bg=DS["card"],
                          highlightbackground=DS["border"],
                          highlightthickness=1,
                          padx=24, pady=14)
        footer.pack(fill="x", side="bottom")

        btn = tk.Button(footer, text="Changer le mot de passe",
                        font=FONTS["btn"],
                        bg=DS["primary"], fg=DS["white"],
                        relief="flat", bd=0, cursor="hand2",
                        padx=16, pady=8,
                        command=self._save)
        btn.pack(side="left")
        btn.bind("<Enter>",
                 lambda e: btn.config(bg=DS["primary_hover"]))
        btn.bind("<Leave>",
                 lambda e: btn.config(bg=DS["primary"]))

    def _save(self):
        old = self.vars["old"].get()
        new = self.vars["new"].get()
        cfm = self.vars["confirm"].get()
        if new != cfm:
            self.msg_var.set("✗  Les mots de passe ne correspondent pas.")
            return
        ok, msg = AuthController.change_password(
            self.user_id, old, new)
        if ok:
            self.destroy()
            if self.on_done:
                self.on_done()
        else:
            self.msg_var.set(f"✗  {msg}")
