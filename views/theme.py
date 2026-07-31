"""
EduTrack Design System v3.0 — Dark Corporate Premium
Inspired by Bloomberg Terminal, Palantir Foundry, JetBrains Fleet.
"""

import tkinter as tk
from tkinter import ttk


# ══════════════════════════════════════════════════════════════════════════════
#  DARK CORPORATE PALETTE
# ══════════════════════════════════════════════════════════════════════════════

DS = {
    # ── Backgrounds (layered depth) ──────────────────────────────────────────
    "bg":               "#0A0E1A",   # Base — deepest navy black
    "bg_2":             "#0F1629",   # Surface
    "bg_3":             "#141D35",   # Elevated
    "card":             "#1A2540",   # Card background
    "card_hover":       "#1F2D4D",   # Card on hover
    "sidebar_bg":       "#080C17",   # Sidebar — darkest
    "topbar_bg":        "#0F1629",   # Topbar

    # ── Brand — Electric Blue ─────────────────────────────────────────────────
    "primary":          "#3B82F6",   # Electric blue
    "primary_hover":    "#2563EB",
    "primary_dark":     "#1D4ED8",
    "primary_glow":     "#0D1F3C",   # Deep blue (no alpha)
    "primary_light":    "#1E3A5F",   # Muted blue bg

    # ── Accent — Cyan ────────────────────────────────────────────────────────
    "accent":           "#06B6D4",   # Cyan
    "accent_hover":     "#0891B2",
    "accent_light":     "#0E3544",

    # ── Semantic ─────────────────────────────────────────────────────────────
    "success":          "#10B981",   # Emerald
    "success_light":    "#0D2B22",
    "success_mid":      "#064E3B",
    "warning":          "#F59E0B",   # Amber
    "warning_light":    "#2D1F07",
    "warning_mid":      "#451A03",
    "danger":           "#EF4444",   # Red
    "danger_hover":     "#DC2626",
    "danger_light":     "#2D1010",
    "danger_mid":       "#450A0A",
    "purple":           "#A855F7",   # Violet
    "purple_light":     "#2D1B4E",
    "teal":             "#14B8A6",
    "teal_light":       "#0D2D2A",
    "orange":           "#F97316",
    "orange_light":     "#2D1507",
    "gold":             "#EAB308",
    "gold_light":       "#2D2407",

    # ── Text ─────────────────────────────────────────────────────────────────
    "text_primary":     "#F1F5F9",   # Near white
    "text_secondary":   "#94A3B8",   # Slate 400
    "text_muted":       "#475569",   # Slate 600
    "text_dim":         "#334155",   # Very dim
    "white":            "#FFFFFF",

    # ── Borders & Separators ─────────────────────────────────────────────────
    "border":           "#1E293B",   # Subtle border
    "border_bright":    "#2D3F5E",   # Visible border
    "border_focus":     "#3B82F6",

    # ── Sidebar specific ─────────────────────────────────────────────────────
    "sidebar_text":     "#64748B",
    "sidebar_text_act": "#F1F5F9",
    "sidebar_active":   "#1E3A5F",
    "sidebar_hover":    "#111827",
    "sidebar_indicator":"#3B82F6",

    # ── Table rows ───────────────────────────────────────────────────────────
    "row_even":         "#1A2540",
    "row_odd":          "#151E38",
    "row_selected":     "#1E3A5F",
}

FONTS = {
    "h1":         ("Segoe UI", 20, "bold"),
    "h2":         ("Segoe UI", 16, "bold"),
    "h3":         ("Segoe UI", 12, "bold"),
    "h4":         ("Segoe UI", 10, "bold"),
    "body_lg":    ("Segoe UI", 11),
    "body":       ("Segoe UI", 10),
    "body_sm":    ("Segoe UI", 9),
    "caption":    ("Segoe UI", 8),
    "mono":       ("Consolas", 10),
    "mono_sm":    ("Consolas", 9),
    "btn_lg":     ("Segoe UI", 11, "bold"),
    "btn":        ("Segoe UI", 10, "bold"),
    "btn_sm":     ("Segoe UI", 9, "bold"),
    "sidebar":    ("Segoe UI", 10),
    "sidebar_h":  ("Segoe UI", 10, "bold"),
    "badge":      ("Segoe UI", 8, "bold"),
    "num":        ("Segoe UI", 22, "bold"),
    "num_lg":     ("Segoe UI", 30, "bold"),
    "label":      ("Segoe UI", 9),
}


