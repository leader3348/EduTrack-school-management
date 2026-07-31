"""
EduTrack PDF Manager v2.0
Premium PDF export with full ReportLab support.
Fixed: all imports, colors namespace, styles.
"""

import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)


def _check():
    if not REPORTLAB_OK:
        raise ImportError("ReportLab manquant. Exécutez : pip install reportlab")


# ── Brand colors (no conflict with rl_colors namespace) ──────────────────────
B_DARK      = rl_colors.HexColor("#0F172A")
B_PRIMARY   = rl_colors.HexColor("#2563EB")
B_PRIMARY_L = rl_colors.HexColor("#EFF6FF")
B_SECONDARY = rl_colors.HexColor("#1E293B")
B_SUCCESS   = rl_colors.HexColor("#22C55E")
B_WARNING   = rl_colors.HexColor("#F59E0B")
B_DANGER    = rl_colors.HexColor("#EF4444")
B_MUTED     = rl_colors.HexColor("#94A3B8")
B_BORDER    = rl_colors.HexColor("#E2E8F0")
B_BG    = rl_colors.HexColor("#0F1629")
B_SLATE = rl_colors.HexColor("#141D35")
B_WHITE     = rl_colors.white
B_TEXT      = rl_colors.HexColor("#0F172A")
B_TEXT2     = rl_colors.HexColor("#475569")
B_PURPLE    = rl_colors.HexColor("#8B5CF6")
B_TEAL      = rl_colors.HexColor("#14B8A6")


# ── Typography ────────────────────────────────────────────────────────────────
def _styles():
    s = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle(
            "doc_title", parent=s["Normal"],
            fontName="Helvetica-Bold", fontSize=26,
            textColor=B_WHITE, spaceAfter=4,
            alignment=TA_LEFT),
        "doc_subtitle": ParagraphStyle(
            "doc_subtitle", parent=s["Normal"],
            fontName="Helvetica", fontSize=11,
            textColor=rl_colors.HexColor("#94A3B8"),
            spaceAfter=0, alignment=TA_LEFT),
        "section_title": ParagraphStyle(
            "section_title", parent=s["Normal"],
            fontName="Helvetica-Bold", fontSize=13,
            textColor=B_DARK, spaceBefore=14, spaceAfter=6),
        "field_label": ParagraphStyle(
            "field_label", parent=s["Normal"],
            fontName="Helvetica-Bold", fontSize=9,
            textColor=B_PRIMARY, spaceAfter=2),
        "field_value": ParagraphStyle(
            "field_value", parent=s["Normal"],
            fontName="Helvetica", fontSize=10,
            textColor=B_TEXT, spaceAfter=4),
        "body": ParagraphStyle(
            "body", parent=s["Normal"],
            fontName="Helvetica", fontSize=10,
            textColor=B_TEXT, spaceAfter=4),
        "small": ParagraphStyle(
            "small", parent=s["Normal"],
            fontName="Helvetica", fontSize=8,
            textColor=B_TEXT2),
        "table_header": ParagraphStyle(
            "table_header", parent=s["Normal"],
            fontName="Helvetica-Bold", fontSize=9,
            textColor=B_WHITE, alignment=TA_LEFT),
        "table_cell": ParagraphStyle(
            "table_cell", parent=s["Normal"],
            fontName="Helvetica", fontSize=9,
            textColor=B_TEXT),
        "kpi_value": ParagraphStyle(
            "kpi_value", parent=s["Normal"],
            fontName="Helvetica-Bold", fontSize=20,
            textColor=B_PRIMARY, alignment=TA_CENTER),
        "kpi_label": ParagraphStyle(
            "kpi_label", parent=s["Normal"],
            fontName="Helvetica", fontSize=8,
            textColor=B_TEXT2, alignment=TA_CENTER),
        "footer": ParagraphStyle(
            "footer", parent=s["Normal"],
            fontName="Helvetica", fontSize=7,
            textColor=B_MUTED),
    }


