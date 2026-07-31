"""EduTrack Dashboard v3.0 — Dark Corporate"""
import tkinter as tk
from tkinter import ttk
from views.theme import DS, FONTS, UIComponents, show_message
from controllers import StatistiquesController


class DashboardView(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", DS["bg"])
        super().__init__(parent, **kw)
        self._canvas  = None
        self._sf      = None
        self._inner   = None
        self._build_shell()
        self.after(60, self.refresh)

    def _build_shell(self):
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
            lambda e: canvas.yview_scroll(
                -1*(e.delta//120), "units"))
        self._canvas = canvas

    def refresh(self):
        if self._inner:
            self._inner.destroy()
        self._inner = tk.Frame(self._sf, bg=DS["bg"])
        self._inner.pack(fill="both", expand=True,
                         padx=28, pady=(20, 28))
        try:
            stats = StatistiquesController.get_dashboard()
        except Exception as e:
            tk.Label(self._inner, text=f"Erreur : {e}",
                     font=FONTS["body"], bg=DS["bg"],
                     fg=DS["danger"]).pack(pady=20)
            return
        self._header()
        self._kpis(stats)
        self._row2(stats)
        self._row3(stats)

    # ── Header ────────────────────────────────────────────────────────────────
    def _header(self):
        from datetime import datetime
        row = tk.Frame(self._inner, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 22))

        left = tk.Frame(row, bg=DS["bg"])
        left.pack(side="left")
        tk.Label(left, text="Tableau de Bord",
                 font=FONTS["h1"],
                 bg=DS["bg"], fg=DS["text_primary"]).pack(anchor="w")
        day = datetime.now().strftime("%A %d %B %Y").capitalize()
        tk.Label(left, text=day,
                 font=FONTS["body_sm"],
                 bg=DS["bg"], fg=DS["text_muted"]).pack(anchor="w", pady=(2,0))

        right = tk.Frame(row, bg=DS["bg"])
        right.pack(side="right")
        UIComponents.btn_primary(right, "↺  Actualiser",
                                  command=self.refresh).pack()

    # ── KPI Row ───────────────────────────────────────────────────────────────
    def _kpis(self, stats):
        row = tk.Frame(self._inner, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 16))
        kpis = [
            ("◈", stats["total_etudiants"],  "Étudiants",  DS["primary"]),
            ("◉", stats["total_projets"],    "Projets",    DS["purple"]),
            ("◎", stats["total_stages"],     "Stages",     DS["teal"]),
            ("◆", stats["total_professeurs"],"Professeurs",DS["gold"]),
            ("◇", stats["total_entreprises"],"Entreprises",DS["accent"]),
        ]
        for i, (icon, val, label, color) in enumerate(kpis):
            UIComponents.kpi_card(row, icon, val, label,
                                   color=color, col=i)
            row.grid_columnconfigure(i, weight=1, uniform="kpi")

    # ── Row 2: Distribution + Performances ───────────────────────────────────
    def _row2(self, stats):
        row = tk.Frame(self._inner, bg=DS["bg"])
        row.pack(fill="x", pady=(0, 16))
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        # Left: Distribution
        left = tk.Frame(row, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        left.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self._distribution(left, stats)

        # Right: Performances
        right = tk.Frame(row, bg=DS["card"],
                         highlightbackground=DS["border_bright"],
                         highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        self._performances(right, stats)

    def _distribution(self, parent, stats):
        inner = tk.Frame(parent, bg=DS["card"], padx=20, pady=16)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Distribution des Étudiants",
                 font=FONTS["h3"], bg=DS["card"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(inner, text="Répartition par niveau et filière",
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 12))

        nb = ttk.Notebook(inner)
        nb.pack(fill="both", expand=True)

        t1 = tk.Frame(nb, bg=DS["card"])
        nb.add(t1, text="  Par Niveau  ")
        d1 = {d["niveau"]: d["total"]
              for d in stats.get("par_niveau", [])
              if d.get("niveau")}
        self._bars(t1, d1, DS["primary"])

        t2 = tk.Frame(nb, bg=DS["card"])
        nb.add(t2, text="  Par Filière  ")
        d2 = {d["filiere"]: d["total"]
              for d in stats.get("par_filiere", [])
              if d.get("filiere")}
        self._bars(t2, d2, DS["purple"])

    def _bars(self, parent, data, color):
        f = tk.Frame(parent, bg=DS["card"], padx=8, pady=10)
        f.pack(fill="both", expand=True)
        if not data:
            tk.Label(f, text="Aucune donnée",
                     font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_muted"]).pack(pady=16)
            return
        mx = max(data.values(), default=1)
        bar_w = 240
        for label, val in sorted(data.items()):
            r = tk.Frame(f, bg=DS["card"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_secondary"],
                     width=20, anchor="w").pack(side="left")
            track = tk.Frame(r, bg=DS["bg_3"], height=10)
            track.pack(side="left", padx=(8,8))
            track.config(width=bar_w)
            track.pack_propagate(False)
            fw = max(int((val/mx)*bar_w), 4)
            tk.Frame(track, bg=color, height=10,
                     width=fw).place(x=0, y=0, relheight=1)
            tk.Label(r, text=str(val),
                     font=FONTS["btn_sm"],
                     bg=DS["card"], fg=color).pack(side="left")

    def _performances(self, parent, stats):
        inner = tk.Frame(parent, bg=DS["card"], padx=20, pady=16)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="Performances",
                 font=FONTS["h3"], bg=DS["card"],
                 fg=DS["text_primary"]).pack(anchor="w")
        tk.Label(inner, text="Moyennes calculées",
                 font=FONTS["body_sm"], bg=DS["card"],
                 fg=DS["text_muted"]).pack(anchor="w", pady=(2, 14))

        items = [
            ("Moyenne Générale", stats.get("moyenne_generale", 0), DS["primary"]),
            ("Projets",          stats.get("moy_projets", 0),      DS["purple"]),
            ("Stages",           stats.get("moy_stages", 0),       DS["teal"]),
        ]
        for label, val, color in items:
            f = tk.Frame(inner, bg=DS["card"])
            f.pack(fill="x", pady=8)

            hdr = tk.Frame(f, bg=DS["card"])
            hdr.pack(fill="x")
            tk.Label(hdr, text=label, font=FONTS["body_sm"],
                     bg=DS["card"], fg=DS["text_secondary"]).pack(side="left")
            nc = DS["success"] if (val or 0) >= 10 else DS["danger"]
            ns = f"{val:.2f}/20" if val else "N/A"
            tk.Label(hdr, text=ns, font=FONTS["h4"],
                     bg=DS["card"], fg=nc).pack(side="right")

            # Progress bar
            pct = min((val or 0)/20.0, 1.0)
            track = tk.Frame(f, bg=DS["bg_3"], height=5)
            track.pack(fill="x", pady=(4, 0))
            track.pack_propagate(False)
            if pct > 0:
                tk.Frame(track, bg=nc,
                         height=5).place(x=0, y=0,
                                         relwidth=pct, relheight=1)

    # ── Row 3: Statuts ────────────────────────────────────────────────────────
    def _row3(self, stats):
        row = tk.Frame(self._inner, bg=DS["bg"])
        row.pack(fill="x")
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        p_data = {d["statut"]: d["total"]
                  for d in stats.get("projets_par_statut", [])}
        s_data = {d["statut"]: d["total"]
                  for d in stats.get("stages_par_statut", [])}

        p_colors = {"En cours": DS["warning"],
                    "Terminé":  DS["success"],
                    "Suspendu": DS["danger"]}
        s_colors = {"En cours": DS["primary"],
                    "Terminé":  DS["success"],
                    "Abandonné":DS["danger"]}

        self._status_panel(row, "◉  Statuts Projets",
                           p_data, p_colors, 0)
        self._status_panel(row, "◎  Statuts Stages",
                           s_data, s_colors, 1)

    def _status_panel(self, parent, title, data, color_map, col):
        card = tk.Frame(parent, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        card.grid(row=0, column=col, padx=5 if col else (0,5),
                  sticky="nsew")
        inner = tk.Frame(card, bg=DS["card"], padx=20, pady=16)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text=title, font=FONTS["h3"],
                 bg=DS["card"], fg=DS["text_primary"]).pack(anchor="w")
        tk.Frame(inner, bg=DS["border"],
                 height=1).pack(fill="x", pady=(8, 12))

        if not data:
            tk.Label(inner, text="Aucune donnée",
                     font=FONTS["body_sm"], bg=DS["card"],
                     fg=DS["text_muted"]).pack()
            return

        total = sum(data.values()) or 1
        dfl = [DS["primary"], DS["purple"], DS["teal"]]
        for i, (status, cnt) in enumerate(data.items()):
            color = color_map.get(status, dfl[i % len(dfl)])
            pct   = cnt * 100 // total
            f = tk.Frame(inner, bg=DS["card"])
            f.pack(fill="x", pady=5)

            # Colored dot + label
            dot_f = tk.Frame(f, bg=DS["card"])
            dot_f.pack(side="left", fill="x", expand=True)
            tk.Label(dot_f, text="●", fg=color, bg=DS["card"],
                     font=("Segoe UI", 9)).pack(side="left")
            tk.Label(dot_f, text=f"  {status}",
                     font=FONTS["body"], bg=DS["card"],
                     fg=DS["text_primary"]).pack(side="left")

            tk.Label(f, text=f"{cnt}  {pct}%",
                     font=FONTS["h4"], bg=DS["card"],
                     fg=color).pack(side="right")

            # Progress bar
            track = tk.Frame(dot_f, bg=DS["bg_3"], height=3)
            track.pack(fill="x", pady=(4, 0))
            if pct > 0:
                tk.Frame(track, bg=color,
                         height=3).place(x=0, y=0,
                                         relwidth=pct/100,
                                         relheight=1)
