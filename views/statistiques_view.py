"""EduTrack – Statistiques v3.0 Dark Corporate"""
import tkinter as tk
from tkinter import ttk
from views.theme import DS, FONTS, UIComponents
from controllers import StatistiquesController


class StatistiquesView(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._content = None
        self._build_shell()
        self.after(60, self.refresh)

    def _build_shell(self):
        toolbar = tk.Frame(self, bg=DS["bg"])
        toolbar.pack(fill="x", padx=28, pady=(20, 0))
        tk.Label(toolbar, text="Statistiques & Analyses",
                 font=FONTS["h1"], bg=DS["bg"],
                 fg=DS["text_primary"]).pack(side="left")
        UIComponents.btn_primary(toolbar, "↺  Actualiser",
                                  command=self.refresh).pack(side="right")
        tk.Frame(self, bg=DS["border"], height=1).pack(
            fill="x", padx=28, pady=14)

        canvas = tk.Canvas(self, bg=DS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._sf = tk.Frame(canvas, bg=DS["bg"])
        self._sf.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._sf, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

    def refresh(self):
        if self._content:
            self._content.destroy()
        self._content = tk.Frame(self._sf, bg=DS["bg"])
        self._content.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        try:
            stats = StatistiquesController.get_dashboard()
        except Exception as e:
            tk.Label(self._content, text=f"Erreur : {e}",
                     font=FONTS["body"], bg=DS["bg"],
                     fg=DS["danger"]).pack(pady=20)
            return
        self._kpis(stats)
        self._moyennes(stats)
        self._charts(stats)
        self._statuts(stats)

    def _section(self, text):
        f = tk.Frame(self._content, bg=DS["bg"])
        f.pack(fill="x", pady=(0, 8))
        r = tk.Frame(f, bg=DS["bg"])
        r.pack(fill="x")
        tk.Label(r, text=text, font=FONTS["h3"],
                 bg=DS["bg"], fg=DS["text_secondary"]).pack(side="left")
        tk.Frame(r, bg=DS["border_bright"], height=1).pack(
            side="left", fill="x", expand=True, padx=(12,0), pady=10)

    def _kpis(self, stats):
        self._section("Indicateurs Clés")
        row = tk.Frame(self._content, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 16))
        kpis = [
            ("◈", stats["total_etudiants"],  "Étudiants",  DS["primary"]),
            ("◉", stats["total_projets"],    "Projets",    DS["purple"]),
            ("◎", stats["total_stages"],     "Stages",     DS["teal"]),
            ("◆", stats["total_professeurs"],"Professeurs",DS["gold"]),
            ("◇", stats["total_entreprises"],"Entreprises",DS["accent"]),
        ]
        for i, (icon, val, label, color) in enumerate(kpis):
            UIComponents.kpi_card(row, icon, val, label, color=color, col=i)
            row.grid_columnconfigure(i, weight=1, uniform="kpi")

    def _moyennes(self, stats):
        self._section("Performances Académiques")
        row = tk.Frame(self._content, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 16))
        items = [
            ("Moyenne Générale", stats.get("moyenne_generale",0), DS["primary"]),
            ("Projets",          stats.get("moy_projets",0),      DS["purple"]),
            ("Stages",           stats.get("moy_stages",0),       DS["teal"]),
        ]
        for i, (label, val, color) in enumerate(items):
            card = tk.Frame(row, bg=DS["card"],
                            highlightbackground=DS["border_bright"],
                            highlightthickness=1)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            row.grid_columnconfigure(i, weight=1)
            tk.Frame(card, bg=color, height=2).pack(fill="x")
            inner = tk.Frame(card, bg=DS["card"], padx=20, pady=16)
            inner.pack(fill="both")
            tk.Label(inner, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"]).pack(anchor="w")
            nc = DS["success"] if (val or 0) >= 10 else DS["danger"]
            tk.Label(inner,
                     text=f"{val:.2f}/20" if val else "N/A",
                     font=FONTS["num"],
                     bg=DS["card"], fg=nc).pack(anchor="w", pady=(6,10))
            # Gauge arc
            cs = 80
            cv = tk.Canvas(inner, width=cs, height=cs,
                           bg=DS["card"], highlightthickness=0)
            cv.pack(anchor="w")
            pct = min((val or 0)/20.0, 1.0)
            cv.create_arc(6, 6, cs-6, cs-6,
                          start=135, extent=270,
                          style="arc", outline=DS["bg_3"], width=8)
            if pct > 0:
                cv.create_arc(6, 6, cs-6, cs-6,
                              start=135, extent=pct*270,
                              style="arc", outline=nc, width=8)
            cv.create_text(cs//2, cs//2,
                           text=f"{int(pct*100)}%",
                           font=FONTS["h4"], fill=nc)

    def _charts(self, stats):
        self._section("Répartition des Étudiants")
        row = tk.Frame(self._content, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        d1 = {d["niveau"]: d["total"]
              for d in stats.get("par_niveau",[]) if d.get("niveau")}
        d2 = {d["filiere"]: d["total"]
              for d in stats.get("par_filiere",[]) if d.get("filiere")}
        self._bar_card(row, "Par Niveau",  d1, DS["primary"], 0)
        self._bar_card(row, "Par Filière", d2, DS["purple"],  1)

    def _bar_card(self, parent, title, data, color, col):
        card = tk.Frame(parent, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        card.grid(row=0, column=col, padx=5, sticky="nsew")
        inner = tk.Frame(card, bg=DS["card"], padx=20, pady=16)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=title, font=FONTS["h3"],
                 bg=DS["card"], fg=DS["text_primary"]).pack(anchor="w")
        tk.Frame(inner, bg=DS["border"], height=1).pack(
            fill="x", pady=(6, 12))
        if not data:
            tk.Label(inner, text="Aucune donnée",
                     font=FONTS["body_sm"], bg=DS["card"],
                     fg=DS["text_muted"]).pack()
            return
        mx = max(data.values(), default=1)
        bw = 280
        for label, val in sorted(data.items()):
            r = tk.Frame(inner, bg=DS["card"])
            r.pack(fill="x", pady=5)
            tk.Label(r, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_secondary"],
                     width=22, anchor="w").pack(side="left")
            track = tk.Frame(r, bg=DS["bg_3"], height=10)
            track.pack(side="left", padx=(8,8))
            track.config(width=bw)
            track.pack_propagate(False)
            fw = max(int((val/mx)*bw), 4)
            tk.Frame(track, bg=color, height=10,
                     width=fw).place(x=0, y=0, relheight=1)
            tk.Label(r, text=str(val), font=FONTS["btn_sm"],
                     bg=DS["card"], fg=color).pack(side="left")

    def _statuts(self, stats):
        self._section("Statuts des Projets & Stages")
        row = tk.Frame(self._content, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        p_data = {d["statut"]: d["total"]
                  for d in stats.get("projets_par_statut",[])}
        s_data = {d["statut"]: d["total"]
                  for d in stats.get("stages_par_statut",[])}
        pc = {"En cours":DS["warning"],"Terminé":DS["success"],"Suspendu":DS["danger"]}
        sc = {"En cours":DS["primary"],"Terminé":DS["success"],"Abandonné":DS["danger"]}
        self._donut(row, "◉  Projets", p_data, pc, 0)
        self._donut(row, "◎  Stages",  s_data, sc, 1)

    def _donut(self, parent, title, data, cmap, col):
        card = tk.Frame(parent, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        card.grid(row=0, column=col, padx=5, sticky="nsew")
        inner = tk.Frame(card, bg=DS["card"], padx=20, pady=16)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=title, font=FONTS["h3"],
                 bg=DS["card"], fg=DS["text_primary"]).pack(anchor="w")
        tk.Frame(inner, bg=DS["border"], height=1).pack(
            fill="x", pady=(6, 12))
        if not data:
            tk.Label(inner, text="Aucune donnée",
                     font=FONTS["body_sm"], bg=DS["card"],
                     fg=DS["text_muted"]).pack()
            return
        body = tk.Frame(inner, bg=DS["card"])
        body.pack(fill="x")
        cs = 160
        cv = tk.Canvas(body, width=cs, height=cs,
                       bg=DS["card"], highlightthickness=0)
        cv.pack(side="left")
        total = sum(data.values()) or 1
        dfl   = [DS["primary"],DS["success"],DS["warning"],DS["danger"],DS["purple"]]
        start = 0.0
        for i, (lbl, val) in enumerate(data.items()):
            color = cmap.get(lbl, dfl[i % len(dfl)])
            ext   = (val/total)*359.9
            cv.create_arc(10, 10, cs-10, cs-10,
                          start=start, extent=ext,
                          fill=color, outline=DS["card"], width=3)
            start += ext
        # Hole
        cv.create_oval(48, 48, cs-48, cs-48,
                       fill=DS["card"], outline=DS["card"])
        cv.create_text(cs//2, cs//2,
                       text=str(total), font=FONTS["h3"],
                       fill=DS["text_primary"])
        legend = tk.Frame(body, bg=DS["card"], padx=16)
        legend.pack(side="left", anchor="center")
        for i, (lbl, val) in enumerate(data.items()):
            color = cmap.get(lbl, dfl[i % len(dfl)])
            pct   = f"{val*100//total}%"
            r = tk.Frame(legend, bg=DS["card"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text="●", fg=color, bg=DS["card"],
                     font=("Segoe UI",12)).pack(side="left", padx=(0,6))
            tk.Label(r, text=lbl, font=FONTS["body"],
                     bg=DS["card"], fg=DS["text_primary"]).pack(side="left")
            tk.Label(r, text=f"  {val} ({pct})",
                     font=FONTS["body_sm"], bg=DS["card"],
                     fg=DS["text_muted"]).pack(side="left")
