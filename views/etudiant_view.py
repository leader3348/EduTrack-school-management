"""
EduTrack — Vue Étudiants v3.1 (Windows-compatible forms)
"""

import tkinter as tk
from tkinter import ttk
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, confirm_delete, show_toast)
from controllers import EtudiantController

COLS    = ["id","matricule","nom","prenom","filiere","niveau","email","telephone"]
HEADERS = ["ID","Matricule","Nom","Prénom","Filière","Niveau","Email","Téléphone"]
WIDTHS  = [40, 100, 120, 120, 150, 70, 200, 120]


class EtudiantView(tk.Frame):

    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._data = []
        self._build()
        self._load()

    def _build(self):
        toolbar = tk.Frame(self, bg=DS["bg"])
        toolbar.pack(fill="x", padx=28, pady=(20, 0))

        left = tk.Frame(toolbar, bg=DS["bg"])
        left.pack(side="left")
        tk.Label(left, text="Étudiants", font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(anchor="w")
        self.count_lbl = tk.Label(left, text="",
                                   font=FONTS["body_sm"],
                                   bg=DS["bg"], fg=DS["text_muted"])
        self.count_lbl.pack(anchor="w")

        right = tk.Frame(toolbar, bg=DS["bg"])
        right.pack(side="right")
        UIComponents.btn_primary(right, "+ Ajouter un étudiant",
                                  command=self._open_add).pack(side="left", padx=(0, 8))
        UIComponents.btn_ghost(right, "PDF Exporter",
                                command=self._export_pdf).pack(side="left")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x", padx=28, pady=14)

        flt = tk.Frame(self, bg=DS["bg"])
        flt.pack(fill="x", padx=28, pady=(0, 12))

        self.search = PremiumSearchBar(flt, "Rechercher par nom, matricule, email...",
                                       on_change=self._on_search, bg=DS["bg"])
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(flt, text="Filière", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.filiere_var = tk.StringVar()
        ttk.Combobox(flt, textvariable=self.filiere_var, width=18,
                     values=[""] + EtudiantController.get_filieres(),
                     state="readonly").pack(side="left", padx=(4, 12))
        self.filiere_var.trace_add("write", lambda *a: self._on_search(""))

        tk.Label(flt, text="Niveau", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.niveau_var = tk.StringVar()
        ttk.Combobox(flt, textvariable=self.niveau_var, width=8,
                     values=[""] + EtudiantController.get_niveaux(),
                     state="readonly").pack(side="left", padx=(4, 12))
        self.niveau_var.trace_add("write", lambda *a: self._on_search(""))

        UIComponents.btn_secondary(flt, "Réinitialiser",
                                    command=self._reset).pack(side="left")

        container = tk.Frame(self, bg=DS["bg"])
        container.pack(fill="both", expand=True, padx=28, pady=(0, 8))
        tbl_wrap, self.tree = make_premium_table(container, COLS, WIDTHS, HEADERS)
        tbl_wrap.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._open_detail())
        self.tree.bind("<Button-3>", self._context_menu)

        actions = tk.Frame(self, bg=DS["card"],
                           highlightbackground=DS["border_bright"],
                           highlightthickness=1, padx=20, pady=8)
        actions.pack(fill="x", padx=28, pady=(0, 20))
        UIComponents.btn_secondary(actions, "Modifier",
                                    command=self._open_edit).pack(side="left", padx=(0, 8))
        UIComponents.btn_secondary(actions, "Fiche complète",
                                    command=self._open_detail).pack(side="left", padx=(0, 8))
        UIComponents.btn_danger(actions, "Supprimer",
                                 command=self._delete).pack(side="left")
        tk.Label(actions, text="Double-clic pour ouvrir la fiche",
                 font=FONTS["caption"], bg=DS["card"],
                 fg=DS["text_dim"]).pack(side="right")

    def _load(self, data=None):
        try:
            self._data = data if data is not None else EtudiantController.get_liste()
            fill_premium_table(self.tree, self._data, COLS)
            n = len(self._data)
            self.count_lbl.config(text=f"{n} étudiant{'s' if n > 1 else ''} enregistré{'s' if n > 1 else ''}")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _on_search(self, terme=""):
        terme = self.search.get()
        f = self.filiere_var.get()
        n = self.niveau_var.get()
        try:
            r = EtudiantController.rechercher(terme, f, n)
            fill_premium_table(self.tree, r, COLS)
            self.count_lbl.config(text=f"{len(r)} résultat(s)")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _reset(self):
        self.filiere_var.set("")
        self.niveau_var.set("")
        self.search.clear()
        self._load()

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            show_message(self, "Sélection requise",
                         "Veuillez sélectionner un étudiant.", "warning")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _open_add(self):
        w = EtudiantForm(self, on_save=self._load)
        w.grab_set()
        w.focus_force()

    def _open_edit(self):
        eid = self._get_id()
        if not eid:
            return
        try:
            detail = EtudiantController.get_detail(eid)
            w = EtudiantForm(self, etudiant=detail["etudiant"], on_save=self._load)
            w.grab_set()
            w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _delete(self):
        eid = self._get_id()
        if not eid:
            return
        sel = self.tree.selection()
        vals = self.tree.item(sel[0])["values"]
        name = f"{vals[2]} {vals[3]}"
        if confirm_delete(self, name):
            try:
                EtudiantController.supprimer(eid)
                self._load()
                show_toast(self, f"{name} supprimé.", "success")
            except Exception as e:
                show_message(self, "Erreur", str(e), "error")

    def _open_detail(self):
        eid = self._get_id()
        if not eid:
            return
        try:
            detail = EtudiantController.get_detail(eid)
            w = EtudiantDetail(self, detail)
            w.grab_set()
            w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _export_pdf(self):
        try:
            from utils.pdf_export import export_liste_etudiants
            fp = export_liste_etudiants(self._data)
            show_toast(self, "PDF généré avec succès.", "success")
            show_message(self, "Export PDF", f"Fichier enregistré :\n{fp}")
        except Exception as e:
            show_message(self, "Erreur PDF", str(e), "error")

    def _context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        menu = tk.Menu(self, tearoff=0, bg=DS["card"], fg=DS["text_primary"])
        menu.add_command(label="Fiche complète", command=self._open_detail)
        menu.add_command(label="Modifier",       command=self._open_edit)
        menu.add_separator()
        menu.add_command(label="Supprimer",      command=self._delete)
        menu.tk_popup(event.x_root, event.y_root)


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULAIRE — Construction sans Toplevel noir
# ══════════════════════════════════════════════════════════════════════════════

class EtudiantForm(tk.Toplevel):

    def __init__(self, parent, etudiant=None, on_save=None):
        super().__init__(parent)
        self.etudiant = etudiant
        self.on_save  = on_save
        self.title("Modifier l'étudiant" if etudiant else "Ajouter un étudiant")
        self.geometry("700x540")
        self.resizable(False, False)
        self.configure(bg=DS["card"])
        self._center()
        self._build()
        self.lift()
        self.focus_force()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 700) // 2
        y = (self.winfo_screenheight() - 540) // 2
        self.geometry(f"700x540+{x}+{y}")

    def _build(self):
        et = self.etudiant or {}
        self.vars = {}

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=16)
        hdr.pack(fill="x")
        title = "Modifier l'étudiant" if self.etudiant else "Ajouter un étudiant"
        sub   = et.get("matricule", "Remplissez les informations ci-dessous")
        tk.Label(hdr, text=title, font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text=sub, font=FONTS["body_sm"],
                 bg="#0F172A", fg=DS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # ── Body ──────────────────────────────────────────────────────────────
        body = tk.Frame(self, bg=DS["card"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # Two columns
        left  = tk.Frame(body, bg=DS["card"])
        right = tk.Frame(body, bg=DS["card"])
        left.grid(row=0, column=0, sticky="n", padx=(0, 20))
        right.grid(row=0, column=1, sticky="n")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        def add_field(parent, label, key, row, show=""):
            tk.Label(parent, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=row, column=0,
                                      sticky="w", pady=(6, 1))
            var = tk.StringVar(value=str(et.get(key, "")))
            e = tk.Entry(parent, textvariable=var,
                         font=FONTS["body"], show=show,
                         bg=DS["bg_3"], fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="solid", bd=1, width=26)
            e.grid(row=row+1, column=0, sticky="ew",
                   pady=(0, 2), ipady=6)
            self.vars[key] = var
            return var

        # Left column fields
        add_field(left, "Matricule *",   "matricule",       0)
        add_field(left, "Nom *",         "nom",             2)
        add_field(left, "Prénom *",      "prenom",          4)
        add_field(left, "Email",         "email",           6)
        add_field(left, "Téléphone",     "telephone",       8)

        # Right column fields
        add_field(right, "Date de naissance (AAAA-MM-JJ)", "date_naissance",  0)
        add_field(right, "Date d'inscription (AAAA-MM-JJ)", "date_inscription", 2)

        tk.Label(right, text="Filière", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"],
                 anchor="w").grid(row=4, column=0, sticky="w", pady=(6, 1))
        self.filiere_var = tk.StringVar(value=et.get("filiere", ""))
        ttk.Combobox(right, textvariable=self.filiere_var,
                     values=EtudiantController.get_filieres(),
                     state="readonly", width=24).grid(
            row=5, column=0, sticky="ew", pady=(0, 2))

        tk.Label(right, text="Niveau", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"],
                 anchor="w").grid(row=6, column=0, sticky="w", pady=(6, 1))
        self.niveau_var = tk.StringVar(value=et.get("niveau", ""))
        ttk.Combobox(right, textvariable=self.niveau_var,
                     values=EtudiantController.get_niveaux(),
                     state="readonly", width=24).grid(
            row=7, column=0, sticky="ew", pady=(0, 2))

        # Error message
        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["danger"], anchor="w").grid(
            row=1, column=0, columnspan=2,
            sticky="w", pady=(8, 0))

        # ── Footer buttons ─────────────────────────────────────────────────────
        footer = tk.Frame(self, bg=DS["bg_3"], padx=24, pady=14)
        footer.pack(fill="x")

        btn_save = tk.Button(footer, text="Enregistrer",
                             font=FONTS["btn"],
                             bg=DS["primary"], fg="white",
                             relief="flat", bd=0,
                             cursor="hand2",
                             padx=18, pady=8,
                             command=self._save)
        btn_save.pack(side="left", padx=(0, 8))
        btn_save.bind("<Enter>", lambda e: btn_save.config(bg=DS["primary_hover"]))
        btn_save.bind("<Leave>", lambda e: btn_save.config(bg=DS["primary"]))

        btn_cancel = tk.Button(footer, text="Annuler",
                               font=FONTS["btn"],
                               bg=DS["bg_3"], fg=DS["text_secondary"],
                               relief="solid", bd=1,
                               cursor="hand2",
                               padx=14, pady=8,
                               command=self.destroy)
        btn_cancel.pack(side="left")

    def _save(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        data["filiere"] = self.filiere_var.get()
        data["niveau"]  = self.niveau_var.get()
        try:
            if self.etudiant:
                EtudiantController.modifier(self.etudiant["id"], **data)
                show_toast(self.master, "Étudiant modifié.", "success")
            else:
                EtudiantController.ajouter(**data)
                show_toast(self.master, "Étudiant ajouté.", "success")
            if self.on_save:
                self.on_save()
            self.destroy()
        except ValueError as e:
            self.msg_var.set(f"Erreur : {e}")
        except Exception as e:
            self.msg_var.set(f"Erreur : {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  DETAIL VIEW
# ══════════════════════════════════════════════════════════════════════════════

class EtudiantDetail(tk.Toplevel):

    def __init__(self, parent, detail):
        super().__init__(parent)
        self.detail = detail
        et = detail["etudiant"]
        self.title(f"Fiche – {et['prenom']} {et['nom']}")
        self.geometry("860x620")
        self.configure(bg=DS["bg"])
        self._center()
        self._build()
        self.lift()

    def _center(self):
        x = (self.winfo_screenwidth()  - 860) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"860x620+{x}+{y}")

    def _build(self):
        et  = self.detail["etudiant"]
        moy = self.detail.get("moyenne", 0)

        # Header
        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=18)
        hdr.pack(fill="x")
        left_h = tk.Frame(hdr, bg="#0F172A")
        left_h.pack(side="left")
        tk.Label(left_h, text=f"{et['prenom']} {et['nom']}",
                 font=FONTS["h2"], bg="#0F172A",
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(left_h,
                 text=f"Matricule : {et['matricule']}  ·  "
                      f"{et.get('filiere', '')}  ·  {et.get('niveau', '')}",
                 font=FONTS["body_sm"], bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 0))

        moy_c = DS["success"] if (moy or 0) >= 10 else DS["danger"]
        moy_f = tk.Frame(hdr, bg=moy_c, padx=16, pady=8)
        moy_f.pack(side="right")
        tk.Label(moy_f, text=f"{moy:.2f}/20" if moy else "N/A",
                 font=FONTS["h2"], bg=moy_c, fg="white").pack()
        tk.Label(moy_f, text="Moyenne", font=FONTS["caption"],
                 bg=moy_c, fg="white").pack()

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        t_info = tk.Frame(nb, bg=DS["card"])
        nb.add(t_info, text="  Informations  ")
        self._tab_info(t_info, et)

        projets = self.detail.get("projets", [])
        t_proj  = tk.Frame(nb, bg=DS["card"])
        nb.add(t_proj, text=f"  Projets ({len(projets)})  ")
        self._tab_list(t_proj, projets,
                       ["titre","type_projet","role",
                        "annee_libelle","statut","note"],
                       ["Titre","Type","Rôle","Année","Statut","Note"],
                       [200, 80, 100, 100, 90, 70])

        stages = self.detail.get("stages", [])
        t_stage = tk.Frame(nb, bg=DS["card"])
        nb.add(t_stage, text=f"  Stages ({len(stages)})  ")
        self._tab_list(t_stage, stages,
                       ["titre","entreprise_nom","date_debut",
                        "date_fin","duree_semaines","statut","note"],
                       ["Titre","Entreprise","Début",
                        "Fin","Semaines","Statut","Note"],
                       [180, 140, 90, 90, 70, 90, 70])

        # Footer
        footer = tk.Frame(self, bg=DS["bg_3"], padx=20, pady=12)
        footer.pack(fill="x")
        btn = tk.Button(footer, text="Exporter PDF",
                        font=FONTS["btn"], bg=DS["teal"],
                        fg="white", relief="flat", bd=0,
                        cursor="hand2", padx=14, pady=7,
                        command=self._pdf)
        btn.pack(side="left")
        tk.Button(footer, text="Fermer",
                  font=FONTS["btn"], bg=DS["bg_3"],
                  fg=DS["text_secondary"], relief="solid", bd=1,
                  cursor="hand2", padx=14, pady=7,
                  command=self.destroy).pack(side="left", padx=(8, 0))

    def _tab_info(self, parent, et):
        frame = tk.Frame(parent, bg=DS["card"], padx=24, pady=16)
        frame.pack(fill="both", expand=True)
        rows = [
            ("Matricule",         et.get("matricule", "")),
            ("Nom complet",       f"{et.get('prenom','')} {et.get('nom','')}"),
            ("Email",             et.get("email", "")),
            ("Téléphone",         et.get("telephone", "")),
            ("Date de naissance", et.get("date_naissance", "")),
            ("Filière",           et.get("filiere", "")),
            ("Niveau",            et.get("niveau", "")),
            ("Date d'inscription",et.get("date_inscription", "")),
            ("Statut",            "Actif" if et.get("actif", 1) else "Inactif"),
        ]
        for i, (label, val) in enumerate(rows):
            r = i // 2
            c = (i % 2) * 2
            tk.Label(frame, text=label + " :", font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=r*2, column=c,
                                      sticky="w", pady=(8, 1), padx=(0, 16))
            tk.Label(frame, text=str(val or "—"), font=FONTS["body"],
                     bg=DS["card"], fg=DS["text_primary"],
                     anchor="w").grid(row=r*2+1, column=c,
                                      sticky="w", padx=(0, 16))
        for c in range(4):
            frame.grid_columnconfigure(c, weight=1)

    def _tab_list(self, parent, data, cols, headers, widths):
        frame, tree = make_premium_table(parent, cols, widths, headers)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        fill_premium_table(tree, data, cols)

    def _pdf(self):
        try:
            from utils.pdf_export import export_fiche_etudiant
            fp = export_fiche_etudiant(self.detail)
            show_message(self, "Export PDF", f"Fichier :\n{fp}")
        except Exception as e:
            show_message(self, "Erreur PDF", str(e), "error")