# ── Page header/footer callback ───────────────────────────────────────────────
class _PageTemplate:
    def __init__(self, doc_type="Report", author="EduTrack"):
        self.doc_type = doc_type
        self.author = author

    def __call__(self, canvas, doc):
        canvas.saveState()
        W, H = A4

        # Header bar
        canvas.setFillColor(B_DARK)
        canvas.rect(0, H - 56, W, 56, fill=1, stroke=0)

        # Brand mark
        canvas.setFillColor(B_PRIMARY)
        canvas.rect(0, H - 56, 5, 56, fill=1, stroke=0)

        # Title in header
        canvas.setFillColor(B_WHITE)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(20, H - 34, "EduTrack")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(rl_colors.HexColor("#94A3B8"))
        canvas.drawString(20, H - 48, self.doc_type)

        # Date in header
        canvas.setFont("Helvetica", 8)
        date_str = datetime.now().strftime("%d %B %Y")
        canvas.drawRightString(W - 20, H - 34, date_str)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(W - 20, H - 48, self.author)

        # Footer
        canvas.setFillColor(B_BORDER)
        canvas.rect(0, 0, W, 28, fill=1, stroke=0)
        canvas.setFillColor(B_PRIMARY)
        canvas.rect(0, 0, 5, 28, fill=1, stroke=0)

        canvas.setFillColor(B_TEXT2)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(20, 10,
            f"EduTrack Academic Management System  •  Généré le "
            f"{datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(B_PRIMARY)
        canvas.drawRightString(W - 20, 10, f"Page {doc.page}")

        canvas.restoreState()


def _make_doc(filepath, doc_type="Report"):
    return SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.6*cm, bottomMargin=1.8*cm,
        title=f"EduTrack – {doc_type}",
        author="EduTrack",
    )


def _table_style(header_color=None):
    """Style de tableau premium commun."""
    hc = header_color or B_PRIMARY
    return TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  hc),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  B_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("TOPPADDING",    (0, 0), (-1, 0),  10),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  10),
        ("LEFTPADDING",   (0, 0), (-1, 0),  10),
        # Body
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TOPPADDING",    (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LEFTPADDING",   (0, 1), (-1, -1), 10),
        ("TEXTCOLOR",     (0, 1), (-1, -1), B_TEXT),
        # Alternating rows
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [B_WHITE, B_SLATE]),
        # Grid
        ("LINEBELOW",     (0, 0), (-1, 0),  1, B_PRIMARY),
        ("LINEBELOW",     (0, 1), (-1, -1), 0.4, B_BORDER),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])


def _section_header(title, st):
    """Bloc titre de section."""
    data = [[Paragraph(title, st["section_title"])]]
    tbl = Table(data, colWidths=[17.4*cm])
    tbl.setStyle(TableStyle([
        ("LINEBELOW",  (0, 0), (-1, -1), 2, B_PRIMARY),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
    ]))
    return tbl


