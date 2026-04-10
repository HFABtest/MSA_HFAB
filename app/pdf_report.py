"""
PDF report generation for Mognadsdialog.

Renders an HTML template, then converts to PDF via WeasyPrint.
The report includes:
  - Cover page with organization, title, date, participants
  - Summary table with maturity levels
  - Radar chart (embedded as inline SVG)
  - Per-perspective detail pages with dimension notes, reasoning, and guidance
"""

import math
from datetime import datetime
from typing import Optional

from .reference_data import (
    PERSPECTIVES, DIMENSIONS, MATURITY_LEVELS,
    PERSPECTIVE_BY_KEY, DIMENSION_BY_KEY, MATURITY_BY_LEVEL,
    NEXT_LEVEL_GUIDANCE,
)
from .mcf_maturity_data import PERSPECTIVE_MATURITY, PERSPECTIVE_CULTURE

LEVEL_COLORS = {1: "#e74c3c", 2: "#f39c12", 3: "#27ae60", 4: "#2980b9", None: "#bdc3c7"}


def generate_report_html(assessment: dict, perspectives: list[dict], organization: dict) -> str:
    """Generate full HTML report string ready for WeasyPrint."""
    title = assessment["title"]
    org_name = organization["name"]
    date_str = _fmt_date(assessment["created_at"])
    finalized_str = _fmt_date(assessment.get("finalized_at")) or "Ej slutförd"

    # Sort perspectives by reference order
    persp_order = [p.key for p in PERSPECTIVES]
    perspectives = sorted(perspectives, key=lambda p: persp_order.index(p["perspective_key"]))

    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<style>
{_css()}
</style>
</head>
<body>

<!-- Cover page -->
<div class="cover">
    <div class="cover-logo">MOGNADSDIALOG</div>
    <h1>{_esc(title)}</h1>
    <div class="cover-org">{_esc(org_name)}</div>
    <div class="cover-meta">
        <table class="meta-table">
            <tr><td class="meta-label">Datum:</td><td>{date_str}</td></tr>
            <tr><td class="meta-label">Slutförd:</td><td>{finalized_str}</td></tr>
            <tr><td class="meta-label">Facilitator:</td><td>{_esc(assessment.get('facilitator', ''))}</td></tr>
            <tr><td class="meta-label">Deltagare:</td><td>{_esc(assessment.get('participants', ''))}</td></tr>
        </table>
    </div>
    <div class="cover-footer">
        Mognadsdialog enligt MSB/MCF-modellen för systematiskt informationssäkerhetsarbete
    </div>
</div>

<!-- Summary page -->
<div class="page">
    <h2>Sammanfattning</h2>
    <table class="summary-table">
        <thead>
            <tr>
                <th style="text-align:left">Perspektiv</th>
                <th>Nivå</th>
                <th style="text-align:left">Motivering</th>
            </tr>
        </thead>
        <tbody>
            {''.join(_summary_row(p) for p in perspectives)}
        </tbody>
    </table>
</div>

<!-- Radar chart page -->
<div class="page">
    <h2>Radardiagram</h2>
    <div class="radar-container">
        {_generate_radar_svg(perspectives)}
    </div>
    <div class="ladder">
        <h3>Mognadstrappa</h3>
        {_generate_ladder_html(perspectives)}
    </div>
</div>

<!-- Per-perspective detail pages -->
{''.join(_perspective_page(p) for p in perspectives)}

<!-- Footer note -->
<div class="page">
    <div class="footer-note">
        <p><strong>Om denna rapport</strong></p>
        <p>Denna rapport är genererad från systemstödet för Mognadsdialog.
        Bedömningarna baseras på den dialog som förts och representerar gruppens
        gemensamma uppfattning vid tillfället. Mognadsnivåerna är satta genom
        konsensus – inte genom automatisk beräkning.</p>
        <p>Modellen följer MSB:s ramverk för systematiskt informationssäkerhetsarbete
        och Myndigheten för samhällsskydd och beredskaps (MSB) vägledning för
        mognadsbedömning.</p>
        <p style="color:#999;margin-top:2em;font-size:0.8em">
            Genererad: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>
    </div>
