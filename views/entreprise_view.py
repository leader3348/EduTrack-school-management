"""EduTrack — Vue Entreprises v3.1 (Windows-compatible forms)"""
import tkinter as tk
from tkinter import ttk
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, confirm_delete, show_toast)
from controllers import EntrepriseController
from models import Entreprise

COLS    = ["id","nom","secteur","adresse","telephone","email","contact_nom"]
HEADERS = ["ID","Nom","Secteur","Adresse","Téléphone","Email","Contact"]
WIDTHS  = [40, 180, 140, 170, 120, 180, 140]


class EntrepriseView(tk.Frame):
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
        tk.Label(left, text="Entreprises", font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(anchor="w")
        self.count_lbl = tk.Label(left, text="", font=FONTS["body_sm"],
                                   bg=DS["bg"], fg=DS["text_muted"])
        self.count_lbl.pack(anchor="w")
        right = tk.Frame(toolbar, bg=DS["bg"])
        right.pack(side="right")
        UIComponents.btn_primary(right, "+ Ajouter une entreprise",
                                  command=self._open_add).pack(side="left")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x", padx=28, pady=14)

        flt = tk.Frame(self, bg=DS["bg"])
        flt.pack(fill="x", padx=28, pady=(0, 12))
        self.search = PremiumSearchBar(flt, "Rechercher par nom ou secteur...",
                                       on_change=self._on_search, bg=DS["bg"])
        self.search.pack(side="left", fill="x", expand=True)

        container = tk.Frame(self, bg=DS["bg"])
        container.pack(fill="both", expand=True, padx=28, pady=(0, 8))
        tbl_wrap, self.tree = make_premium_table(container, COLS, WIDTHS, HEADERS)
        tbl_wrap.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self._open_edit())

        actions = tk.Frame(self, bg=DS["card"],
                           highlightbackground=DS["border_bright"],
                           highlightthickness=1, padx=20, pady=8)
        actions.pack(fill="x", padx=28, pady=(0, 20))
        UIComponents.btn_secondary(actions, "Modifier",
                                    command=self._open_edit).pack(side="left", padx=(0, 8))
        UIComponents.btn_danger(actions, "Supprimer",
                                 command=self._delete).pack(side="left")

    def _load(self, data=None):
        try:
            self._data = data if data is not None else EntrepriseController.get_liste()
            fill_premium_table(self.tree, self._data, COLS)
            n = len(self._data)
            self.count_lbl.config(text=f"{n} entreprise{'s' if n > 1 else ''}")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _on_search(self, terme=""):
        terme = self.search.get()
        try:
            r = EntrepriseController.rechercher(terme)
            fill_premium_table(self.tree, r, COLS)
            self.count_lbl.config(text=f"{len(r)} résultat(s)")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            show_message(self, "Sélection", "Sélectionnez une entreprise.", "warning")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _open_add(self):
        w = EntrepriseForm(self, on_save=self._load)
        w.grab_set(); w.focus_force()

    def _open_edit(self):
        eid = self._get_id()
        if not eid: return
        entr = Entreprise.get_by_id(eid)
        if entr:
            w = EntrepriseForm(self, entreprise=entr, on_save=self._load)
            w.grab_set(); w.focus_force()

    def _delete(self):
        eid = self._get_id()
        if not eid: return
        sel = self.tree.selection()
        nom = self.tree.item(sel[0])["values"][1]
        if confirm_delete(self, nom):
            try:
                EntrepriseController.supprimer(eid)
                self._load()
                show_toast(self, "Entreprise supprimée.", "success")
            except Exception as e:
                show_message(self, "Erreur", str(e), "error")


class EntrepriseForm(tk.Toplevel):
    def __init__(self, parent, entreprise=None, on_save=None):
        super().__init__(parent)
        self.entreprise = entreprise
        self.on_save    = on_save
        self.title("Modifier l'entreprise" if entreprise else "Ajouter une entreprise")
        self.geometry("660x500")
        self.resizable(False, False)
        self.configure(bg=DS["card"])
        x = (self.winfo_screenwidth()  - 660) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"660x500+{x}+{y}")
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        e = self.entreprise or {}
        self.vars = {}

        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=16)
        hdr.pack(fill="x")
        title = "Modifier l'entreprise" if self.entreprise else "Ajouter une entreprise"
        tk.Label(hdr, text=title, font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(anchor="w")

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
                     anchor="w").grid(row=row, column=0, sticky="w", pady=(6, 1))
            var = tk.StringVar(value=str(e.get(key, "")))
            en  = tk.Entry(parent, textvariable=var, font=FONTS["body"],
                           bg=DS["bg_3"], fg=DS["text_primary"],
                           insertbackground=DS["primary"],
                           relief="solid", bd=1, width=26)
            en.grid(row=row+1, column=0, sticky="ew", pady=(0, 2), ipady=6)
            self.vars[key] = var

        field(left,  "Nom *",          "nom",           0)
        field(left,  "Secteur",        "secteur",       2)
        field(left,  "Adresse",        "adresse",       4)
        field(left,  "Téléphone",      "telephone",     6)
        field(right, "Email",          "email",         0)
        field(right, "Site Web",       "site_web",      2)
        field(right, "Contact (Nom)",  "contact_nom",   4)
        field(right, "Contact (Email)","contact_email", 6)

        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["danger"], anchor="w").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        footer = tk.Frame(self, bg=DS["bg_3"], padx=24, pady=14)
        footer.pack(fill="x")
        btn = tk.Button(footer, text="Enregistrer",
                        font=FONTS["btn"], bg=DS["primary"],
                        fg="white", relief="flat", bd=0,
                        cursor="hand2", padx=18, pady=8,
                        command=self._save)
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
        try:
            if self.entreprise:
                EntrepriseController.modifier(self.entreprise["id"], **data)
                show_toast(self.master, "Entreprise modifiée.", "success")
            else:
                EntrepriseController.ajouter(**data)
                show_toast(self.master, "Entreprise ajoutée.", "success")
            if self.on_save: self.on_save()
            self.destroy()
        except ValueError as e:
            self.msg_var.set(str(e))
        except Exception as e:
            self.msg_var.set(str(e))