def apply_theme(root):
    """Configure ttk styles — full dark theme."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Treeview ──────────────────────────────────────────────────────────────
    style.configure("Treeview",
                    background=DS["row_even"],
                    foreground=DS["text_primary"],
                    fieldbackground=DS["row_even"],
                    rowheight=36,
                    font=FONTS["body"],
                    borderwidth=0,
                    relief="flat")
    style.configure("Treeview.Heading",
                    background=DS["bg_3"],
                    foreground=DS["text_secondary"],
                    font=FONTS["h4"],
                    relief="flat",
                    padding=(12, 9))
    style.map("Treeview",
              background=[("selected", DS["row_selected"])],
              foreground=[("selected", DS["primary"])])
    style.map("Treeview.Heading",
              background=[("active", DS["card_hover"])])

    # ── Scrollbar ─────────────────────────────────────────────────────────────
    style.configure("Dark.Vertical.TScrollbar",
                    background=DS["border"],
                    troughcolor=DS["bg_2"],
                    arrowcolor=DS["text_muted"],
                    borderwidth=0,
                    width=6)
    style.configure("Vertical.TScrollbar",
                    background=DS["border"],
                    troughcolor=DS["bg_2"],
                    borderwidth=0, width=6)

    # ── Notebook ──────────────────────────────────────────────────────────────
    style.configure("TNotebook",
                    background=DS["card"],
                    borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=DS["bg_3"],
                    foreground=DS["text_muted"],
                    font=FONTS["body"],
                    padding=[14, 8],
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", DS["card"])],
              foreground=[("selected", DS["primary"])],
              font=[("selected", FONTS["h4"])])

    # ── Combobox ──────────────────────────────────────────────────────────────
    style.configure("TCombobox",
                    fieldbackground=DS["bg_3"],
                    background=DS["bg_3"],
                    foreground=DS["text_primary"],
                    arrowcolor=DS["text_muted"],
                    selectbackground=DS["bg_3"],
                    selectforeground=DS["text_primary"],
                    padding=(8, 6),
                    borderwidth=1,
                    relief="solid")
    style.map("TCombobox",
              fieldbackground=[("readonly", DS["bg_3"])],
              selectbackground=[("readonly", DS["bg_3"])],
              selectforeground=[("readonly", DS["text_primary"])])

    # ── Progressbar ──────────────────────────────────────────────────────────
    style.configure("Blue.Horizontal.TProgressbar",
                    background=DS["primary"],
                    troughcolor=DS["bg_3"],
                    borderwidth=0, thickness=4)
    style.configure("Green.Horizontal.TProgressbar",
                    background=DS["success"],
                    troughcolor=DS["bg_3"],
                    borderwidth=0, thickness=4)

    # ── Canvas/Frame bg ───────────────────────────────────────────────────────
    root.configure(bg=DS["bg"])


# ══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENT LIBRARY
# ══════════════════════════════════════════════════════════════════════════════

class UIComponents:

    @staticmethod
    def card(parent, padding=(20, 16), **kw):
        kw.setdefault("bg", DS["card"])
        f = tk.Frame(parent, **kw,
                     highlightbackground=DS["border_bright"],
                     highlightthickness=1, bd=0)
        if padding:
            inner = tk.Frame(f, bg=DS["card"],
                             padx=padding[0], pady=padding[1])
            inner.pack(fill="both", expand=True)
            return f, inner
        return f

    @staticmethod
    def btn_primary(parent, text, command=None, width=None, size="normal"):
        px = 18 if size == "large" else 14
        py = 9  if size == "large" else 7
        font = FONTS["btn_lg"] if size == "large" else FONTS["btn"]
        b = tk.Button(parent, text=text, font=font,
                      bg=DS["primary"], fg=DS["white"],
                      relief="flat", bd=0, cursor="hand2",
                      padx=px, pady=py, command=command,
                      activebackground=DS["primary_hover"],
                      activeforeground=DS["white"])
        if width:
            b.config(width=width)
        b.bind("<Enter>", lambda e: b.config(bg=DS["primary_hover"]))
        b.bind("<Leave>", lambda e: b.config(bg=DS["primary"]))
        return b

    @staticmethod
    def btn_secondary(parent, text, command=None):
        b = tk.Button(parent, text=text, font=FONTS["btn"],
                      bg=DS["bg_3"], fg=DS["text_secondary"],
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=7, command=command,
                      highlightbackground=DS["border_bright"],
                      highlightthickness=1,
                      activebackground=DS["card_hover"],
                      activeforeground=DS["text_primary"])
        b.bind("<Enter>", lambda e: b.config(
            bg=DS["card_hover"], fg=DS["text_primary"]))
        b.bind("<Leave>", lambda e: b.config(
            bg=DS["bg_3"], fg=DS["text_secondary"]))
        return b

    @staticmethod
    def btn_danger(parent, text, command=None):
        b = tk.Button(parent, text=text, font=FONTS["btn"],
                      bg=DS["danger_light"], fg=DS["danger"],
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=7, command=command,
                      activebackground=DS["danger_mid"],
                      activeforeground=DS["danger"])
        b.bind("<Enter>", lambda e: b.config(bg=DS["danger_mid"]))
        b.bind("<Leave>", lambda e: b.config(bg=DS["danger_light"]))
        return b

    @staticmethod
    def btn_success(parent, text, command=None):
        b = tk.Button(parent, text=text, font=FONTS["btn"],
                      bg=DS["success"], fg=DS["white"],
                      relief="flat", bd=0, cursor="hand2",
                      padx=14, pady=7, command=command,
                      activebackground="#059669")
        b.bind("<Enter>", lambda e: b.config(bg="#059669"))
        b.bind("<Leave>", lambda e: b.config(bg=DS["success"]))
        return b

    @staticmethod
    def btn_ghost(parent, text, command=None, color=None):
        color = color or DS["accent"]
        b = tk.Button(parent, text=text, font=FONTS["btn_sm"],
                      bg=DS["bg_2"], fg=color,
                      relief="flat", bd=0, cursor="hand2",
                      padx=10, pady=5, command=command,
                      activebackground=DS["bg_3"])
        b.bind("<Enter>", lambda e: b.config(bg=DS["bg_3"]))
        b.bind("<Leave>", lambda e: b.config(bg=DS["bg_2"]))
        return b

    @staticmethod
    def badge(parent, text, color="primary", bg=None):
        bg_parent = bg or DS["card"]
        map_ = {
            "primary": (DS["primary"],  DS["primary_light"]),
            "accent":  (DS["accent"],   DS["accent_light"]),
            "success": (DS["success"],  DS["success_light"]),
            "warning": (DS["warning"],  DS["warning_light"]),
            "danger":  (DS["danger"],   DS["danger_light"]),
            "purple":  (DS["purple"],   DS["purple_light"]),
            "teal":    (DS["teal"],     DS["teal_light"]),
            "muted":   (DS["text_muted"], DS["bg_3"]),
        }
        fg, bg_b = map_.get(color, map_["primary"])
        return tk.Label(parent, text=f"  {text}  ",
                        font=FONTS["badge"], bg=bg_b, fg=fg)

    @staticmethod
    def status_badge(parent, status, bg=None):
        m = {"En cours":"warning","Terminé":"success",
             "Suspendu":"danger","Abandonné":"danger",
             "Actif":"success","Inactif":"muted"}
        return UIComponents.badge(parent, status, m.get(status,"primary"), bg)

    @staticmethod
    def input_field(parent, label, var=None, placeholder="",
                    width=28, row=0, col=0, bg=None, required=False):
        bg = bg or DS["card"]
        lbl_text = label + (" *" if required else "")
        tk.Label(parent, text=lbl_text, font=FONTS["label"],
                 bg=bg, fg=DS["text_muted"],
                 anchor="w").grid(row=row, column=col,
                                  sticky="w", pady=(8, 2), padx=(0, 8))
        if var is None:
            var = tk.StringVar()
        e = tk.Entry(parent, textvariable=var, width=width,
                     font=FONTS["body"],
                     bg=DS["bg_3"], fg=DS["text_primary"],
                     insertbackground=DS["primary"],
                     relief="flat", bd=0,
                     highlightbackground=DS["border_bright"],
                     highlightcolor=DS["primary"],
                     highlightthickness=1)
        e.grid(row=row+1, column=col, sticky="ew",
               pady=(0, 4), padx=(0, 8), ipady=6)
        e.bind("<FocusIn>",
               lambda ev: e.config(highlightbackground=DS["primary"]))
        e.bind("<FocusOut>",
               lambda ev: e.config(highlightbackground=DS["border_bright"]))
        return e, var

    @staticmethod
    def combo_field(parent, label, values, var=None,
                    row=0, col=0, bg=None, width=26, required=False):
        bg = bg or DS["card"]
        lbl_text = label + (" *" if required else "")
        tk.Label(parent, text=lbl_text, font=FONTS["label"],
                 bg=bg, fg=DS["text_muted"],
                 anchor="w").grid(row=row, column=col,
                                  sticky="w", pady=(8, 2), padx=(0, 8))
        if var is None:
            var = tk.StringVar()
        cb = ttk.Combobox(parent, textvariable=var,
                          values=values, width=width,
                          state="readonly", font=FONTS["body"])
        cb.grid(row=row+1, column=col, sticky="ew",
                pady=(0, 4), padx=(0, 8))
        return cb, var

    @staticmethod
    def text_field(parent, label, row=0, col=0, height=4, bg=None):
        bg = bg or DS["card"]
        tk.Label(parent, text=label, font=FONTS["label"],
                 bg=bg, fg=DS["text_muted"],
                 anchor="w").grid(row=row, column=col,
                                  sticky="w", pady=(8, 2), padx=(0, 8))
        w = tk.Text(parent, height=height, font=FONTS["body"],
                    bg=DS["bg_3"], fg=DS["text_primary"],
                    insertbackground=DS["primary"],
                    relief="flat", bd=0,
                    highlightbackground=DS["border_bright"],
                    highlightcolor=DS["primary"],
                    highlightthickness=1,
                    wrap="word", padx=8, pady=6)
        w.grid(row=row+1, column=col, sticky="ew",
               pady=(0, 4), padx=(0, 8))
        return w

    @staticmethod
    def kpi_card(parent, icon, value, label,
                 delta=None, color=None, col=0):
        color = color or DS["primary"]
        card = tk.Frame(parent, bg=DS["card"],
                        highlightbackground=DS["border_bright"],
                        highlightthickness=1)
        card.grid(row=0, column=col, padx=5, pady=4, sticky="nsew")

        # Top accent line
        tk.Frame(card, bg=color, height=2).pack(fill="x")

        inner = tk.Frame(card, bg=DS["card"], padx=18, pady=14)
        inner.pack(fill="both", expand=True)

        # Icon row
        top = tk.Frame(inner, bg=DS["card"])
        top.pack(fill="x", pady=(0, 6))

        icon_bg = tk.Frame(top, bg=DS["bg_3"],
                           width=34, height=34)
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        tk.Label(icon_bg, text=icon,
                 font=("Segoe UI Emoji", 14),
                 bg=DS["bg_3"], fg=color).pack(
            expand=True, fill="both")

        tk.Label(top, text=label, font=FONTS["body_sm"],
                 bg=DS["card"], fg=DS["text_muted"]).pack(
            side="right", anchor="e")

        # Value
        tk.Label(inner, text=str(value), font=FONTS["num"],
                 bg=DS["card"], fg=DS["text_primary"]).pack(anchor="w")

        # Delta
        if delta is not None:
            dc = DS["success"] if delta >= 0 else DS["danger"]
            di = "▲" if delta >= 0 else "▼"
            tk.Label(inner, text=f"{di} {abs(delta)}%",
                     font=FONTS["caption"],
                     bg=DS["card"], fg=dc).pack(anchor="w", pady=(2, 0))
        return card

    @staticmethod
    def section_header(parent, text, bg=None):
        bg = bg or DS["bg"]
        f = tk.Frame(parent, bg=bg)
        row = tk.Frame(f, bg=bg)
        row.pack(fill="x")
        tk.Label(row, text=text, font=FONTS["h3"],
                 bg=bg, fg=DS["text_secondary"],
                 padx=0).pack(side="left")
        tk.Frame(row, bg=DS["border_bright"],
                 height=1).pack(side="left", fill="x",
                                expand=True, padx=(12, 0), pady=10)
        return f


# ══════════════════════════════════════════════════════════════════════════════
#  PREMIUM TABLE
# ══════════════════════════════════════════════════════════════════════════════

def make_premium_table(parent, columns,
                       col_widths=None, col_headers=None):
    frame = tk.Frame(parent, bg=DS["card"],
                     highlightbackground=DS["border_bright"],
                     highlightthickness=1)
    tree = ttk.Treeview(frame, columns=columns,
                        show="headings", selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical",
                        command=tree.yview,
                        style="Dark.Vertical.TScrollbar")
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    for i, col in enumerate(columns):
        hdr = (col_headers[i] if col_headers
               else col.replace("_", " ").title())
        w = col_widths[i] if col_widths else 120
        tree.heading(col, text=hdr)
        tree.column(col, width=w, minwidth=40, anchor="w")

    tree.tag_configure("even", background=DS["row_even"])
    tree.tag_configure("odd",  background=DS["row_odd"])
    return frame, tree


def fill_premium_table(tree, rows, columns):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        vals = [row.get(c, "") if row.get(c) is not None
                else "—" for c in columns]
        tree.insert("", "end", values=vals, tags=(tag,))


# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH BAR
# ══════════════════════════════════════════════════════════════════════════════

class PremiumSearchBar(tk.Frame):
    def __init__(self, parent, placeholder="Search…",
                 on_change=None, bg=None, **kw):
        bg = bg or DS["bg"]
        super().__init__(parent, bg=bg, **kw)
        self._on_change  = on_change
        self._placeholder = placeholder
        self._focused    = False
        self._build()

    def _build(self):
        c = tk.Frame(self, bg=DS["bg_3"],
                     highlightbackground=DS["border_bright"],
                     highlightthickness=1)
        c.pack(fill="x")
        self._c = c

        tk.Label(c, text="⌕", font=("Segoe UI", 13),
                 bg=DS["bg_3"], fg=DS["text_muted"],
                 padx=10).pack(side="left")

        self.var   = tk.StringVar()
        self.entry = tk.Entry(c, textvariable=self.var,
                              font=FONTS["body"],
                              bg=DS["bg_3"], fg=DS["text_muted"],
                              insertbackground=DS["primary"],
                              relief="flat", bd=0)
        self.entry.insert(0, self._placeholder)
        self.entry.pack(side="left", fill="x",
                        expand=True, pady=9, padx=(0, 10))

        self.entry.bind("<FocusIn>",  self._fi)
        self.entry.bind("<FocusOut>", self._fo)
        if self._on_change:
            self.var.trace_add("write",
                lambda *a: self._on_change(self.get()))

    def _fi(self, e):
        if not self._focused:
            self._focused = True
            if self.entry.get() == self._placeholder:
                self.entry.delete(0, "end")
                self.entry.config(fg=DS["text_primary"])
        self._c.config(highlightbackground=DS["primary"])

    def _fo(self, e):
        if not self.entry.get():
            self._focused = False
            self.entry.insert(0, self._placeholder)
            self.entry.config(fg=DS["text_muted"])
        self._c.config(highlightbackground=DS["border_bright"])

    def get(self):
        v = self.var.get()
        return "" if v == self._placeholder else v

    def clear(self):
        self.var.set("")
        self._focused = False
        self.entry.delete(0, "end")
        self.entry.insert(0, self._placeholder)
        self.entry.config(fg=DS["text_muted"])


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def show_toast(parent, message, type_="success", duration=3000):
    colors = {
        "success": (DS["success_light"],  DS["success"], "✓"),
        "error":   (DS["danger_light"],   DS["danger"],  "✗"),
        "info":    (DS["primary_light"],  DS["accent"],  "i"),
        "warning": (DS["warning_light"],  DS["warning"], "!"),
    }
    bg, fg, icon = colors.get(type_, colors["info"])
    t = tk.Toplevel(parent)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.config(bg=bg,
             highlightbackground=fg,
             highlightthickness=1)
    tk.Label(t, text=f"  {icon}  {message}  ",
             font=FONTS["body"], bg=bg, fg=fg,
             padx=12, pady=10).pack()
    t.update_idletasks()
    pw  = parent.winfo_rootx()
    py  = parent.winfo_rooty()
    pw2 = parent.winfo_width()
    tx  = pw + pw2 - t.winfo_width() - 20
    ty  = py + 60
    t.geometry(f"+{tx}+{ty}")
    parent.after(duration, t.destroy)


def show_message(parent, title, message, type_="info"):
    from tkinter import messagebox
    if type_ == "error":
        messagebox.showerror(title, message, parent=parent)
    elif type_ == "warning":
        messagebox.showwarning(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)


def confirm_delete(parent, item_name):
    from tkinter import messagebox
    return messagebox.askyesno(
        "Confirmer la suppression",
        f"Supprimer définitivement :\n\n« {item_name} »",
        parent=parent, icon="warning")


# Compat aliases
Card      = lambda parent, **kw: UIComponents.card(parent, **kw)
SearchBar = PremiumSearchBar
make_table = make_premium_table
fill_table = fill_premium_table
THEME = DS
