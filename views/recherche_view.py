"""EduTrack – Vue Recherche Avancée v2.0"""
import tkinter as tk
from tkinter import ttk
from views.theme import (DS, FONTS, UIComponents, PremiumSearchBar,
                          make_premium_table, fill_premium_table,
                          show_message, show_toast)
from controllers import RechercheController, AnneeController


class RechercheView(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._results = {}
        self._build()
        self._search()

    def _build(self):
        toolbar = tk.Frame(self, bg=DS["bg"])
        toolbar.pack(fill="x", padx=28, pady=(20,0))
        tk.Label(toolbar, text="Recherche Avancée", font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(side="left", anchor="w")
        UIComponents.btn_ghost(toolbar, "📄  Exporter PDF",
                                command=self._export_pdf).pack(side="right")

        tk.Frame(self, bg=DS["border"], height=1).pack(fill="x", padx=28, pady=14)

        # ── Filter panel ──────────────────────────────────────────────────────
        panel = tk.Frame(self, bg=DS["card"],
                         highlightbackground=DS["border"],
                         highlightthickness=1)
        panel.pack(fill="x", padx=28, pady=(0,14))
        inner = tk.Frame(panel, bg=DS["card"], padx=20, pady=16)
        inner.pack(fill="x")

        tk.Label(inner, text="Filtres de recherche", font=FONTS["h3"],
                 bg=DS["card"], fg=DS["text_primary"]).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0,12))

        # Row 1
        tk.Label(inner, text="Mot-clé", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"]).grid(
            row=1, column=0, sticky="w", pady=(0,2))
        self.terme_var = tk.StringVar()
        entry = tk.Entry(inner, textvariable=self.terme_var,
                         font=FONTS["body"], width=28, relief="solid", bd=1,
                         highlightbackground=DS["border"],
                         highlightcolor=DS["primary"], highlightthickness=1)
        entry.grid(row=2, column=0, sticky="ew", padx=(0,12))
        entry.bind("<Return>", lambda e: self._search())

        tk.Label(inner, text="Entité", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"]).grid(
            row=1, column=1, sticky="w", pady=(0,2))
        self.type_var = tk.StringVar(value="Tout")
        ttk.Combobox(inner, textvariable=self.type_var, width=14,
                     values=["Tout","Étudiants","Projets","Stages","Professeurs"],
                     state="readonly").grid(row=2, column=1, sticky="ew", padx=(0,12))

        tk.Label(inner, text="Année", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"]).grid(
            row=1, column=2, sticky="w", pady=(0,2))
        self.annee_var = tk.StringVar(value="Toutes")
        annees = AnneeController.get_annees()
        self._annees_map = {a["libelle"]: a["id"] for a in annees}
        ttk.Combobox(inner, textvariable=self.annee_var, width=12,
                     values=["Toutes"] + list(self._annees_map.keys()),
                     state="readonly").grid(row=2, column=2, sticky="ew", padx=(0,12))

        tk.Label(inner, text="Filière", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"]).grid(
            row=1, column=3, sticky="w", pady=(0,2))
        self.filiere_var = tk.StringVar()
        ttk.Combobox(inner, textvariable=self.filiere_var, width=18,
                     values=["","Informatique","Télécommunication","Génie Logiciel",
                             "Systèmes Embarqués","Réseaux","Intelligence Artificielle"],
                     state="readonly").grid(row=2, column=3, sticky="ew", padx=(0,12))

        tk.Label(inner, text="Statut", font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"]).grid(
            row=1, column=4, sticky="w", pady=(0,2))
        self.statut_var = tk.StringVar()
        ttk.Combobox(inner, textvariable=self.statut_var, width=12,
                     values=["","En cours","Terminé","Suspendu","Abandonné"],
                     state="readonly").grid(row=2, column=4, sticky="ew", padx=(0,12))

        for c in range(5):
            inner.grid_columnconfigure(c, weight=1)

        # Buttons row
        btn_row = tk.Frame(inner, bg=DS["card"])
        btn_row.grid(row=3, column=0, columnspan=6, pady=(14,0), sticky="w")
        UIComponents.btn_primary(btn_row, "🔍  Rechercher",
                                  command=self._search).pack(side="left", padx=(0,8))
        UIComponents.btn_secondary(btn_row, "Réinitialiser",
                                    command=self._reset).pack(side="left")

        # ── Results notebook ──────────────────────────────────────────────────
        self.status_lbl = tk.Label(self, text="", font=FONTS["body_sm"],
                                    bg=DS["bg"], fg=DS["text_muted"])
        self.status_lbl.pack(anchor="w", padx=28, pady=(0,4))

        self.nb = ttk.Notebook(self, style="TNotebook")
        self.nb.pack(fill="both", expand=True, padx=28, pady=(0,20))

        configs = [
            ("etudiants",   "👥 Étudiants",
             ["matricule","nom","prenom","filiere","niveau","email"],
             ["Matricule","Nom","Prénom","Filière","Niveau","Email"],
             [100,130,130,160,80,220]),
            ("projets",     "📁 Projets",
             ["titre","type_projet","annee_libelle","statut","note"],
             ["Titre","Type","Année","Statut","Note"],
             [240,90,110,100,80]),
            ("stages",      "🏢 Stages",
             ["titre","etudiant_nom","entreprise_nom","annee_libelle","statut","note"],
             ["Titre","Étudiant","Entreprise","Année","Statut","Note"],
             [180,140,140,110,90,80]),
            ("professeurs", "👨‍🏫 Professeurs",
             ["matricule","nom","prenom","specialite","grade"],
             ["Matricule","Nom","Prénom","Spécialité","Grade"],
             [100,130,130,200,120]),
        ]
        self._tabs  = {}
        self._trees = {}
        for key, label, cols, hdrs, widths in configs:
            tab = tk.Frame(self.nb, bg=DS["card"])
            self.nb.add(tab, text=f"  {label} (0)  ")
            self._tabs[key]  = tab
            f, tree = make_premium_table(tab, cols, widths, hdrs)
            f.pack(fill="both", expand=True, padx=8, pady=8)
            self._trees[key] = (tree, cols)

    def _search(self):
        terme  = self.terme_var.get().strip()
        type_e = self.type_var.get()
        al     = self.annee_var.get()
        aid    = self._annees_map.get(al) if al != "Toutes" else None
        filiere= self.filiere_var.get()
        niveau = ""
        statut = self.statut_var.get()
        try:
            self._results = RechercheController.recherche_avancee(
                terme=terme, type_entite=type_e,
                annee_id=aid, filiere=filiere,
                niveau=niveau, statut=statut)
        except Exception as e:
            show_message(self, "Erreur", str(e), "error")
            return

        icons = {"etudiants":"👥 Étudiants","projets":"📁 Projets",
                 "stages":"🏢 Stages","professeurs":"👨‍🏫 Professeurs"}
        total = 0
        for i, (key, (tree, cols)) in enumerate(self._trees.items()):
            data = self._results.get(key, [])
            fill_premium_table(tree, data, cols)
            cnt = len(data)
            total += cnt
            try:
                self.nb.tab(i, text=f"  {icons[key]} ({cnt})  ")
            except Exception:
                pass

        term_str = f'"{terme}"' if terme else "tout"
        self.status_lbl.config(
            text=f"{total} résultat(s) trouvé(s) pour {term_str}")

    def _reset(self):
        self.terme_var.set("")
        self.type_var.set("Tout")
        self.annee_var.set("Toutes")
        self.filiere_var.set("")
        self.statut_var.set("")
        self._search()

    def _export_pdf(self):
        if not self._results:
            show_message(self, "Info", "Lancez d'abord une recherche.", "warning")
            return
        try:
            from utils.pdf_export import export_resultats_recherche
            terme = self.terme_var.get().strip() or "Tous"
            fp = export_resultats_recherche(self._results, terme)
            show_toast(self, "PDF généré.", "success")
            show_message(self, "Export PDF", f"Fichier :\n{fp}")
        except Exception as e:
            show_message(self, "Erreur PDF", str(e), "error")