</div>

</body>
</html>"""


def _summary_row(p: dict) -> str:
    ref = PERSPECTIVE_BY_KEY[p["perspective_key"]]
    level = p.get("chosen_level")
    color = LEVEL_COLORS.get(level, LEVEL_COLORS[None])
    level_text = str(level) if level else "–"
    reasoning = _esc(p.get("reasoning", "")) or "<em>Ingen motivering</em>"
    return f"""
        <tr>
            <td style="font-weight:600">{ref.name_sv}</td>
            <td style="text-align:center">
                <span class="level-badge" style="background:{color}">{level_text}</span>
            </td>
            <td class="reasoning-cell">{reasoning}</td>
        </tr>"""


def _perspective_page(p: dict) -> str:
    ref = PERSPECTIVE_BY_KEY[p["perspective_key"]]
    level = p.get("chosen_level")
    color = LEVEL_COLORS.get(level, LEVEL_COLORS[None])
    level_label = MATURITY_BY_LEVEL[level].name_sv if level else "Ej bedömd"

    # Dimension assessments
    dim_notes_html = ""
    for dim in DIMENSIONS:
        da = next((d for d in p.get("dimension_assessments", []) if d["dimension_key"] == dim.key), None)
        dim_level = da["selected_level"] if da and da.get("selected_level") else None
        notes = da["notes"].strip() if da and da.get("notes") else None
        # Get the MCF description for the selected level
        mcf_desc = None
        if dim_level:
            pm = PERSPECTIVE_MATURITY.get(p["perspective_key"], {})
            dim_descs = pm.get(dim.key, {})
            mcf_desc = dim_descs.get(dim_level)
        dim_color = LEVEL_COLORS.get(dim_level, LEVEL_COLORS[None])
        dim_notes_html += f"""
        <div class="dimension">
            <h4>{dim.name_sv} <span class="dim-en">({dim.name_en})</span>
                {f'<span class="level-badge" style="background:{dim_color};margin-left:0.5em">{dim_level}</span>' if dim_level else ''}
            </h4>
            {f'<div class="notes has-content">{_esc(mcf_desc)}</div>' if mcf_desc else '<div class="notes empty"><em>Ej bedömd</em></div>'}
            {f'<p class="dim-comment"><em>Kommentar:</em> {_esc(notes)}</p>' if notes else ''}
        </div>"""

    # Reasoning
    reasoning_html = ""
    if p.get("reasoning", "").strip():
        reasoning_html = f"""
        <div class="reasoning-box">
            <strong>Motivering för vald nivå:</strong>
            <p>{_esc(p['reasoning'])}</p>
        </div>"""

    # Guidance
    guidance_html = ""
    if level and level < 4:
        suggestions = NEXT_LEVEL_GUIDANCE.get((p["perspective_key"], level), [])
        if suggestions:
            guidance_html = f"""
            <div class="guidance-box">
                <strong>Vägledning mot nivå {level + 1}:</strong>
                <ul>
                    {''.join(f'<li>{_esc(s)}</li>' for s in suggestions)}
                </ul>
                <p class="guidance-note">Förslagen är riktningsgivande, inte en checklista.</p>
            </div>"""

    return f"""
    <div class="page perspective-page">
        <div class="persp-header" style="border-left-color:{color}">
            <div class="persp-title">
                <h2>{ref.name_sv}</h2>
                <span class="persp-en">{ref.name_en}</span>
            </div>
            <div class="persp-level">
                <span class="level-badge large" style="background:{color}">{level or '–'}</span>
                <span class="level-label">{level_label}</span>
            </div>
        </div>
        <p class="persp-desc">{ref.description_sv}</p>

        {dim_notes_html}
        {reasoning_html}
        {guidance_html}
    </div>"""


def _generate_radar_svg(perspectives: list[dict]) -> str:
    """Generate an inline SVG radar chart."""
    cx, cy = 200, 200
    max_r = 150
    n = len(perspectives)
    levels = 4

    elements = []

    # Grid rings
    for l in range(1, levels + 1):
        r = (l / levels) * max_r
        points = []
        for i in range(n):
            angle = (math.pi * 2 * i) / n - math.pi / 2
            points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
        elements.append(f'<polygon points="{" ".join(points)}" fill="none" stroke="#dce1e8" stroke-width="1"/>')
        # Level number
        label_angle = -math.pi / 2
        lx = cx + r * math.cos(label_angle) + 5
        ly = cy + r * math.sin(label_angle) + 4
        elements.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="10" fill="#aab">{l}</text>')

    # Spokes + labels
    for i in range(n):
        angle = (math.pi * 2 * i) / n - math.pi / 2
        x2 = cx + max_r * math.cos(angle)
        y2 = cy + max_r * math.sin(angle)
        elements.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#dce1e8" stroke-width="1"/>')

        ref = PERSPECTIVE_BY_KEY[perspectives[i]["perspective_key"]]
        label_r = max_r + 20
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        anchor = "end" if math.cos(angle) < -0.1 else ("start" if math.cos(angle) > 0.1 else "middle")
        baseline = "auto" if math.sin(angle) < -0.1 else ("hanging" if math.sin(angle) > 0.1 else "central")
        elements.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="11" fill="#2c3e50" text-anchor="{anchor}" dominant-baseline="{baseline}">{ref.name_sv}</text>')

    # Data polygon
    values = [p.get("chosen_level") or 0 for p in perspectives]
    data_points = []
    for i in range(n):
        angle = (math.pi * 2 * i) / n - math.pi / 2
        r = (values[i] / levels) * max_r
        data_points.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")

    elements.append(f'<polygon points="{" ".join(data_points)}" fill="rgba(41,128,185,0.2)" stroke="#2980b9" stroke-width="2.5"/>')

    # Data dots
    for i in range(n):
        angle = (math.pi * 2 * i) / n - math.pi / 2
        r = (values[i] / levels) * max_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        color = "#2980b9" if values[i] else "#bdc3c7"
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}" stroke="white" stroke-width="2"/>')

    return f'<svg viewBox="0 0 400 400" width="400" height="400" xmlns="http://www.w3.org/2000/svg">{"".join(elements)}</svg>'


def _generate_ladder_html(perspectives: list[dict]) -> str:
    html = ""
    for level in range(4, 0, -1):
        ml = MATURITY_BY_LEVEL[level]
        color = LEVEL_COLORS[level]
        at_level = [p for p in perspectives if p.get("chosen_level") == level]
        names = ", ".join(PERSPECTIVE_BY_KEY[p["perspective_key"]].name_sv for p in at_level) if at_level else "–"
        bg = f"{color}15" if at_level else "#fafafa"
        html += f"""
        <div class="ladder-row" style="border-left-color:{color};background:{bg}">
            <span class="ladder-level" style="color:{color}">Nivå {level}</span>
            <span class="ladder-names">{names}</span>
        </div>"""
    return html


def _css() -> str:
    return """
    @page {
        size: A4;
        margin: 2cm 2.5cm;
        @bottom-center {
            content: counter(page) " / " counter(pages);
            font-size: 9pt;
            color: #999;
        }
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        color: #2c3e50;
        font-size: 10pt;
        line-height: 1.6;
    }

    h2 { font-size: 14pt; color: #1a5276; margin-bottom: 0.8em; }
    h3 { font-size: 12pt; color: #2980b9; margin-bottom: 0.5em; margin-top: 1em; }
    h4 { font-size: 10.5pt; color: #2980b9; margin-bottom: 0.3em; }

    .page { page-break-before: always; }
    .page:first-of-type { page-break-before: avoid; }

    /* Cover */
    .cover {
        text-align: center;
        padding-top: 6cm;
        page-break-after: always;
    }
    .cover-logo {
        font-size: 11pt;
        letter-spacing: 4px;
        color: #7f8c8d;
        margin-bottom: 2cm;
    }
    .cover h1 {
        font-size: 22pt;
        color: #1a5276;
        margin-bottom: 0.5em;
    }
    .cover-org {
        font-size: 14pt;
        color: #2980b9;
        margin-bottom: 2cm;
    }
    .cover-meta { display: inline-block; text-align: left; }
    .meta-table td { padding: 0.2em 0.5em; font-size: 10pt; }
    .meta-label { font-weight: 600; color: #7f8c8d; }
    .cover-footer {
        position: absolute;
        bottom: 2cm;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 9pt;
        color: #999;
    }

    /* Summary table */
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.5em;
    }
    .summary-table th {
        padding: 0.5em;
        border-bottom: 2px solid #dce1e8;
        font-size: 9.5pt;
        color: #7f8c8d;
    }
    .summary-table td {
        padding: 0.5em;
        border-bottom: 1px solid #eee;
        vertical-align: top;
    }
    .reasoning-cell { font-size: 9pt; color: #555; }

    /* Level badge */
    .level-badge {
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        border-radius: 50%;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 10pt;
    }
    .level-badge.large {
        width: 36px;
        height: 36px;
        line-height: 36px;
        font-size: 14pt;
    }

    /* Radar */
    .radar-container { text-align: center; margin: 1em 0; }

    /* Ladder */
    .ladder { margin-top: 1.5em; }
    .ladder-row {
        display: flex;
        align-items: center;
        gap: 1em;
        padding: 0.5em 0.8em;
        border-left: 4px solid #ccc;
        margin-bottom: 2px;
        border-radius: 3px;
    }
    .ladder-level { font-weight: 700; font-size: 9pt; min-width: 50px; }
    .ladder-names { font-size: 9pt; }

    /* Perspective pages */
    .perspective-page { }
    .persp-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 5px solid;
        padding-left: 0.8em;
        margin-bottom: 0.8em;
    }
    .persp-en { font-size: 9pt; color: #7f8c8d; }
    .persp-level { text-align: center; }
    .level-label { display: block; font-size: 8pt; color: #7f8c8d; margin-top: 0.2em; }
    .persp-desc { color: #555; margin-bottom: 1em; font-size: 9.5pt; }

    /* Dimensions */
    .dimension {
        margin-bottom: 1em;
        padding: 0.6em 0.8em;
        background: #f8f9fa;
        border-radius: 4px;
        border: 1px solid #eee;
    }
    .dim-en { font-weight: normal; font-size: 8.5pt; color: #999; }
    .dim-desc { font-size: 8.5pt; color: #999; margin-bottom: 0.4em; }
    .notes { font-size: 9.5pt; white-space: pre-wrap; }
    .notes.empty { color: #bbb; font-style: italic; }
    .notes.has-content { color: #2c3e50; }
    .dim-comment { font-size: 8.5pt; color: #666; margin-top: 0.3em; }

    /* Reasoning box */
    .reasoning-box {
        margin-top: 1em;
        padding: 0.6em 0.8em;
        background: #f0f7ff;
        border-left: 3px solid #2980b9;
        border-radius: 4px;
    }
    .reasoning-box p { margin-top: 0.3em; font-size: 9.5pt; white-space: pre-wrap; }

    /* Guidance box */
    .guidance-box {
        margin-top: 1em;
        padding: 0.6em 0.8em;
        background: #f0fff4;
        border-left: 3px solid #27ae60;
        border-radius: 4px;
    }
    .guidance-box ul { margin: 0.3em 0 0 1.2em; font-size: 9pt; }
    .guidance-box li { margin-bottom: 0.2em; }
    .guidance-note { font-size: 8pt; color: #999; font-style: italic; margin-top: 0.5em; }

    /* Footer note */
    .footer-note {
        margin-top: 3cm;
        padding: 1em;
        background: #f8f9fa;
        border-radius: 6px;
    }
    .footer-note p { margin-bottom: 0.5em; font-size: 9pt; color: #555; }
    """


def _esc(s: Optional[str]) -> str:
    if not s:
        return ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _fmt_date(dt) -> Optional[str]:
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%Y-%m-%d")
