"""EduTrack — Vue Projets v3.1 (Windows-compatible forms)"""
import tkinter as tk
from tkinter import ttk
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, confirm_delete, show_toast)
from controllers import (ProjetController, EtudiantController,
                          ProfesseurController, AnneeController)
from models import Projet
from views.stage_view import NoteDialog

COLS    = ["id","titre","type_projet","annee_libelle",
           "semestre_numero","statut","note","mention"]
HEADERS = ["ID","Titre","Type","Année","Sem.","Statut","Note","Mention"]
WIDTHS  = [40, 220, 90, 110, 50, 90, 60, 110]


class ProjetView(tk.Frame):
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
        tk.Label(left, text="Projets", font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(anchor="w")
        self.count_lbl = tk.Label(left, text="", font=FONTS["body_sm"],
                                   bg=DS["bg"], fg=DS["text_muted"])
        self.count_lbl.pack(anchor="w")
        right = tk.Frame(toolbar, bg=DS["bg"])
        right.pack(side="right")
        UIComponents.btn_primary(right, "+ Nouveau projet",
                                  command=self._open_add).pack(side="left", padx=(0, 8))
        UIComponents.btn_ghost(right, "PDF", command=self._export_pdf).pack(side="left")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x", padx=28, pady=14)

        flt = tk.Frame(self, bg=DS["bg"])
        flt.pack(fill="x", padx=28, pady=(0, 12))
        self.search = PremiumSearchBar(flt, "Rechercher un projet...",
                                       on_change=self._on_search, bg=DS["bg"])
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(flt, text="Type", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.type_var = tk.StringVar()
        ttk.Combobox(flt, textvariable=self.type_var, width=10,
                     values=[""] + Projet.TYPES, state="readonly").pack(
            side="left", padx=(4, 12))
        self.type_var.trace_add("write", lambda *a: self._on_search(""))

        tk.Label(flt, text="Statut", font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(side="left")
        self.statut_var = tk.StringVar()
        ttk.Combobox(flt, textvariable=self.statut_var, width=12,
                     values=[""] + Projet.STATUTS, state="readonly").pack(
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
        for text, cmd in [
            ("Modifier",  self._open_edit),
            ("Détail",    self._open_detail),
            ("Noter",     self._noter),
        ]:
            UIComponents.btn_secondary(actions, text,
                                        command=cmd).pack(side="left", padx=(0, 8))
        UIComponents.btn_danger(actions, "Supprimer",
                                 command=self._delete).pack(side="left")

    def _load(self, data=None):
        try:
            self._data = data if data is not None else ProjetController.get_liste()
            fill_premium_table(self.tree, self._data, COLS)
            n = len(self._data)
            self.count_lbl.config(text=f"{n} projet{'s' if n > 1 else ''}")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _on_search(self, terme=""):
        terme  = self.search.get()
        tp     = self.type_var.get()
        st     = self.statut_var.get()
        al     = self.annee_var.get()
        aid    = self._annees_map.get(al) if al != "Toutes" else None
        try:
            r = ProjetController.rechercher(terme, tp, st, aid)
            fill_premium_table(self.tree, r, COLS)
            self.count_lbl.config(text=f"{len(r)} résultat(s)")
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _reset(self):
        self.type_var.set("")
        self.statut_var.set("")
        self.annee_var.set("Toutes")
        self.search.clear()
        self._load()

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            show_message(self, "Sélection", "Sélectionnez un projet.", "warning")
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _open_add(self):
        w = ProjetForm(self, on_save=self._load)
        w.grab_set(); w.focus_force()

    def _open_edit(self):
        pid = self._get_id()
        if not pid: return
        try:
            d = ProjetController.get_detail(pid)
            w = ProjetForm(self, projet=d["projet"],
                           etudiants=d["etudiants"],
                           jury=d["jury"],
                           on_save=self._load)
            w.grab_set(); w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _delete(self):
        pid = self._get_id()
        if not pid: return
        sel   = self.tree.selection()
        titre = self.tree.item(sel[0])["values"][1]
        if confirm_delete(self, titre):
            try:
                ProjetController.supprimer(pid)
                self._load()
                show_toast(self, "Projet supprimé.", "success")
            except Exception as e:
                show_message(self, "Erreur", str(e), "error")

    def _open_detail(self):
        pid = self._get_id()
        if not pid: return
        try:
            d = ProjetController.get_detail(pid)
            w = ProjetDetail(self, d)
            w.grab_set(); w.focus_force()
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")

    def _noter(self):
        pid = self._get_id()
        if not pid: return
        w = NoteDialog(self, "Projet", pid, callback=self._load)
        w.grab_set(); w.focus_force()

    def _export_pdf(self):
        try:
            from utils.pdf_export import export_liste_projets
            fp = export_liste_projets(self._data)
            show_toast(self, "PDF généré.", "success")
            show_message(self, "Export", f"Fichier :\n{fp}")
        except Exception as e:
            show_message(self, "Erreur PDF", str(e), "error")


# ══════════════════════════════════════════════════════════════════════════════
#  FORMULAIRE PROJET
# ══════════════════════════════════════════════════════════════════════════════

class ProjetForm(tk.Toplevel):
    def __init__(self, parent, projet=None, etudiants=None,
                 jury=None, on_save=None):
        super().__init__(parent)
        self.projet    = projet
        self._et_init  = list(etudiants or [])
        self._jr_init  = list(jury or [])
        self.on_save   = on_save
        self.title("Modifier le projet" if projet else "Nouveau projet")
        self.geometry("800x620")
        self.resizable(True, True)
        self.configure(bg=DS["card"])
        x = (self.winfo_screenwidth()  - 800) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"800x620+{x}+{y}")
        self._build()
        self.lift(); self.focus_force()

    def _build(self):
        p = self.projet or {}

        # Header
        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=16)
        hdr.pack(fill="x")
        title = "Modifier le projet" if self.projet else "Nouveau projet"
        tk.Label(hdr, text=title, font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(hdr, text=p.get("titre", "Créer un nouveau projet académique"),
                 font=FONTS["body_sm"], bg="#0F172A",
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=8)

        # Tab 1: Informations
        t1 = tk.Frame(nb, bg=DS["card"])
        nb.add(t1, text="  Informations  ")
        self._build_info_tab(t1, p)

        # Tab 2: Étudiants
        t2 = tk.Frame(nb, bg=DS["card"])
        nb.add(t2, text="  Étudiants  ")
        self._build_members_tab(t2, "etudiants")

        # Tab 3: Jury
        t3 = tk.Frame(nb, bg=DS["card"])
        nb.add(t3, text="  Jury  ")
        self._build_members_tab(t3, "jury")

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

        self.msg_var = tk.StringVar()
        tk.Label(footer, textvariable=self.msg_var,
                 font=FONTS["body_sm"], bg=DS["bg_3"],
                 fg=DS["danger"]).pack(side="left", padx=(16, 0))

    def _build_info_tab(self, parent, p):
        body = tk.Frame(parent, bg=DS["card"], padx=20, pady=16)
        body.pack(fill="both", expand=True)

        annees = AnneeController.get_annees()
        self._annee_map = {a["libelle"]: a["id"] for a in annees}
        self._annee_rev = {a["id"]: a["libelle"] for a in annees}
        self.pvars = {}

        left  = tk.Frame(body, bg=DS["card"])
        right = tk.Frame(body, bg=DS["card"])
        left.grid(row=0, column=0, sticky="n", padx=(0, 20))
        right.grid(row=0, column=1, sticky="n")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        def txt(parent, label, key, row, val=""):
            tk.Label(parent, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=row, column=0, sticky="w", pady=(6, 1))
            var = tk.StringVar(value=str(p.get(key, val) or ""))
            e = tk.Entry(parent, textvariable=var, font=FONTS["body"],
                         bg=DS["bg_3"], fg=DS["text_primary"],
                         insertbackground=DS["primary"],
                         relief="solid", bd=1, width=26)
            e.grid(row=row+1, column=0, sticky="ew", pady=(0, 2), ipady=6)
            self.pvars[key] = var

        def combo(parent, label, values, key, default, row):
            tk.Label(parent, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w").grid(row=row, column=0, sticky="w", pady=(6, 1))
            var = tk.StringVar(value=str(default))
            cb  = ttk.Combobox(parent, textvariable=var,
                                values=values, state="readonly", width=24)
            cb.grid(row=row+1, column=0, sticky="ew", pady=(0, 2))
            self.pvars[key] = var

        txt(left, "Titre *", "titre", 0)
        combo(left, "Type", Projet.TYPES, "type_projet",
              p.get("type_projet", Projet.TYPES[0]), 2)
        combo(left, "Statut", Projet.STATUTS, "statut",
              p.get("statut", "En cours"), 4)

        combo(right, "Année universitaire *",
              list(self._annee_map.keys()), "annee",
              self._annee_rev.get(p.get("annee_id", ""), ""), 0)
        txt(right, "Date début (AAAA-MM-JJ)", "date_debut", 2)
        txt(right, "Date fin (AAAA-MM-JJ)",   "date_fin",   4)

        # Description
        tk.Label(left, text="Description", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"],
                 anchor="w").grid(row=6, column=0, sticky="w", pady=(6, 1))
        self.desc_text = tk.Text(left, height=4, font=FONTS["body"],
                                  bg=DS["bg_3"], fg=DS["text_primary"],
                                  insertbackground=DS["primary"],
                                  relief="solid", bd=1, width=26,
                                  wrap="word")
        self.desc_text.grid(row=7, column=0, sticky="ew", pady=(0, 2))
        self.desc_text.insert("1.0", p.get("description", "") or "")
        left.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

    def _build_members_tab(self, parent, mode):
        frame = tk.Frame(parent, bg=DS["card"], padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        if mode == "etudiants":
            all_items = EtudiantController.get_liste()
            label_fn  = lambda x: f"{x['matricule']} – {x['nom']} {x['prenom']}"
            current   = {m["id"]: m.get("role","Membre") for m in self._et_init}
            src_attr  = "_et_src"; dst_attr = "_et_dst"; all_attr = "_et_all"
        else:
            all_items = ProfesseurController.get_liste()
            label_fn  = lambda x: f"{x['matricule']} – {x['nom']} {x['prenom']}"
            current   = {m["id"]: m.get("jury_role","Membre") for m in self._jr_init}
            src_attr  = "_jr_src"; dst_attr = "_jr_dst"; all_attr = "_jr_all"

        setattr(self, all_attr, all_items)

        # Available list
        lf1 = tk.LabelFrame(frame, text=" Disponibles ",
                            font=FONTS["h4"], bg=DS["card"],
                            fg=DS["text_secondary"])
        lf1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        lb_src = tk.Listbox(lf1, font=FONTS["body"],
                             selectmode="extended", height=14,
                             bg=DS["bg_3"], fg=DS["text_primary"],
                             selectbackground=DS["primary"],
                             selectforeground="white",
                             relief="flat", bd=0,
                             highlightthickness=0)
        sb1 = ttk.Scrollbar(lf1, orient="vertical", command=lb_src.yview)
        lb_src.config(yscrollcommand=sb1.set)
        lb_src.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        sb1.pack(side="right", fill="y")

        for item in all_items:
            if item["id"] not in current:
                lb_src.insert("end", label_fn(item))
        setattr(self, src_attr, lb_src)

        # Arrows
        mid = tk.Frame(frame, bg=DS["card"])
        mid.grid(row=0, column=1, padx=8)

        def add_m():
            src = getattr(self, src_attr)
            dst = getattr(self, dst_attr)
            for i in reversed(src.curselection()):
                t = src.get(i); src.delete(i)
                dst.insert("end", t + " [Membre]")

        def rem_m():
            src = getattr(self, src_attr)
            dst = getattr(self, dst_attr)
            for i in reversed(dst.curselection()):
                t = dst.get(i).split(" [")[0]; dst.delete(i)
                src.insert("end", t)

        btn_add = tk.Button(mid, text="→", font=FONTS["h3"],
                             bg=DS["primary"], fg="white",
                             relief="flat", cursor="hand2",
                             width=3, command=add_m)
        btn_add.pack(pady=4)
        btn_rem = tk.Button(mid, text="←", font=FONTS["h3"],
                             bg=DS["danger_light"], fg=DS["danger"],
                             relief="flat", cursor="hand2",
                             width=3, command=rem_m)
        btn_rem.pack(pady=4)

        # Selected list
        lf2 = tk.LabelFrame(frame, text=" Sélectionnés ",
                            font=FONTS["h4"], bg=DS["card"],
                            fg=DS["text_secondary"])
        lf2.grid(row=0, column=2, sticky="nsew")

        lb_dst = tk.Listbox(lf2, font=FONTS["body"], height=14,
                             bg=DS["bg_3"], fg=DS["text_primary"],
                             selectbackground=DS["primary"],
                             selectforeground="white",
                             relief="flat", bd=0,
                             highlightthickness=0)
        sb2 = ttk.Scrollbar(lf2, orient="vertical", command=lb_dst.yview)
        lb_dst.config(yscrollcommand=sb2.set)
        lb_dst.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        sb2.pack(side="right", fill="y")

        for item in all_items:
            if item["id"] in current:
                lb_dst.insert("end", f"{label_fn(item)} [{current[item['id']]}]")
        setattr(self, dst_attr, lb_dst)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)

    def _save(self):
        try:
            titre    = self.pvars["titre"].get().strip()
            al       = self.pvars["annee"].get()
            annee_id = self._annee_map.get(al)
            if not titre:
                self.msg_var.set("Le titre est obligatoire.")
                return
            if not annee_id:
                self.msg_var.set("Sélectionnez une année universitaire.")
                return

            description = self.desc_text.get("1.0", "end").strip()
            kw = dict(
                type_projet=self.pvars["type_projet"].get(),
                statut=self.pvars["statut"].get(),
                date_debut=self.pvars["date_debut"].get(),
                date_fin=self.pvars["date_fin"].get())

            if self.projet:
                ProjetController.modifier(self.projet["id"],
                    annee_id=annee_id, description=description,
                    titre=titre, **kw)
                pid = self.projet["id"]
            else:
                pid = ProjetController.ajouter(
                    titre, annee_id, description=description, **kw)

            # Associate students
            et_ids = []
            for t in [self._et_dst.get(i) for i in range(self._et_dst.size())]:
                mat  = t.split(" – ")[0]
                role = t.split("[")[-1].rstrip("]") if "[" in t else "Membre"
                for e in self._et_all:
                    if e["matricule"] == mat:
                        et_ids.append((e["id"], role)); break
            ProjetController.associer_etudiants(pid, et_ids)

            # Associate jury
            jr_ids = []
            for t in [self._jr_dst.get(i) for i in range(self._jr_dst.size())]:
                mat  = t.split(" – ")[0]
                role = t.split("[")[-1].rstrip("]") if "[" in t else "Membre"
                for p in self._jr_all:
                    if p["matricule"] == mat:
                        jr_ids.append((p["id"], role)); break
            ProjetController.associer_jury(pid, jr_ids)

            show_toast(self.master, "Projet enregistré.", "success")
            if self.on_save: self.on_save()
            self.destroy()
        except Exception as e:
            self.msg_var.set(str(e))


class ProjetDetail(tk.Toplevel):
    def __init__(self, parent, detail):
        super().__init__(parent)
        self.detail = detail
        p = detail["projet"]
        self.title(f"Projet – {p['titre']}")
        self.geometry("780x520")
        self.configure(bg=DS["bg"])
        x = (self.winfo_screenwidth()  - 780) // 2
        y = (self.winfo_screenheight() - 520) // 2
        self.geometry(f"780x520+{x}+{y}")
        self._build()
        self.lift()

    def _build(self):
        p  = self.detail["projet"]
        et = self.detail.get("etudiants", [])
        jr = self.detail.get("jury", [])

        hdr = tk.Frame(self, bg="#0F172A", padx=24, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text=p["titre"], font=FONTS["h2"],
                 bg="#0F172A", fg=DS["text_primary"]).pack(side="left", anchor="w")
        if p.get("note"):
            nf = tk.Frame(hdr, bg=DS["success"], padx=12, pady=6)
            nf.pack(side="right")
            tk.Label(nf,
                     text=f"{p['note']:.1f}/20  {p.get('mention','')}",
                     font=FONTS["h3"], bg=DS["success"], fg="white").pack()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        t1 = tk.Frame(nb, bg=DS["card"], padx=20, pady=16)
        nb.add(t1, text="  Informations  ")
        infos = [
            ("Type",        p.get("type_projet","")),
            ("Année",       p.get("annee_libelle","")),
            ("Semestre",    p.get("semestre_numero","")),
            ("Statut",      p.get("statut","")),
            ("Début",       p.get("date_debut","")),
            ("Fin",         p.get("date_fin","")),
            ("Description", p.get("description","")),
        ]
        for i, (k, v) in enumerate(infos):
            tk.Label(t1, text=k+":", font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"],
                     anchor="w", width=14).grid(row=i, column=0, sticky="w", pady=5)
            tk.Label(t1, text=str(v or "—"), font=FONTS["body"],
                     bg=DS["card"], anchor="w").grid(row=i, column=1, sticky="w", padx=12)

        t2 = tk.Frame(nb, bg=DS["card"])
        nb.add(t2, text=f"  Étudiants ({len(et)})  ")
        f1, tr1 = make_premium_table(t2,
            ["matricule","nom","prenom","role"],
            [100,130,130,120], ["Matricule","Nom","Prénom","Rôle"])
        f1.pack(fill="both", expand=True, padx=8, pady=8)
        fill_premium_table(tr1, et, ["matricule","nom","prenom","role"])

        t3 = tk.Frame(nb, bg=DS["card"])
        nb.add(t3, text=f"  Jury ({len(jr)})  ")
        f2, tr2 = make_premium_table(t3,
            ["matricule","nom","prenom","jury_role"],
            [100,130,130,130], ["Matricule","Nom","Prénom","Rôle"])
        f2.pack(fill="both", expand=True, padx=8, pady=8)
        fill_premium_table(tr2, jr, ["matricule","nom","prenom","jury_role"])

        footer = tk.Frame(self, bg=DS["bg_3"], padx=20, pady=12)
        footer.pack(fill="x")
        tk.Button(footer, text="Fermer", font=FONTS["btn"],
                  bg=DS["bg_3"], fg=DS["text_secondary"],
                  relief="solid", bd=1, cursor="hand2",
                  padx=14, pady=7, command=self.destroy).pack(side="left")
