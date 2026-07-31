"""EduTrack — Vue Stages v3.1 (Windows-compatible forms)"""
import tkinter as tk
from tkinter import ttk
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, confirm_delete, show_toast)
from controllers import (StageController, EtudiantController,
                          ProfesseurController, AnneeController,
                          EntrepriseController)
from models import Stage

COLS    = ["id","titre","etudiant_nom","entreprise_nom",
           "date_debut","date_fin","duree_semaines","statut","note"]
HEADERS = ["ID","Titre","Étudiant","Entreprise",
           "Début","Fin","Semaines","Statut","Note"]
WIDTHS  = [40, 180, 140, 140, 90, 90, 70, 90, 60]


class StageView(tk.Frame):
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
        tk.Label(left, text="Stages", font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(anchor="w")
        self.count_lbl = tk.Label(left, text="", font=FONTS["body_sm"],
                                   bg=DS["bg"], fg=DS["text_muted"])
        self.count_lbl.pack(anchor="w")
        right = tk.Frame(toolbar, bg=DS["bg"])
        right.pack(side="right")
        UIComponents.btn_primary(right, "+ Nouveau stage",
                                  command=self._open_add).pack(side="left", padx=(0, 8))
        UIComponents.btn_ghost(right, "PDF", command=self._export_pdf).pack(side="left")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x", padx=28, pady=14)

        flt = tk.Frame(self, bg=DS["bg"])
        flt.pack(fill="x", padx=28, pady=(0, 12))
        self.search = PremiumSearchBar(flt, "Rechercher par titre, étudiant, entreprise...",
                                       on_change=self._on_search, bg=DS["bg"])
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(flt, text="Statut", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.statut_var = tk.StringVar()
        ttk.Combobox(flt, textvariable=self.statut_var, width=12,
                     values=[""] + Stage.STATUTS, state="readonly").pack(
            side="left", padx=(4, 12))
        self.statut_var.trace_add("write", lambda *a: self._on_search(""))

        tk.Label(flt, text="Année", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.annee_var = tk.StringVar(value="Toutes")
        annees = AnneeController.get_annees()
        self._annees_map = {a["libelle"]: a["id"] for a in annees}
        ttk.Combobox(flt, textvariable=self.annee_var, width=12,
                     values=["Toutes"] + list(self._annees_map.keys()),
                     state="readonly").pack(side="left", padx=(4, 12))
        self.annee_var.trace_add("write", lambda *a: self._on_search(""))
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
        UIComponents.btn_secondary(actions, "Noter",
                                    command=self._noter).pack(side="left", padx=(0, 8))
        UIComponents.btn_danger(actions, "Supprimer",
                                 command=self._delete).pack(side="left")

    def _load(self, data=None):
        try:
            self._data = data if data is not None else StageController.get_liste()
            fill_premium_table(self.tree, self._data, COLS)
            n = len(self._data)
            self.count_lbl.config(text=f"{n} stage{'s' if n > 1 else ''}")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _on_search(self, terme=""):
        terme  = self.search.get()
        statut = self.statut_var.get()
        al     = self.annee_var.get()
        aid    = self._annees_map.get(al) if al != "Toutes" else None
        try:
            r = StageController.rechercher(terme, statut, aid)
            fill_premium_table(self.tree, r, COLS)
            self.count_lbl.config(text=f"{len(r)} résultat(s)")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _reset(self):
        self.statut_var.set("")
        self.annee_var.set("Toutes")
        self.search.clear()
        self._load()

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            show_message(self, "Sélection", "Sélectionnez un stage.", "warning")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _open_add(self):
        w = StageForm(self, on_save=self._load)
        w.grab_set(); w.focus_force()

    def _open_edit(self):
        sid = self._get_id()
        if not sid: return
        try:
            stage = StageController.get_detail(sid)
            w = StageForm(self, stage=stage, on_save=self._load)
            w.grab_set(); w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _delete(self):
        sid = self._get_id()
        if not sid: return
        sel   = self.tree.selection()
        titre = self.tree.item(sel[0])["values"][1]
        if confirm_delete(self, titre):
            try:
                StageController.supprimer(sid)
                self._load()
                show_toast(self, "Stage supprimé.", "success")
            except Exception as e:
                show_message(self, "Erreur", str(e), "error")

    def _open_detail(self):
        sid = self._get_id()
        if not sid: return
        try:
            stage = StageController.get_detail(sid)
            w = StageDetail(self, stage)
            w.grab_set(); w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _noter(self):
        sid = self._get_id()
        if not sid: return
        w = NoteDialog(self, "Stage", sid, callback=self._load)
        w.grab_set(); w.focus_force()

    def _export_pdf(self):
        try:
            from utils.pdf_export import export_liste_stages
            fp = export_liste_stages(self._data)
            show_toast(self, "PDF généré.", "success")
            show_message(self, "Export", f"Fichier :\n{fp}")
        except Exception as e:
            show_message(self, "Erreur PDF", str(e), "error")


class StageForm(tk.Toplevel):
    def __init__(self, parent, stage=None, on_save=None):
        super().__init__(parent)
        self.stage   = stage
        self.on_save = on_save
        self.title("Modifier le stage" if stage else "Nouveau stage")
        self.geometry("720x580")
        self.resizable(False, False)
        self.configure(bg=DS["card"])
        x = (self.winfo_screenwidth()  - 720) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"720x580+{x}+{y}")
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        s = self.stage or {}

        # Header
        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=16)
        hdr.pack(fill="x")
        title = "Modifier le stage" if self.stage else "Nouveau stage"
        tk.Label(hdr, text=title, font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text=s.get("titre", "Enregistrer un stage professionnel"),
                 font=FONTS["body_sm"], bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Load reference data
        etudiants   = EtudiantController.get_liste()
        professeurs = ProfesseurController.get_liste()
        entreprises = EntrepriseController.get_liste()
        annees      = AnneeController.get_annees()

        self._etud_map  = {f"{e['matricule']} - {e['nom']} {e['prenom']}": e["id"]
                           for e in etudiants}
        self._prof_map  = {"-- Aucun --": None,
                           **{f"{p['matricule']} - {p['nom']} {p['prenom']}": p["id"]
                              for p in professeurs}}
        self._entr_map  = {"-- Aucune --": None,
                           **{e["nom"]: e["id"] for e in entreprises}}
        self._annee_map = {a["libelle"]: a["id"] for a in annees}
        self._annee_rev = {a["id"]: a["libelle"] for a in annees}

        def cur_label(map_, id_val):
            for k, v in map_.items():
                if v == id_val: return k
            return list(map_.keys())[0] if map_ else ""

        # Body
        body = tk.Frame(self, bg=DS["card"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        left  = tk.Frame(body, bg=DS["card"])
        right = tk.Frame(body, bg=DS["card"])
        left.grid(row=0, column=0, sticky="n", padx=(0, 20))
        right.grid(row=0, column=1, sticky="n")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        self.vars = {}

        def txt_field(parent, label, key, row, val=""):
            tk.Label(parent, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=row, column=0, sticky="w", pady=(6, 1))
            var = tk.StringVar(value=str(s.get(key, val) or ""))
            e = tk.Entry(parent, textvariable=var, font=FONTS["body"],
                         bg=DS["bg_3"], fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="solid", bd=1, width=24)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 2), ipady=6)
            self.vars[key] = var

        def combo_field(parent, label, values, current, row, width=22):
            tk.Label(parent, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=row, column=0, sticky="w", pady=(6, 1))
            var = tk.StringVar(value=current)
            cb  = ttk.Combobox(parent, textvariable=var,
                                values=values, state="readonly", width=width)
            cb.grid(row=row+1, column=0, sticky="ew", pady=(0, 2))
            return var

        # Left column
        txt_field(left, "Titre *", "titre", 0)
        self.etud_var = combo_field(
            left, "Étudiant *",
            list(self._etud_map.keys()),
            cur_label(self._etud_map, s.get("etudiant_id")),
            2)
        self.entr_var = combo_field(
            left, "Entreprise",
            list(self._entr_map.keys()),
            cur_label(self._entr_map, s.get("entreprise_id")),
            4)
        self.prof_var = combo_field(
            left, "Encadrant",
            list(self._prof_map.keys()),
            cur_label(self._prof_map, s.get("professeur_encadrant_id")),
            6)

        # Right column
        self.annee_var = combo_field(
            right, "Année universitaire *",
            list(self._annee_map.keys()),
            self._annee_rev.get(s.get("annee_id"), ""),
            0)
        txt_field(right, "Date début * (AAAA-MM-JJ)", "date_debut", 2)
        txt_field(right, "Date fin * (AAAA-MM-JJ)",   "date_fin",   4)
        txt_field(right, "Durée (semaines)",           "duree_semaines", 6,
                  val=str(s.get("duree_semaines", "") or ""))
        self.statut_var = combo_field(
            right, "Statut",
            Stage.STATUTS,
            s.get("statut", "En cours"),
            8)

        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var,
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["danger"], anchor="w").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # Footer
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
        try:
            titre       = self.vars["titre"].get().strip()
            etud_id     = self._etud_map.get(self.etud_var.get())
            entr_id     = self._entr_map.get(self.entr_var.get())
            prof_id     = self._prof_map.get(self.prof_var.get())
            annee_id    = self._annee_map.get(self.annee_var.get())
            date_debut  = self.vars["date_debut"].get().strip()
            date_fin    = self.vars["date_fin"].get().strip()
            duree_str   = self.vars["duree_semaines"].get().strip()
            duree       = int(duree_str) if duree_str.isdigit() else None
            statut      = self.statut_var.get()

            if self.stage:
                StageController.modifier(
                    self.stage["id"], titre=titre,
                    etudiant_id=etud_id, entreprise_id=entr_id,
                    professeur_encadrant_id=prof_id, annee_id=annee_id,
                    date_debut=date_debut, date_fin=date_fin,
                    duree_semaines=duree, statut=statut)
            else:
                StageController.ajouter(
                    titre=titre, etudiant_id=etud_id, annee_id=annee_id,
                    date_debut=date_debut, date_fin=date_fin,
                    entreprise_id=entr_id, professeur_encadrant_id=prof_id,
                    duree_semaines=duree)

            show_toast(self.master, "Stage enregistré.", "success")
            if self.on_save: self.on_save()
            self.destroy()
        except ValueError as e:
            self.msg_var.set(str(e))
        except Exception as e:
            self.msg_var.set(str(e))


class StageDetail(tk.Toplevel):
    def __init__(self, parent, stage):
        super().__init__(parent)
        self.stage = stage
        self.title(f"Stage – {stage['titre']}")
        self.geometry("620x500")
        self.configure(bg=DS["bg"])
        x = (self.winfo_screenwidth()  - 620) // 2
        y = (self.winfo_screenheight() - 500) // 2
        self.geometry(f"620x500+{x}+{y}")
        self._build()
        self.lift()

    def _build(self):
        s = self.stage
        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text=s["titre"], font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(side="left", anchor="w")
        if s.get("note"):
            nf = tk.Frame(hdr, bg=DS["success"], padx=12, pady=6)
            nf.pack(side="right")
            tk.Label(nf, text=f"{s['note']:.1f}/20",
                     font=FONTS["h3"], bg=DS["success"], fg="white").pack()

        frame = tk.Frame(self, bg=DS["card"], padx=24, pady=16)
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        infos = [
            ("Étudiant",   s.get("etudiant_nom", "")),
            ("Entreprise", s.get("entreprise_nom", "N/A")),
            ("Encadrant",  s.get("encadrant_nom", "")),
            ("Année",      s.get("annee_libelle", "")),
            ("Date début", s.get("date_debut", "")),
            ("Date fin",   s.get("date_fin", "")),
            ("Durée",      f"{s.get('duree_semaines','?')} semaines"),
            ("Statut",     s.get("statut", "")),
            ("Note",       f"{s['note']:.1f}/20" if s.get("note") else "Non notée"),
            ("Mention",    s.get("mention", "")),
        ]
        for i, (k, v) in enumerate(infos):
            r = i // 2
            c = (i % 2) * 2
            tk.Label(frame, text=k+":", font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w", width=12).grid(row=r*2, column=c,
                                                 sticky="w", pady=(6,1), padx=(0,12))
            tk.Label(frame, text=str(v or "—"), font=FONTS["body"],
                     bg=DS["card"], fg=DS["text_primary"],
                     anchor="w").grid(row=r*2+1, column=c,
                                      sticky="w", padx=(0,12))
        for c in range(4):
            frame.grid_columnconfigure(c, weight=1)

        footer = tk.Frame(self, bg=DS["bg_3"], padx=20, pady=12)
        footer.pack(fill="x")
        tk.Button(footer, text="Fermer", font=FONTS["btn"],
                  bg=DS["bg_3"], fg=DS["text_secondary"],
                  relief="solid", bd=1, cursor="hand2",
                  padx=14, pady=7, command=self.destroy).pack(side="left")


class NoteDialog(tk.Toplevel):
    def __init__(self, parent, entity_type, entity_id, callback=None):
        super().__init__(parent)
        self.etype    = entity_type
        self.eid      = entity_id
        self.callback = callback
        self.title(f"Attribuer une note – {entity_type}")
        self.geometry("400x260")
        self.resizable(False, False)
        self.configure(bg=DS["card"])
        x = (self.winfo_screenwidth()  - 400) // 2
        y = (self.winfo_screenheight() - 260) // 2
        self.geometry(f"400x260+{x}+{y}")
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        hdr = tk.Frame(self, bg="#0F172A", padx=20, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"Note – {self.etype}",
                 font=FONTS["h3"], bg="#0F172A",
                 fg=DS["text_primary"]).pack(anchor="w")

        body = tk.Frame(self, bg=DS["card"], padx=24, pady=20)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)

        tk.Label(body, text="Note (0 – 20) *", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"],
                 anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.note_var = tk.StringVar()
        tk.Entry(body, textvariable=self.note_var, font=FONTS["body"],
                 bg=DS["bg_3"], fg=DS["text_primary"],
                 insertbackground=DS["primary"],
                 relief="solid", bd=1, width=20).grid(
            row=1, column=0, sticky="ew", ipady=7, pady=(0, 10))

        tk.Label(body, text="Mention", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"],
                 anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.mention_var = tk.StringVar()
        ttk.Combobox(body, textvariable=self.mention_var,
                     values=["","Passable","Assez Bien","Bien","Très Bien","Excellent"],
                     state="readonly", width=22).grid(
            row=3, column=0, sticky="ew", pady=(0, 6))

        self.msg_var = tk.StringVar()
        tk.Label(body, textvariable=self.msg_var, font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["danger"]).grid(
            row=4, column=0, sticky="w")

        footer = tk.Frame(self, bg=DS["bg_3"], padx=20, pady=12)
        footer.pack(fill="x")
        btn = tk.Button(footer, text="Valider",
                        font=FONTS["btn"], bg=DS["success"],
                        fg="white", relief="flat", bd=0,
                        cursor="hand2", padx=16, pady=8,
                        command=self._save)
        btn.pack(side="left", padx=(0, 8))
        tk.Button(footer, text="Annuler",
                  font=FONTS["btn"], bg=DS["bg_3"],
                  fg=DS["text_secondary"], relief="solid", bd=1,
                  cursor="hand2", padx=14, pady=8,
                  command=self.destroy).pack(side="left")

    def _save(self):
        try:
            note    = float(self.note_var.get())
            mention = self.mention_var.get()
            if self.etype == "Projet":
                from controllers import ProjetController
                ProjetController.noter(self.eid, note, mention)
            else:
                StageController.noter(self.eid, note, mention)
            show_toast(self.master, "Note enregistrée.", "success")
            if self.callback: self.callback()
            self.destroy()
        except ValueError:
            self.msg_var.set("Entrez une note valide (ex: 14.5)")
        except Exception as e:
            self.msg_var.set(str(e))