def _kpi_row(items):
    """
    items = [(value, label, color), ...]
    Returns a Table with KPI boxes.
    """
    n = len(items)
    col_w = 17.4 / n

    data = []
    vals_row = []
    labs_row = []
    for val, label, color in items:
        vals_row.append(str(val))
        labs_row.append(label)
    data.append(vals_row)
    data.append(labs_row)

    col_widths = [col_w * cm] * n

    tbl = Table(data, colWidths=col_widths, rowHeights=[28, 14])
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, -1), B_WHITE),
        ("BOX",           (0, 0), (-1, -1), 1, B_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.5, B_PRIMARY),
        ("TOPPADDING",    (0, 0), (-1, 0),  10),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  4),
        ("TOPPADDING",    (0, 1), (-1, 1),  0),
        ("BOTTOMPADDING", (0, 1), (-1, 1),  10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, (_, _, color) in enumerate(items):
        style_cmds.append(("TEXTCOLOR", (i, 0), (i, 0), color))
        style_cmds.append(("FONTNAME",  (i, 0), (i, 0), "Helvetica-Bold"))
        style_cmds.append(("FONTSIZE",  (i, 0), (i, 0), 18))
        style_cmds.append(("TEXTCOLOR", (i, 1), (i, 1), B_TEXT2))
        style_cmds.append(("FONTNAME",  (i, 1), (i, 1), "Helvetica"))
        style_cmds.append(("FONTSIZE",  (i, 1), (i, 1), 8))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: FICHE ÉTUDIANT
# ══════════════════════════════════════════════════════════════════════════════

def export_fiche_etudiant(detail: dict, filepath: str = None) -> str:
    _check()
    et = detail["etudiant"]
    projets = detail["projets"]
    stages = detail["stages"]
    notes = detail["notes"]
    moyenne = detail.get("moyenne", 0.0)

    if not filepath:
        fname = (f"fiche_{et['matricule']}_"
                 f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        filepath = os.path.join(EXPORTS_DIR, fname)

    doc = _make_doc(filepath, f"Fiche Étudiant – {et['prenom']} {et['nom']}")
    tpl = _PageTemplate(f"Fiche Étudiant – {et['matricule']}")
    st = _styles()
    story = []
    story.append(Spacer(1, 0.3*cm))

    # ── KPIs ─────────────────────────────────────────────────────────────────
    moy_color = B_SUCCESS if (moyenne or 0) >= 10 else B_DANGER
    story.append(_kpi_row([
        (len(projets), "Projets", B_PRIMARY),
        (len(stages),  "Stages",  B_TEAL),
        (len(notes),   "Évaluations", B_PURPLE),
        (f"{moyenne:.2f}/20" if moyenne else "N/A", "Moyenne Générale", moy_color),
    ]))
    story.append(Spacer(1, 0.5*cm))

    # ── Informations personnelles ─────────────────────────────────────────────
    story.append(_section_header("Informations Personnelles", st))
    story.append(Spacer(1, 0.2*cm))

    info = [
        ["Matricule", et.get("matricule",""), "Filière", et.get("filiere","")],
        ["Nom",       et.get("nom",""),        "Niveau",  et.get("niveau","")],
        ["Prénom",    et.get("prenom",""),      "Tél.",    et.get("telephone","")],
        ["Email",     et.get("email",""),       "Né(e) le",et.get("date_naissance","")],
        ["Inscrit le",et.get("date_inscription",""), "Statut",
         "Actif" if et.get("actif",1) else "Inactif"],
    ]
    tbl = Table(info, colWidths=[3*cm, 5.7*cm, 3*cm, 5.7*cm])
    tbl.setStyle(TableStyle([
        ("FONTNAME",   (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",   (2,0),(2,-1), "Helvetica-Bold"),
        ("FONTNAME",   (1,0),(1,-1), "Helvetica"),
        ("FONTNAME",   (3,0),(3,-1), "Helvetica"),
        ("FONTSIZE",   (0,0),(-1,-1),9),
        ("TEXTCOLOR",  (0,0),(0,-1), B_PRIMARY),
        ("TEXTCOLOR",  (2,0),(2,-1), B_PRIMARY),
        ("TEXTCOLOR",  (1,0),(1,-1), B_TEXT),
        ("TEXTCOLOR",  (3,0),(3,-1), B_TEXT),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[B_WHITE, B_SLATE]),
        ("LINEBELOW",  (0,0),(-1,-1), 0.4, B_BORDER),
        ("TOPPADDING", (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Projets ───────────────────────────────────────────────────────────────
    story.append(_section_header("Projets Académiques", st))
    story.append(Spacer(1, 0.2*cm))
    if projets:
        headers = [["Titre", "Type", "Rôle", "Année", "Statut", "Note"]]
        rows = []
        for p in projets:
            note_v = f"{p['note']:.1f}/20" if p.get("note") else "—"
            rows.append([
                str(p.get("titre",""))[:38],
                str(p.get("type_projet","")),
                str(p.get("role","")),
                str(p.get("annee_libelle","")),
                str(p.get("statut","")),
                note_v,
            ])
        tbl = Table(headers+rows,
                    colWidths=[5.2*cm,2.2*cm,2.5*cm,2.5*cm,2.3*cm,2.7*cm])
        tbl.setStyle(_table_style())
        story.append(tbl)
    else:
        story.append(Paragraph("Aucun projet enregistré.", st["body"]))
    story.append(Spacer(1, 0.5*cm))

    # ── Stages ────────────────────────────────────────────────────────────────
    story.append(_section_header("Stages Professionnels", st))
    story.append(Spacer(1, 0.2*cm))
    if stages:
        headers = [["Titre", "Entreprise", "Début", "Fin", "Semaines", "Note"]]
        rows = []
        for s in stages:
            note_v = f"{s['note']:.1f}/20" if s.get("note") else "—"
            rows.append([
                str(s.get("titre",""))[:30],
                str(s.get("entreprise_nom","N/A"))[:22],
                str(s.get("date_debut","")),
                str(s.get("date_fin","")),
                str(s.get("duree_semaines","—")),
                note_v,
            ])
        tbl = Table(headers+rows,
                    colWidths=[4.5*cm,3.5*cm,2.2*cm,2.2*cm,2*cm,3*cm])
        tbl.setStyle(_table_style(B_TEAL))
        story.append(tbl)
    else:
        story.append(Paragraph("Aucun stage enregistré.", st["body"]))
    story.append(Spacer(1, 0.5*cm))

    # ── Notes ─────────────────────────────────────────────────────────────────
    if notes:
        story.append(_section_header("Historique des Évaluations", st))
        story.append(Spacer(1, 0.2*cm))
        headers = [["Type", "Note", "Coeff.", "Date", "Commentaire"]]
        rows = []
        for n in notes:
            rows.append([
                str(n.get("type_evaluation","")),
                f"{n['note']:.1f}/20",
                str(n.get("coefficient",1.0)),
                str(n.get("date_evaluation","")),
                str(n.get("commentaire","") or "")[:40],
            ])
        tbl = Table(headers+rows,
                    colWidths=[3.2*cm,2.2*cm,1.8*cm,3*cm,7.2*cm])
        tbl.setStyle(_table_style(B_PURPLE))
        story.append(tbl)

    doc.build(story, onFirstPage=tpl, onLaterPages=tpl)
    return filepath


# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: LISTE ÉTUDIANTS
# ══════════════════════════════════════════════════════════════════════════════

def export_liste_etudiants(etudiants: list, filepath: str = None) -> str:
    _check()
    if not filepath:
        fname = f"etudiants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, fname)

    doc = _make_doc(filepath, "Liste des Étudiants")
    tpl = _PageTemplate("Liste des Étudiants")
    st = _styles()
    story = []
    story.append(Spacer(1, 0.3*cm))

    story.append(_kpi_row([
        (len(etudiants), "Étudiants", B_PRIMARY),
        (len(set(e.get("filiere","") for e in etudiants)), "Filières", B_PURPLE),
        (len(set(e.get("niveau","") for e in etudiants)), "Niveaux", B_TEAL),
    ]))
    story.append(Spacer(1, 0.5*cm))
    story.append(_section_header("Registre des Étudiants", st))
    story.append(Spacer(1, 0.2*cm))

    headers = [["#", "Matricule", "Nom", "Prénom", "Filière", "Niveau", "Email"]]
    rows = []
    for i, e in enumerate(etudiants, 1):
        rows.append([
            str(i),
            str(e.get("matricule","")),
            str(e.get("nom","")),
            str(e.get("prenom","")),
            str(e.get("filiere","")),
            str(e.get("niveau","")),
            str(e.get("email",""))[:30],
        ])
    tbl = Table(headers+rows,
                colWidths=[0.8*cm,2.5*cm,3*cm,3*cm,3.5*cm,1.8*cm,4.8*cm])
    tbl.setStyle(_table_style())
    story.append(tbl)

    doc.build(story, onFirstPage=tpl, onLaterPages=tpl)
    return filepath


# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: LISTE PROJETS
# ══════════════════════════════════════════════════════════════════════════════

def export_liste_projets(projets: list, filepath: str = None) -> str:
    _check()
    if not filepath:
        fname = f"projets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, fname)

    doc = _make_doc(filepath, "Liste des Projets")
    tpl = _PageTemplate("Liste des Projets")
    st = _styles()
    story = []
    story.append(Spacer(1, 0.3*cm))

    termines = sum(1 for p in projets if p.get("statut") == "Terminé")
    en_cours = sum(1 for p in projets if p.get("statut") == "En cours")
    notes_val = [p["note"] for p in projets if p.get("note")]
    moy = sum(notes_val)/len(notes_val) if notes_val else 0

    story.append(_kpi_row([
        (len(projets), "Total Projets", B_PRIMARY),
        (en_cours,     "En cours",      B_WARNING),
        (termines,     "Terminés",      B_SUCCESS),
        (f"{moy:.1f}/20" if moy else "N/A", "Note Moy.", B_PURPLE),
    ]))
    story.append(Spacer(1, 0.5*cm))
    story.append(_section_header("Catalogue des Projets", st))
    story.append(Spacer(1, 0.2*cm))

    headers = [["#","Titre","Type","Année","Statut","Note","Mention"]]
    rows = []
    for i, p in enumerate(projets, 1):
        note_v = f"{p['note']:.1f}" if p.get("note") else "—"
        rows.append([
            str(i),
            str(p.get("titre",""))[:35],
            str(p.get("type_projet","")),
            str(p.get("annee_libelle","")),
            str(p.get("statut","")),
            note_v,
            str(p.get("mention","") or "—"),
        ])
    tbl = Table(headers+rows,
                colWidths=[0.8*cm,5.5*cm,2*cm,2.5*cm,2.2*cm,1.5*cm,2.9*cm])
    tbl.setStyle(_table_style())
    story.append(tbl)

    doc.build(story, onFirstPage=tpl, onLaterPages=tpl)
    return filepath


# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: LISTE STAGES
# ══════════════════════════════════════════════════════════════════════════════

def export_liste_stages(stages: list, filepath: str = None) -> str:
    _check()
    if not filepath:
        fname = f"stages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, fname)

    doc = _make_doc(filepath, "Liste des Stages")
    tpl = _PageTemplate("Liste des Stages")
    st = _styles()
    story = []
    story.append(Spacer(1, 0.3*cm))

    termines = sum(1 for s in stages if s.get("statut") == "Terminé")
    en_cours = sum(1 for s in stages if s.get("statut") == "En cours")
    notes_val = [s["note"] for s in stages if s.get("note")]
    moy = sum(notes_val)/len(notes_val) if notes_val else 0

    story.append(_kpi_row([
        (len(stages), "Total Stages", B_TEAL),
        (en_cours,    "En cours",     B_WARNING),
        (termines,    "Terminés",     B_SUCCESS),
        (f"{moy:.1f}/20" if moy else "N/A", "Note Moy.", B_PRIMARY),
    ]))
    story.append(Spacer(1, 0.5*cm))
    story.append(_section_header("Registre des Stages", st))
    story.append(Spacer(1, 0.2*cm))

    headers = [["#","Étudiant","Titre","Entreprise","Début","Fin","Note"]]
    rows = []
    for i, s in enumerate(stages, 1):
        note_v = f"{s['note']:.1f}" if s.get("note") else "—"
        rows.append([
            str(i),
            str(s.get("etudiant_nom",""))[:20],
            str(s.get("titre",""))[:28],
            str(s.get("entreprise_nom","N/A"))[:20],
            str(s.get("date_debut","")),
            str(s.get("date_fin","")),
            note_v,
        ])
    tbl = Table(headers+rows,
                colWidths=[0.8*cm,3.5*cm,4*cm,3*cm,1.9*cm,1.9*cm,2.3*cm])
    tbl.setStyle(_table_style(B_TEAL))
    story.append(tbl)

    doc.build(story, onFirstPage=tpl, onLaterPages=tpl)
    return filepath


# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: RÉSULTATS RECHERCHE
# ══════════════════════════════════════════════════════════════════════════════

def export_resultats_recherche(resultats: dict, terme: str,
                                filepath: str = None) -> str:
    _check()
    if not filepath:
        fname = f"recherche_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(EXPORTS_DIR, fname)

    doc = _make_doc(filepath, f'Recherche : "{terme}"')
    tpl = _PageTemplate(f'Résultats : "{terme}"')
    st = _styles()
    story = []
    story.append(Spacer(1, 0.3*cm))

    etudiants  = resultats.get("etudiants", [])
    projets    = resultats.get("projets", [])
    stages     = resultats.get("stages", [])
    professeurs= resultats.get("professeurs", [])

    total = len(etudiants)+len(projets)+len(stages)+len(professeurs)
    story.append(_kpi_row([
        (len(etudiants),   "Étudiants",   B_PRIMARY),
        (len(projets),     "Projets",     B_PURPLE),
        (len(stages),      "Stages",      B_TEAL),
        (len(professeurs), "Professeurs", B_WARNING),
    ]))
    story.append(Spacer(1, 0.5*cm))

    if etudiants:
        story.append(_section_header(f"Étudiants ({len(etudiants)})", st))
        story.append(Spacer(1, 0.2*cm))
        h = [["Matricule","Nom","Prénom","Filière","Niveau"]]
        r = [[e.get("matricule",""),e.get("nom",""),e.get("prenom",""),
              e.get("filiere",""),e.get("niveau","")] for e in etudiants]
        tbl = Table(h+r, colWidths=[2.5*cm,3.5*cm,3.5*cm,4*cm,3.9*cm])
        tbl.setStyle(_table_style())
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

    if projets:
        story.append(_section_header(f"Projets ({len(projets)})", st))
        story.append(Spacer(1, 0.2*cm))
        h = [["Titre","Type","Année","Statut","Note"]]
        r = [[p.get("titre","")[:35],p.get("type_projet",""),
              p.get("annee_libelle",""),p.get("statut",""),
              f"{p['note']:.1f}" if p.get("note") else "—"] for p in projets]
        tbl = Table(h+r, colWidths=[6*cm,2.5*cm,3*cm,3*cm,2.9*cm])
        tbl.setStyle(_table_style(B_PURPLE))
        story.append(tbl)
        story.append(Spacer(1, 0.4*cm))

    if stages:
        story.append(_section_header(f"Stages ({len(stages)})", st))
        story.append(Spacer(1, 0.2*cm))
        h = [["Titre","Étudiant","Entreprise","Statut","Note"]]
        r = [[s.get("titre","")[:28],s.get("etudiant_nom","")[:20],
              s.get("entreprise_nom","N/A")[:20],s.get("statut",""),
              f"{s['note']:.1f}" if s.get("note") else "—"] for s in stages]
        tbl = Table(h+r, colWidths=[4.5*cm,3.5*cm,3.5*cm,2.5*cm,3.4*cm])
        tbl.setStyle(_table_style(B_TEAL))
        story.append(tbl)

    if not total:
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("Aucun résultat trouvé pour cette recherche.", st["body"]))

    doc.build(story, onFirstPage=tpl, onLaterPages=tpl)
    return filepath
