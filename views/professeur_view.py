"""EduTrack — Vue Professeurs v3.1 (Windows-compatible)"""
import tkinter as tk
from tkinter import ttk
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, confirm_delete, show_toast)
from controllers import ProfesseurController
from models import Professeur

COLS    = ["id","matricule","nom","prenom","specialite","grade","email","telephone"]
HEADERS = ["ID","Matricule","Nom","Prénom","Spécialité","Grade","Email","Téléphone"]
WIDTHS  = [40, 100, 120, 120, 180, 100, 190, 120]


class ProfesseurView(tk.Frame):
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
        tk.Label(left, text="Professeurs", font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(anchor="w")
        self.count_lbl = tk.Label(left, text="", font=FONTS["body_sm"],
                                   bg=DS["bg"], fg=DS["text_muted"])
        self.count_lbl.pack(anchor="w")
        right = tk.Frame(toolbar, bg=DS["bg"])
        right.pack(side="right")
        UIComponents.btn_primary(right, "+ Ajouter un professeur",
                                  command=self._open_add).pack(side="left")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x", padx=28, pady=14)

        flt = tk.Frame(self, bg=DS["bg"])
        flt.pack(fill="x", padx=28, pady=(0, 12))
        self.search = PremiumSearchBar(flt, "Rechercher par nom, matricule, spécialité...",
                                       on_change=self._on_search, bg=DS["bg"])
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(flt, text="Grade", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.grade_var = tk.StringVar()
        ttk.Combobox(flt, textvariable=self.grade_var, width=12,
                     values=[""] + ProfesseurController.get_grades(),
                     state="readonly").pack(side="left", padx=(4, 12))
        self.grade_var.trace_add("write", lambda *a: self._on_search(""))
        UIComponents.btn_secondary(flt, "Réinitialiser",
                                    command=self._reset).pack(side="left")

        container = tk.Frame(self, bg=DS["bg"])
        container.pack(fill="both", expand=True, padx=28, pady=(0, 8))
        tbl_wrap, self.tree = make_premium_table(container, COLS, WIDTHS, HEADERS)
        tbl_wrap.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._open_detail())

        actions = tk.Frame(self, bg=DS["card"],
                           highlightbackground=DS["border_bright"],
                           highlightthickness=1, padx=20, pady=8)
        actions.pack(fill="x", padx=28, pady=(0, 20))
        UIComponents.btn_secondary(actions, "Modifier",
                                    command=self._open_edit).pack(side="left", padx=(0, 8))
        UIComponents.btn_secondary(actions, "Détail",
                                    command=self._open_detail).pack(side="left", padx=(0, 8))
        UIComponents.btn_danger(actions, "Supprimer",
                                 command=self._delete).pack(side="left")

    def _load(self, data=None):
        try:
            self._data = data if data is not None else ProfesseurController.get_liste()
            fill_premium_table(self.tree, self._data, COLS)
            n = len(self._data)
            self.count_lbl.config(text=f"{n} professeur{'s' if n > 1 else ''}")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _on_search(self, terme=""):
        terme = self.search.get()
        grade = self.grade_var.get()
        try:
            r = ProfesseurController.rechercher(terme, grade)
            fill_premium_table(self.tree, r, COLS)
            self.count_lbl.config(text=f"{len(r)} résultat(s)")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _reset(self):
        self.grade_var.set("")
        self.search.clear()
        self._load()

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            show_message(self, "Sélection", "Sélectionnez un professeur.", "warning")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _open_add(self):
        w = ProfesseurForm(self, on_save=self._load)
        w.grab_set(); w.focus_force()

    def _open_edit(self):
        pid = self._get_id()
        if not pid: return
        prof = Professeur.get_by_id(pid)
        if prof:
            w = ProfesseurForm(self, professeur=prof, on_save=self._load)
            w.grab_set(); w.focus_force()

    def _delete(self):
        pid = self._get_id()
        if not pid: return
        sel = self.tree.selection()
        name = f"{self.tree.item(sel[0])['values'][2]} {self.tree.item(sel[0])['values'][3]}"
        if confirm_delete(self, name):
            try:
                ProfesseurController.supprimer(pid)
                self._load()
                show_toast(self, "Professeur supprimé.", "success")
            except Exception as e:
                show_message(self, "Erreur", str(e), "error")

    def _open_detail(self):
        pid = self._get_id()
        if not pid: return
        try:
            detail = ProfesseurController.get_detail(pid)
            w = ProfesseurDetail(self, detail)
            w.grab_set(); w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")


class ProfesseurForm(tk.Toplevel):
    def __init__(self, parent, professeur=None, on_save=None):
        super().__init__(parent)
        self.professeur = professeur
        self.on_save    = on_save
        self.title("Modifier le professeur" if professeur else "Ajouter un professeur")
        self.geometry("660x480")
        self.resizable(False, False)
        self.configure(bg=DS["card"])
        x = (self.winfo_screenwidth()  - 660) // 2
        y = (self.winfo_screenheight() - 480) // 2
        self.geometry(f"660x480+{x}+{y}")
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        p = self.professeur or {}
        self.vars = {}

        # Header
        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=16)
        hdr.pack(fill="x")
        title = "Modifier le professeur" if self.professeur else "Ajouter un professeur"
        tk.Label(hdr, text=title, font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text=p.get("matricule", "Corps enseignant"),
                 font=FONTS["body_sm"], bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Body - two columns
        body = tk.Frame(self, bg=DS["card"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        left  = tk.Frame(body, bg=DS["card"])
        right = tk.Frame(body, bg=DS["card"])
        left.grid(row=0, column=0, sticky="n", padx=(0, 20))
        right.grid(row=0, column=1, sticky="n")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        def field(parent, label, key, row):
            tk.Label(parent, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=row, column=0,
                                      sticky="w", pady=(6, 1))
            var = tk.StringVar(value=str(p.get(key, "")))
            e = tk.Entry(parent, textvariable=var,
                         font=FONTS["body"],
                         bg=DS["bg_3"], fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="solid", bd=1, width=24)
            e.grid(row=row+1, column=0, sticky="ew",
                   pady=(0, 2), ipady=6)
            self.vars[key] = var

        field(left, "Matricule *",  "matricule",  0)
        field(left, "Nom *",        "nom",         2)
        field(left, "Prénom *",     "prenom",      4)
        field(left, "Email",        "email",       6)

        field(right, "Téléphone",   "telephone",   0)
        field(right, "Spécialité",  "specialite",  2)

        tk.Label(right, text="Grade", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"],
                 anchor="w").grid(row=4, column=0, sticky="w", pady=(6, 1))
        self.grade_var = tk.StringVar(value=p.get("grade", "Assistant"))
        ttk.Combobox(right, textvariable=self.grade_var,
                     values=ProfesseurController.get_grades(),
                     state="readonly", width=22).grid(
            row=5, column=0, sticky="ew", pady=(0, 2))

        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["danger"], anchor="w").grid(
            row=1, column=0, columnspan=2,
            sticky="w", pady=(8, 0))

        # Footer
        footer = tk.Frame(self, bg=DS["bg_3"], padx=24, pady=14)
        footer.pack(fill="x")
        btn = tk.Button(footer, text="Enregistrer",
                        font=FONTS["btn"],
                        bg=DS["primary"], fg="white",
                        relief="flat", bd=0, cursor="hand2",
                        padx=18, pady=8, command=self._save)
        btn.pack(side="left", padx=(0, 8))
        btn.bind("<Enter>", lambda e: btn.config(bg=DS["primary_hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=DS["primary"]))
        tk.Button(footer, text="Annuler",
                  font=FONTS["btn"], bg=DS["bg_3"],
                  fg=DS["text_secondary"], relief="solid", bd=1,
                  cursor="hand2", padx=14, pady=8,
                  command=self.destroy).pack(side="left")

    def _save(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        data["grade"] = self.grade_var.get()
        try:
            if self.professeur:
                ProfesseurController.modifier(self.professeur["id"], **data)
                show_toast(self.master, "Professeur modifié.", "success")
            else:
                ProfesseurController.ajouter(**data)
                show_toast(self.master, "Professeur ajouté.", "success")
            if self.on_save: self.on_save()
            self.destroy()
        except ValueError as e:
            self.msg_var.set(str(e))
        except Exception as e:
            self.msg_var.set(str(e))


class ProfesseurDetail(tk.Toplevel):
    def __init__(self, parent, detail):
        super().__init__(parent)
        self.detail = detail
        p = detail["professeur"]
        self.title(f"Prof. {p['prenom']} {p['nom']}")
        self.geometry("780x520")
        self.configure(bg=DS["bg"])
        x = (self.winfo_screenwidth()  - 780) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"780x520+{x}+{y}")
        self._build()
        self.lift()

    def _build(self):
        p  = self.detail["professeur"]
        pr = self.detail.get("projets", [])
        st = self.detail.get("stages", [])

        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{p['prenom']} {p['nom']}",
                 font=FONTS["h2"], bg="#0F172A",
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text=f"{p.get('grade','')}  ·  {p.get('specialite','')}",
                 font=FONTS["body_sm"], bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 0))

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        t1 = tk.Frame(nb, bg=DS["card"], padx=20, pady=16)
        nb.add(t1, text="  Informations  ")
        for i, (k, v) in enumerate([
            ("Matricule", p.get("matricule","")),
            ("Email",     p.get("email","")),
            ("Téléphone", p.get("telephone","")),
            ("Spécialité",p.get("specialite","")),
            ("Grade",     p.get("grade",""))
        ]):
            tk.Label(t1, text=k+":", font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w", width=16).grid(row=i, column=0, sticky="w", pady=6)
            tk.Label(t1, text=str(v or "—"), font=FONTS["body"],
                     bg=DS["card"]).grid(row=i, column=1, sticky="w", padx=12)

        t2 = tk.Frame(nb, bg=DS["card"])
        nb.add(t2, text=f"  Projets ({len(pr)})  ")
        f1, tr1 = make_premium_table(t2,
            ["titre","type_projet","jury_role","annee_libelle","statut"],
            [200, 90, 110, 110, 100],
            ["Titre","Type","Rôle jury","Année","Statut"])
        f1.pack(fill="both", expand=True, padx=8, pady=8)
        fill_premium_table(tr1, pr, ["titre","type_projet","jury_role","annee_libelle","statut"])

        t3 = tk.Frame(nb, bg=DS["card"])
        nb.add(t3, text=f"  Stages ({len(st)})  ")
        f2, tr2 = make_premium_table(t3,
            ["titre","etudiant_nom","entreprise_nom","annee_libelle","statut"],
            [180, 140, 140, 110, 100],
            ["Titre","Étudiant","Entreprise","Année","Statut"])
        f2.pack(fill="both", expand=True, padx=8, pady=8)
        fill_premium_table(tr2, st, ["titre","etudiant_nom","entreprise_nom","annee_libelle","statut"])

        footer = tk.Frame(self, bg=DS["bg_3"], padx=20, pady=12)
        footer.pack(fill="x")
        tk.Button(footer, text="Fermer", font=FONTS["btn"],
                  bg=DS["bg_3"], fg=DS["text_secondary"],
                  relief="solid", bd=1, cursor="hand2",
                  padx=14, pady=7, command=self.destroy).pack(side="left")
