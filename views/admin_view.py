"""
EduTrack Admin Panel v3.0 — Dark Corporate Premium
Full user management, permissions, audit log, system settings.
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, confirm_delete, show_toast)
from controllers.auth_controller import (
    AuthController, AuthSession,
    ROLES, ROLE_LABELS, ROLE_COLORS,
    MODULES)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ADMIN VIEW
# ══════════════════════════════════════════════════════════════════════════════

class AdminView(tk.Frame):
    """Master admin panel — users, permissions, audit, settings."""

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=DS["bg"])
        hdr.pack(fill="x", padx=28, pady=(20, 0))

        left = tk.Frame(hdr, bg=DS["bg"])
        left.pack(side="left")
        tk.Label(left, text="Administration",
                 font=FONTS["h1"], bg=DS["bg"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(left,
                 text=f"Connecté en tant que  "
                      f"{AuthSession.get_display_name()}  "
                      f"·  {ROLE_LABELS.get(AuthSession.role(),'?')}",
                 font=FONTS["body_sm"], bg=DS["bg"],
                 fg=DS["text_muted"]).pack(anchor="w")

        tk.Frame(self, bg=DS["border"], height=1).pack(
            fill="x", padx=28, pady=14)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True,
                padx=28, pady=(0, 20))

        # ── Tab 1: Users ──────────────────────────────────────────────────────
        t_users = tk.Frame(nb, bg=DS["bg"])
        nb.add(t_users, text="  ◈  Utilisateurs  ")
        UsersTab(t_users).pack(fill="both", expand=True)

        # ── Tab 2: Permissions ────────────────────────────────────────────────
        if AuthSession.is_superadmin():
            t_perms = tk.Frame(nb, bg=DS["bg"])
            nb.add(t_perms, text="  ◉  Permissions  ")
            PermissionsTab(t_perms).pack(fill="both", expand=True)

        # ── Tab 3: Audit Log ──────────────────────────────────────────────────
        t_audit = tk.Frame(nb, bg=DS["bg"])
        nb.add(t_audit, text="  ◎  Journal d'audit  ")
        AuditTab(t_audit).pack(fill="both", expand=True)

        # ── Tab 4: Settings ───────────────────────────────────────────────────
        if AuthSession.is_superadmin():
            t_settings = tk.Frame(nb, bg=DS["bg"])
            nb.add(t_settings, text="  ⊞  Paramètres  ")
            SettingsTab(t_settings).pack(fill="both", expand=True)

        # ── Tab 5: My Profile ─────────────────────────────────────────────────
        t_profile = tk.Frame(nb, bg=DS["bg"])
        nb.add(t_profile, text="  ◆  Mon Profil  ")
        ProfileTab(t_profile).pack(fill="both", expand=True)


# ══════════════════════════════════════════════════════════════════════════════
#  USERS TAB
# ══════════════════════════════════════════════════════════════════════════════

class UsersTab(tk.Frame):

    COLS    = ["id","username","full_name","role","email",
               "is_active","last_login","created_at"]
    HEADERS = ["ID","Identifiant","Nom complet","Rôle",
               "Email","Actif","Dernière connexion","Créé le"]
    WIDTHS  = [40,120,160,110,190,60,160,140]

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._data = []
        self._build()
        self._load()

    def _build(self):
        # Stats row
        self.stats_frame = tk.Frame(self, bg=DS["bg"])
        self.stats_frame.pack(fill="x", pady=(16,0))
        self._stats_row()

        tk.Frame(self, bg=DS["border"], height=1).pack(
            fill="x", pady=12)

        # Toolbar
        toolbar = tk.Frame(self, bg=DS["bg"])
        toolbar.pack(fill="x", pady=(0,10))

        self.search = PremiumSearchBar(
            toolbar,
            "Rechercher utilisateur…",
            on_change=self._on_search,
            bg=DS["bg"])
        self.search.pack(side="left", fill="x",
                         expand=True, padx=(0,12))

        tk.Label(toolbar, text="Rôle",
                 font=FONTS["body_sm"],
                 bg=DS["bg"],
                 fg=DS["text_muted"]).pack(side="left")
        self.role_filter = tk.StringVar(value="Tous")
        ttk.Combobox(
            toolbar,
            textvariable=self.role_filter,
            values=["Tous"] + [r[0] for r in ROLES],
            width=14, state="readonly").pack(
                side="left", padx=(4,12))
        self.role_filter.trace_add(
            "write", lambda *a: self._on_search(""))

        if AuthSession.is_admin_or_above():
            UIComponents.btn_primary(
                toolbar, "＋  Nouvel utilisateur",
                command=self._open_add).pack(side="left",
                                              padx=(0,8))

        # Table
        container = tk.Frame(self, bg=DS["bg"])
        container.pack(fill="both", expand=True)
        tbl, self.tree = make_premium_table(
            container, self.COLS,
            self.WIDTHS, self.HEADERS)
        tbl.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>",
                       lambda e: self._open_edit())
        self.tree.bind("<Button-3>", self._ctx_menu)

        # Actions bar
        acts = tk.Frame(self, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1,
                        padx=20, pady=8)
        acts.pack(fill="x", pady=(8,0))

        if AuthSession.is_admin_or_above():
            UIComponents.btn_secondary(
                acts, "✏️  Modifier",
                command=self._open_edit).pack(
                    side="left", padx=(0,8))
            UIComponents.btn_secondary(
                acts, "🔑  Réinitialiser MdP",
                command=self._reset_pwd).pack(
                    side="left", padx=(0,8))
            UIComponents.btn_secondary(
                acts, "⊙  Activer / Désactiver",
                command=self._toggle).pack(
                    side="left", padx=(0,8))
        if AuthSession.is_superadmin():
            UIComponents.btn_danger(
                acts, "🗑  Supprimer",
                command=self._delete).pack(side="left")

        tk.Label(acts, text="Double-clic pour modifier",
                 font=FONTS["caption"], bg=DS["card"],
                 fg=DS["text_dim"]).pack(side="right")

    def _stats_row(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        try:
            stats = AuthController.get_user_stats()
        except Exception:
            return

        items = [
            ("◈", stats["total"],    "Total",    DS["primary"]),
            ("●", stats["active"],   "Actifs",   DS["success"]),
            ("○", stats["inactive"], "Inactifs", DS["danger"]),
        ]
        for r in stats.get("by_role", []):
            color = ROLE_COLORS.get(r["role"], DS["text_muted"])
            items.append(
                ("◆", r["n"],
                 ROLE_LABELS.get(r["role"], r["role"]),
                 color))

        for i, (icon, val, label, color) in enumerate(items):
            UIComponents.kpi_card(
                self.stats_frame, icon, val,
                label, color=color, col=i)
            self.stats_frame.grid_columnconfigure(
                i, weight=1, uniform="u")

    def _load(self, data=None):
        try:
            self._data = (data if data is not None
                          else AuthController.get_users())
            self._render(self._data)
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _render(self, rows):
        fill_premium_table(self.tree, rows, self.COLS)
        # Color rows by role
        for i, item in enumerate(
                self.tree.get_children()):
            vals  = self.tree.item(item)["values"]
            role  = str(vals[3]) if len(vals) > 3 else ""
            color = ROLE_COLORS.get(role, DS["text_muted"])
            active = str(vals[5])
            bg = DS["row_even"] if i % 2 == 0 else DS["row_odd"]
            if active in ("0", "False", "Inactif"):
                bg = DS["danger_light"]
            self.tree.item(item,
                           tags=(f"role_{role}",))
            self.tree.tag_configure(
                f"role_{role}",
                foreground=color,
                background=bg)

    def _on_search(self, terme=""):
        terme  = self.search.get().lower()
        role_f = self.role_filter.get()
        result = [
            u for u in self._data
            if (terme in str(u.get("username","")).lower()
                or terme in str(u.get("full_name","")).lower()
                or terme in str(u.get("email","")).lower())
            and (role_f == "Tous"
                 or u.get("role","") == role_f)
        ]
        self._render(result)

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            show_message(self, "Sélection",
                         "Sélectionnez un utilisateur.",
                         "warning")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _open_add(self):
        UserForm(self, on_save=lambda: (
            self._load(), self._stats_row()
        )).grab_set()

    def _open_edit(self):
        uid = self._get_id()
        if not uid: return
        user = AuthController.get_user(uid)
        if user:
            UserForm(
                self, user=user,
                on_save=lambda: (
                    self._load(),
                    self._stats_row()
                )).grab_set()

    def _reset_pwd(self):
        uid = self._get_id()
        if not uid: return
        ResetPwdDialog(self, uid,
                       on_done=self._load).grab_set()

    def _toggle(self):
        uid = self._get_id()
        if not uid: return
        new_state = AuthController.toggle_user(uid)
        state_str = "activé" if new_state else "désactivé"
        show_toast(self, f"Utilisateur {state_str}.",
                   "success" if new_state else "warning")
        self._load()
        self._stats_row()

    def _delete(self):
        uid = self._get_id()
        if not uid: return
        sel  = self.tree.selection()
        name = self.tree.item(sel[0])["values"][1]
        if confirm_delete(self, name):
            ok, msg = AuthController.delete_user(uid)
            if ok:
                show_toast(self, "Utilisateur supprimé.",
                           "success")
                self._load()
                self._stats_row()
            else:
                show_message(self, "Erreur", msg, "error")

    def _ctx_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid: return
        self.tree.selection_set(iid)
        menu = tk.Menu(self, tearoff=0,
                       font=FONTS["body"],
                       bg=DS["card"],
                       fg=DS["text_primary"])
        menu.add_command(
            label="  ✏️  Modifier",
            command=self._open_edit)
        menu.add_command(
            label="  🔑  Réinitialiser MdP",
            command=self._reset_pwd)
        menu.add_command(
            label="  ⊙  Activer/Désactiver",
            command=self._toggle)
        if AuthSession.is_superadmin():
            menu.add_separator()
            menu.add_command(
                label="  🗑  Supprimer",
                command=self._delete)
        menu.tk_popup(event.x_root, event.y_root)


# ══════════════════════════════════════════════════════════════════════════════
#  USER FORM
# ══════════════════════════════════════════════════════════════════════════════

class UserForm(tk.Toplevel):

    AVATAR_COLORS = [
        "#3B82F6","#EF4444","#10B981","#F59E0B",
        "#A855F7","#06B6D4","#F97316","#EC4899",
    ]

    def __init__(self, parent, user=None, on_save=None):
        super().__init__(parent)
        self.user    = user
        self.on_save = on_save
        mode = "Modifier" if user else "Nouvel utilisateur"
        self.title(mode)
        self.geometry("580x560")
        self.resizable(False, False)
        self.configure(bg=DS["bg"])
        x = (self.winfo_screenwidth()-580)//2
        y = (self.winfo_screenheight()-560)//2
        self.geometry(f"580x560+{x}+{y}")
        self._build(mode)

    def _build(self, mode):
        # Header
        hdr = tk.Frame(self, bg=DS["dark"] if hasattr(DS,"dark") else "#0F172A",
                       padx=24, pady=18)
        hdr.configure(bg="#0F172A")
        hdr.pack(fill="x")
        tk.Label(hdr, text=mode, font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(anchor="w")
        sub = (self.user["username"] if self.user
               else "Créer un nouvel accès")
        tk.Label(hdr, text=sub, font=FONTS["body_sm"],
                 bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2,0))

        body = tk.Frame(self, bg=DS["bg"],
                        padx=24, pady=20)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        u = self.user or {}
        left  = tk.Frame(body, bg=DS["bg"])
        right = tk.Frame(body, bg=DS["bg"])
        left.grid(row=0, column=0,
                  sticky="n", padx=(0,16))
        right.grid(row=0, column=1, sticky="n")
        left.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.vars = {}

        def inp(parent, label, key, row,
                required=False, show=None):
            tk.Label(parent, text=label
                     + (" *" if required else ""),
                     font=FONTS["label"],
                     bg=DS["bg"],
                     fg=DS["text_muted"],
                     anchor="w").grid(
                row=row, column=0,
                sticky="w", pady=(8,2))
            var = tk.StringVar(
                value=str(u.get(key,"")))
            e = tk.Entry(parent,
                         textvariable=var,
                         font=FONTS["body"],
                         bg=DS["bg_3"],
                         fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="flat", bd=0,
                         highlightbackground=DS["border_bright"],
                         highlightthickness=1,
                         show=show or "")
            e.grid(row=row+1, column=0,
                   sticky="ew", ipady=7,
                   pady=(0,4))
            e.bind("<FocusIn>",
                lambda ev, w=e: w.config(
                    highlightbackground=DS["primary"]))
            e.bind("<FocusOut>",
                lambda ev, w=e: w.config(
                    highlightbackground=DS["border_bright"]))
            self.vars[key] = var
            return var

        inp(left, "Identifiant *", "username", 0, required=True)
        inp(left, "Nom complet *",  "full_name", 2, required=True)
        inp(left, "Email",          "email",     4)

        if not self.user:
            inp(left, "Mot de passe *", "_pwd", 6,
                required=True, show="●")

        # Role
        tk.Label(right, text="Rôle *",
                 font=FONTS["label"],
                 bg=DS["bg"], fg=DS["text_muted"],
                 anchor="w").grid(
            row=0, column=0, sticky="w", pady=(8,2))
        self.role_var = tk.StringVar(
            value=u.get("role","viewer"))

        role_f = tk.Frame(right, bg=DS["bg"])
        role_f.grid(row=1, column=0,
                    sticky="ew", pady=(0,16))

        role_labels  = [r[0] for r in ROLES]
        visible_roles = (role_labels
                         if AuthSession.is_superadmin()
                         else role_labels[1:])
        cb = ttk.Combobox(role_f,
                          textvariable=self.role_var,
                          values=visible_roles,
                          width=22, state="readonly")
        cb.pack(side="left")

        # Role color preview
        self.role_color_lbl = tk.Label(
            role_f, text="  ●  ",
            font=("Segoe UI", 16),
            bg=DS["bg"],
            fg=ROLE_COLORS.get(
                self.role_var.get(), DS["primary"]))
        self.role_color_lbl.pack(side="left", padx=(8,0))
        self.role_var.trace_add("write",
            lambda *a: self.role_color_lbl.config(
                fg=ROLE_COLORS.get(
                    self.role_var.get(),
                    DS["primary"])))

        # Active status
        tk.Label(right, text="Statut",
                 font=FONTS["label"],
                 bg=DS["bg"], fg=DS["text_muted"],
                 anchor="w").grid(
            row=2, column=0, sticky="w", pady=(8,2))
        self.active_var = tk.BooleanVar(
            value=bool(u.get("is_active", 1)))
        act_f = tk.Frame(right, bg=DS["bg"])
        act_f.grid(row=3, column=0,
                   sticky="w", pady=(0,16))
        for label, val in [("Actif",True),
                            ("Inactif",False)]:
            tk.Radiobutton(
                act_f, text=label,
                variable=self.active_var,
                value=val,
                font=FONTS["body"],
                bg=DS["bg"],
                fg=DS["text_primary"],
                selectcolor=DS["bg_3"],
                activebackground=DS["bg"],
                relief="flat").pack(
                    side="left", padx=(0,16))

        # Avatar color
        tk.Label(right, text="Couleur avatar",
                 font=FONTS["label"],
                 bg=DS["bg"], fg=DS["text_muted"],
                 anchor="w").grid(
            row=4, column=0, sticky="w", pady=(8,2))

        self.avatar_color = u.get(
            "avatar_color", "#3B82F6")
        color_row = tk.Frame(right, bg=DS["bg"])
        color_row.grid(row=5, column=0,
                       sticky="w", pady=(0,8))

        self._color_btns = {}
        for i, c in enumerate(self.AVATAR_COLORS):
            cb2 = tk.Label(
                color_row,
                text="●",
                font=("Segoe UI", 18),
                bg=DS["bg"], fg=c,
                cursor="hand2")
            cb2.grid(row=0, column=i, padx=2)
            cb2.bind("<Button-1>",
                     lambda e, col=c: self._pick_color(col))
            self._color_btns[c] = cb2
        self._highlight_color(self.avatar_color)

        # Validation message
        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["danger"],
                 anchor="w").grid(
            row=1, column=0,
            columnspan=2, sticky="w", pady=(8,0))

        # Footer
        footer = tk.Frame(
            self, bg=DS["card"],
            highlightbackground=DS["border"],
            highlightthickness=1,
            padx=20, pady=12)
        footer.pack(fill="x", side="bottom")
        UIComponents.btn_primary(
            footer, "💾  Enregistrer",
            command=self._save).pack(side="left")
        UIComponents.btn_secondary(
            footer, "Annuler",
            command=self.destroy).pack(
                side="left", padx=(8,0))

    def _pick_color(self, color):
        self.avatar_color = color
        self._highlight_color(color)

    def _highlight_color(self, selected):
        for c, lbl in self._color_btns.items():
            lbl.config(
                font=("Segoe UI",
                      22 if c == selected else 18))

    def _save(self):
        data = {k: v.get().strip()
                for k, v in self.vars.items()}
        role   = self.role_var.get()
        active = int(self.active_var.get())
        color  = self.avatar_color

        if not data.get("username"):
            self.msg_var.set("✗  Identifiant requis.")
            return
        if not data.get("full_name"):
            self.msg_var.set("✗  Nom complet requis.")
            return

        try:
            if self.user:
                ok, msg = AuthController.update_user(
                    self.user["id"],
                    full_name=data["full_name"],
                    email=data.get("email",""),
                    role=role,
                    is_active=active,
                    avatar_color=color)
            else:
                pwd = data.pop("_pwd","")
                ok, msg = AuthController.create_user(
                    username=data["username"],
                    password=pwd,
                    role=role,
                    full_name=data["full_name"],
                    email=data.get("email",""),
                    avatar_color=color)

            if ok:
                show_toast(self.master, msg, "success")
                if self.on_save:
                    self.on_save()
                self.destroy()
            else:
                self.msg_var.set(f"✗  {msg}")
        except Exception as e:
            self.msg_var.set(f"✗  Erreur: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  RESET PASSWORD DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class ResetPwdDialog(tk.Toplevel):
    def __init__(self, parent, user_id, on_done=None):
        super().__init__(parent)
        self.user_id = user_id
        self.on_done = on_done
        self.title("Réinitialiser le mot de passe")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(bg=DS["bg"])
        x = (self.winfo_screenwidth()-400)//2
        y = (self.winfo_screenheight()-300)//2
        self.geometry(f"400x300+{x}+{y}")
        self._build()

    def _build(self):
        user = AuthController.get_user(self.user_id)
        name = user["full_name"] if user else "?"

        hdr = tk.Frame(self, bg="#0F172A",
                       padx=24, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔑  Réinitialiser MdP",
                 font=FONTS["h2"],
                 bg="#0F172A",
                 fg=DS["warning"]).pack(anchor="w")
        tk.Label(hdr, text=name,
                 font=FONTS["body_sm"],
                 bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w")

        body = tk.Frame(self, bg=DS["bg"],
                        padx=24, pady=20)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)

        tk.Label(body, text="Nouveau mot de passe *",
                 font=FONTS["label"],
                 bg=DS["bg"], fg=DS["text_muted"],
                 anchor="w").grid(
            row=0, column=0, sticky="w", pady=(0,4))
        self.pwd_var = tk.StringVar()
        e = tk.Entry(body, textvariable=self.pwd_var,
                     show="●", font=FONTS["body"],
                     bg=DS["bg_3"],
                     fg=DS["text_primary"],
                     insertbackground=DS["primary"],
                     relief="flat", bd=0,
                     highlightbackground=DS["border_bright"],
                     highlightthickness=1)
        e.grid(row=1, column=0,
               sticky="ew", ipady=8,
               pady=(0,6))

        tk.Label(body,
                 text="L'utilisateur devra changer son MdP "
                      "à la prochaine connexion.",
                 font=FONTS["caption"],
                 bg=DS["bg"], fg=DS["text_dim"],
                 wraplength=330, justify="left").grid(
            row=2, column=0, sticky="w")

        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["danger"]).grid(
            row=3, column=0, sticky="w", pady=(8,0))

        footer = tk.Frame(
            self, bg=DS["card"],
            highlightbackground=DS["border"],
            highlightthickness=1,
            padx=20, pady=12)
        footer.pack(fill="x", side="bottom")
        UIComponents.btn_primary(
            footer, "Réinitialiser",
            command=self._save).pack(side="left")
        UIComponents.btn_secondary(
            footer, "Annuler",
            command=self.destroy).pack(
                side="left", padx=(8,0))

    def _save(self):
        pwd = self.pwd_var.get()
        if not pwd:
            self.msg_var.set("✗  Entrez un mot de passe.")
            return
        ok, msg = AuthController.reset_password(
            self.user_id, pwd)
        if ok:
            show_toast(self.master, msg, "success")
            if self.on_done:
                self.on_done()
            self.destroy()
        else:
            self.msg_var.set(f"✗  {msg}")


# ══════════════════════════════════════════════════════════════════════════════
#  PERMISSIONS TAB
# ══════════════════════════════════════════════════════════════════════════════

class PermissionsTab(tk.Frame):

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._vars = {}
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=DS["bg"])
        hdr.pack(fill="x", pady=(16,8))
        tk.Label(hdr,
                 text="Matrice des permissions par rôle",
                 font=FONTS["h3"], bg=DS["bg"],
                 fg=DS["text_primary"]).pack(side="left")
        UIComponents.btn_primary(
            hdr, "💾  Sauvegarder",
            command=self._save).pack(side="right")

        tk.Frame(self, bg=DS["border"],
                 height=1).pack(fill="x", pady=(0,12))

        # Scrollable grid
        canvas = tk.Canvas(self, bg=DS["bg"],
                           highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical",
                             command=canvas.yview)
        sf = tk.Frame(canvas, bg=DS["bg"])
        sf.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        roles_to_show = [
            r for r in ROLES if r[0] != "superadmin"]

        # Column headers: roles
        tk.Label(sf, text="Module",
                 font=FONTS["h4"], bg=DS["bg"],
                 fg=DS["text_secondary"],
                 width=16, anchor="w").grid(
            row=0, column=0,
            padx=(16,8), pady=8)

        for c, (role, label, color) in enumerate(
                roles_to_show, 1):
            hf = tk.Frame(sf, bg=DS["bg"])
            hf.grid(row=0, column=c,
                    padx=4, pady=8, sticky="n")
            tk.Label(hf, text="●",
                     font=("Segoe UI",12),
                     bg=DS["bg"], fg=color).pack()
            tk.Label(hf, text=label,
                     font=FONTS["body_sm"],
                     bg=DS["bg"],
                     fg=DS["text_secondary"]).pack()
            # Sub-headers
            sub_f = tk.Frame(hf, bg=DS["bg"])
            sub_f.pack()
            for sub in ["R","W","D"]:
                tk.Label(sub_f, text=sub,
                         font=FONTS["caption"],
                         bg=DS["bg"],
                         fg=DS["text_dim"],
                         width=3).pack(side="left")

        # Row separator
        tk.Frame(sf, bg=DS["border"],
                 height=1).grid(
            row=1, column=0,
            columnspan=len(roles_to_show)+1,
            sticky="ew", padx=16)

        # Load current permissions
        perms_raw = AuthController.get_all_permissions()
        perm_map  = {}
        for p in perms_raw:
            key = (p["role"], p["module"])
            perm_map[key] = p

        # Permission rows
        for r, module in enumerate(MODULES, 2):
            bg_row = DS["card"] if r % 2 == 0 else DS["bg"]
            tk.Label(sf, text=module.capitalize(),
                     font=FONTS["body"],
                     bg=bg_row,
                     fg=DS["text_primary"],
                     width=16, anchor="w",
                     padx=16).grid(
                row=r, column=0,
                padx=(0,8), pady=4,
                sticky="ew")

            for c, (role, _, _) in enumerate(
                    roles_to_show, 1):
                p = perm_map.get((role, module), {})
                cell = tk.Frame(sf, bg=bg_row)
                cell.grid(row=r, column=c,
                          padx=4, pady=4)

                for action, default in [
                    ("can_read",   p.get("can_read",0)),
                    ("can_write",  p.get("can_write",0)),
                    ("can_delete", p.get("can_delete",0)),
                ]:
                    var = tk.IntVar(value=int(default or 0))
                    key = f"{role}_{module}_{action}"
                    self._vars[key] = var
                    color_map = {
                        "can_read":   DS["success"],
                        "can_write":  DS["warning"],
                        "can_delete": DS["danger"],
                    }
                    cb = tk.Checkbutton(
                        cell,
                        variable=var,
                        bg=bg_row,
                        activebackground=bg_row,
                        selectcolor=DS["bg_3"],
                        cursor="hand2",
                        relief="flat")
                    cb.pack(side="left")

    def _save(self):
        # Group vars by (role, module)
        groups = {}
        for key, var in self._vars.items():
            parts  = key.split("_", 2)
            # key = role_module_can_action
            # Need smarter split since role has no _
            pass

        # Rebuild from scratch using clean key format
        from collections import defaultdict
        data = defaultdict(dict)
        for key, var in self._vars.items():
            # format: {role}_{module}_{can_read|can_write|can_delete}
            for role, rl, _ in ROLES:
                if role == "superadmin":
                    continue
                for mod in MODULES:
                    for act in ["can_read","can_write","can_delete"]:
                        k = f"{role}_{mod}_{act}"
                        if k in self._vars:
                            data[(role,mod)][act] = \
                                self._vars[k].get()

        for (role, module), acts in data.items():
            AuthController.update_permission(
                role, module,
                acts.get("can_read",0),
                acts.get("can_write",0),
                acts.get("can_delete",0))
        show_toast(self.master,
                   "Permissions sauvegardées.", "success")


# ══════════════════════════════════════════════════════════════════════════════
#  AUDIT LOG TAB
# ══════════════════════════════════════════════════════════════════════════════

class AuditTab(tk.Frame):

    COLS    = ["id","created_at","username","action",
               "entity","entity_id","detail"]
    HEADERS = ["ID","Date / Heure","Utilisateur","Action",
               "Entité","ID Entité","Détail"]
    WIDTHS  = [50,150,120,160,100,70,300]

    ACTION_COLORS = {
        "LOGIN_SUCCESS":    DS["success"] if "success" in dir() else "#10B981",
        "LOGIN_FAILED":     "#EF4444",
        "LOGOUT":           "#94A3B8",
        "USER_CREATED":     "#3B82F6",
        "USER_UPDATED":     "#F59E0B",
        "USER_DELETED":     "#EF4444",
        "PASSWORD_CHANGED": "#A855F7",
        "PASSWORD_RESET":   "#F97316",
        "USER_ACTIVATED":   "#10B981",
        "USER_DEACTIVATED": "#EF4444",
    }

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._data = []
        self._build()
        self._load()

    def _build(self):
        toolbar = tk.Frame(self, bg=DS["bg"])
        toolbar.pack(fill="x", pady=(16,10))

        self.search = PremiumSearchBar(
            toolbar,
            "Filtrer par utilisateur, action…",
            on_change=self._on_filter,
            bg=DS["bg"])
        self.search.pack(side="left", fill="x",
                         expand=True, padx=(0,12))

        tk.Label(toolbar, text="Action",
                 font=FONTS["body_sm"],
                 bg=DS["bg"],
                 fg=DS["text_muted"]).pack(side="left")
        self.action_var = tk.StringVar(value="Toutes")
        actions = ["Toutes"] + list(
            self.ACTION_COLORS.keys())
        ttk.Combobox(
            toolbar,
            textvariable=self.action_var,
            values=actions,
            width=18,
            state="readonly").pack(
                side="left", padx=(4,12))
        self.action_var.trace_add(
            "write", lambda *a: self._on_filter(""))

        UIComponents.btn_secondary(
            toolbar, "↺  Actualiser",
            command=self._load).pack(side="left",
                                      padx=(0,8))

        container = tk.Frame(self, bg=DS["bg"])
        container.pack(fill="both", expand=True)

        tbl, self.tree = make_premium_table(
            container, self.COLS,
            self.WIDTHS, self.HEADERS)
        tbl.pack(fill="both", expand=True)

        # Count label
        self.count_lbl = tk.Label(
            self, text="",
            font=FONTS["body_sm"], bg=DS["bg"],
            fg=DS["text_muted"], anchor="w")
        self.count_lbl.pack(fill="x", pady=(4,0))

    def _load(self):
        try:
            self._data = AuthController.get_audit_log(500)
            self._render(self._data)
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _render(self, rows):
        fill_premium_table(self.tree, rows, self.COLS)
        for item in self.tree.get_children():
            vals   = self.tree.item(item)["values"]
            action = str(vals[3]) if len(vals) > 3 else ""
            color  = self.ACTION_COLORS.get(
                action, DS["text_muted"])
            self.tree.item(
                item,
                tags=(f"act_{action}",))
            self.tree.tag_configure(
                f"act_{action}",
                foreground=color)
        self.count_lbl.config(
            text=f"{len(rows)} entrée(s)")

    def _on_filter(self, terme=""):
        terme  = self.search.get().lower()
        action = self.action_var.get()
        result = [
            r for r in self._data
            if (terme in str(r.get("username","")).lower()
                or terme in str(r.get("action","")).lower()
                or terme in str(r.get("detail","")).lower())
            and (action == "Toutes"
                 or r.get("action","") == action)
        ]
        self._render(result)


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS TAB
# ══════════════════════════════════════════════════════════════════════════════

class SettingsTab(tk.Frame):

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._vars = {}
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=DS["bg"])
        hdr.pack(fill="x", pady=(16,12))
        tk.Label(hdr, text="Paramètres Système",
                 font=FONTS["h3"], bg=DS["bg"],
                 fg=DS["text_primary"]).pack(side="left")
        UIComponents.btn_primary(
            hdr, "💾  Enregistrer",
            command=self._save).pack(side="right")

        tk.Frame(self, bg=DS["border"],
                 height=1).pack(fill="x", pady=(0,16))

        # Settings grid
        try:
            settings = AuthController.get_settings()
        except Exception as e:
            tk.Label(self, text=f"Erreur : {e}",
                     font=FONTS["body"], bg=DS["bg"],
                     fg=DS["danger"]).pack(pady=20)
            return

        card = tk.Frame(self, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        card.pack(fill="x", padx=0)
        tk.Frame(card, bg=DS["primary"],
                 height=2).pack(fill="x")

        inner = tk.Frame(card, bg=DS["card"],
                         padx=28, pady=24)
        inner.pack(fill="x")
        inner.grid_columnconfigure(1, weight=1)

        for r, (key, setting) in enumerate(
                settings.items()):
            label = setting.get("label", key)
            value = setting.get("value", "")
            stype = setting.get("type", "text")

            tk.Label(inner, text=label + ":",
                     font=FONTS["body"],
                     bg=DS["card"],
                     fg=DS["text_secondary"],
                     anchor="w",
                     width=22).grid(
                row=r, column=0,
                sticky="w", pady=8, padx=(0,16))

            var = tk.StringVar(value=str(value or ""))
            self._vars[key] = var

            e = tk.Entry(inner, textvariable=var,
                         font=FONTS["body"],
                         bg=DS["bg_3"],
                         fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="flat", bd=0,
                         highlightbackground=DS["border_bright"],
                         highlightthickness=1,
                         width=36)
            e.grid(row=r, column=1,
                   sticky="ew", ipady=6, pady=8)
            e.bind("<FocusIn>",
                lambda ev, w=e: w.config(
                    highlightbackground=DS["primary"]))
            e.bind("<FocusOut>",
                lambda ev, w=e: w.config(
                    highlightbackground=DS["border_bright"]))

        # Danger zone
        tk.Frame(self, bg=DS["border"],
                 height=1).pack(fill="x", pady=16)

        danger = tk.Frame(
            self, bg=DS["danger_light"],
            highlightbackground=DS["danger"],
            highlightthickness=1)
        danger.pack(fill="x")
        d_inner = tk.Frame(danger,
                           bg=DS["danger_light"],
                           padx=20, pady=14)
        d_inner.pack(fill="x")
        tk.Label(d_inner, text="⚠  Zone dangereuse",
                 font=FONTS["h4"],
                 bg=DS["danger_light"],
                 fg=DS["danger"]).pack(anchor="w")
        tk.Label(d_inner,
                 text="Ces actions sont irréversibles.",
                 font=FONTS["body_sm"],
                 bg=DS["danger_light"],
                 fg=DS["text_muted"]).pack(anchor="w",
                                            pady=(2,10))
        UIComponents.btn_danger(
            d_inner, "🗑  Vider le journal d'audit",
            command=self._clear_audit).pack(side="left")

    def _save(self):
        for key, var in self._vars.items():
            AuthController.set_setting(key, var.get())
        show_toast(self.master,
                   "Paramètres enregistrés.", "success")

    def _clear_audit(self):
        from tkinter import messagebox
        if messagebox.askyesno(
                "Confirmation",
                "Vider intégralement le journal d'audit ?\n"
                "Cette action est irréversible.",
                icon="warning"):
            try:
                from database.db_connection import execute_query
                execute_query("DELETE FROM audit_log")
                show_toast(self.master,
                           "Journal vidé.", "success")
            except Exception as e:
                show_message(self, "Erreur",
                             str(e), "error")


# ══════════════════════════════════════════════════════════════════════════════
#  PROFILE TAB
# ══════════════════════════════════════════════════════════════════════════════

class ProfileTab(tk.Frame):

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._build()

    def _build(self):
        u = AuthSession.user()
        if not u:
            return

        # Profile card
        card = tk.Frame(self, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        card.pack(fill="x", padx=0,
                  pady=(16,0))
        # Top accent
        color = ROLE_COLORS.get(
            u.get("role",""), DS["primary"])
        tk.Frame(card, bg=color,
                 height=3).pack(fill="x")

        inner = tk.Frame(card, bg=DS["card"],
                         padx=32, pady=24)
        inner.pack(fill="x")

        # Avatar circle
        av_canvas = tk.Canvas(
            inner, width=72, height=72,
            bg=DS["card"], highlightthickness=0)
        av_canvas.pack(side="left")
        av_canvas.create_oval(
            2, 2, 70, 70,
            fill=u.get("avatar_color", DS["primary"]),
            outline="")
        initials = "".join(
            p[0].upper()
            for p in u.get("full_name","?").split()[:2])
        av_canvas.create_text(
            36, 36, text=initials,
            font=("Segoe UI", 22, "bold"),
            fill=DS["white"])

        # User info
        info = tk.Frame(inner, bg=DS["card"],
                        padx=20)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info,
                 text=u.get("full_name",""),
                 font=FONTS["h2"],
                 bg=DS["card"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(info,
                 text=f"@{u.get('username','')}",
                 font=FONTS["body"],
                 bg=DS["card"],
                 fg=DS["text_secondary"]).pack(anchor="w")

        role_lbl = tk.Label(
            info,
            text=f"  {ROLE_LABELS.get(u.get('role',''), u.get('role',''))}  ",
            font=FONTS["badge"],
            bg=color,
            fg=DS["white"])
        role_lbl.pack(anchor="w",
                      pady=(4,0))

        # Session info
        sess = tk.Frame(inner, bg=DS["card"],
                        padx=0)
        sess.pack(side="right", anchor="n")
        for label, val in [
            ("Email",       u.get("email","—")),
            ("Dernière conn.",u.get("last_login","—")),
            ("Session",     AuthSession.session_duration()),
            ("Compte créé", u.get("created_at","")[:10]
                            if u.get("created_at") else "—"),
        ]:
            r = tk.Frame(sess, bg=DS["card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=label+":",
                     font=FONTS["body_sm"],
                     bg=DS["card"],
                     fg=DS["text_muted"],
                     width=16, anchor="w").pack(side="left")
            tk.Label(r, text=str(val or "—"),
                     font=FONTS["body"],
                     bg=DS["card"],
                     fg=DS["text_primary"]).pack(side="left")

        # Change password section
        tk.Frame(self, bg=DS["border"],
                 height=1).pack(fill="x", pady=20)

        pwd_card = tk.Frame(
            self, bg=DS["card"],
            highlightbackground=DS["border_bright"],
            highlightthickness=1)
        pwd_card.pack(fill="x")
        tk.Frame(pwd_card, bg=DS["purple"],
                 height=2).pack(fill="x")

        pwd_inner = tk.Frame(pwd_card, bg=DS["card"],
                             padx=32, pady=20)
        pwd_inner.pack(fill="x")
        pwd_inner.grid_columnconfigure(1, weight=1)

        tk.Label(pwd_inner,
                 text="🔐  Changer mon mot de passe",
                 font=FONTS["h3"], bg=DS["card"],
                 fg=DS["text_primary"]).grid(
            row=0, column=0, columnspan=2,
            sticky="w", pady=(0,16))

        self._pvars = {}
        for r, (lbl, key) in enumerate([
            ("Mot de passe actuel", "old"),
            ("Nouveau mot de passe","new"),
            ("Confirmer",           "cfm"),
        ]):
            tk.Label(pwd_inner, text=lbl,
                     font=FONTS["label"],
                     bg=DS["card"],
                     fg=DS["text_muted"],
                     width=22, anchor="w").grid(
                row=r+1, column=0,
                sticky="w", pady=(8,2), padx=(0,16))
            var = tk.StringVar()
            e = tk.Entry(pwd_inner, textvariable=var,
                         show="●", font=FONTS["body"],
                         bg=DS["bg_3"],
                         fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="flat", bd=0,
                         highlightbackground=DS["border_bright"],
                         highlightthickness=1)
            e.grid(row=r+1, column=1,
                   sticky="ew", ipady=7,
                   pady=(8,2))
            e.bind("<FocusIn>",
                lambda ev, w=e: w.config(
                    highlightbackground=DS["primary"]))
            e.bind("<FocusOut>",
                lambda ev, w=e: w.config(
                    highlightbackground=DS["border_bright"]))
            self._pvars[key] = var

        self.pwd_msg = tk.StringVar()
        tk.Label(pwd_inner,
                 textvariable=self.pwd_msg,
                 font=FONTS["body_sm"],
                 bg=DS["card"],
                 fg=DS["danger"],
                 anchor="w").grid(
            row=5, column=0,
            columnspan=2, sticky="w", pady=(8,0))

        UIComponents.btn_primary(
            pwd_inner, "Changer le mot de passe",
            command=self._change_pwd).grid(
            row=6, column=0,
            columnspan=2, sticky="w",
            pady=(16,0))

    def _change_pwd(self):
        old = self._pvars["old"].get()
        new = self._pvars["new"].get()
        cfm = self._pvars["cfm"].get()
        if new != cfm:
            self.pwd_msg.set(
                "✗  Les mots de passe ne correspondent pas.")
            return
        uid = AuthSession.user().get("id")
        ok, msg = AuthController.change_password(
            uid, old, new)
        if ok:
            self.pwd_msg.set("")
            for v in self._pvars.values():
                v.set("")
            show_toast(self.master, msg, "success")
        else:
            self.pwd_msg.set(f"✗  {msg}")
