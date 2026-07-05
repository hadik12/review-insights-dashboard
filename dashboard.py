from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

from clustering import ThemeReport

POS, NEG, NEU = "#16a34a", "#dc2626", "#9ca3af"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"
_HTML_OPTS = dict(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})


def _pie(counts: dict) -> str:
    fig = go.Figure(go.Pie(
        labels=["Positive", "Negative", "Neutral"],
        values=[counts.get("positive", 0), counts.get("negative", 0), counts.get("neutral", 0)],
        marker_colors=[POS, NEG, NEU], hole=0.45, sort=False,
    ))
    fig.update_layout(title="Sentiment breakdown", height=360, margin=dict(t=50, b=10, l=10, r=10))
    return pio.to_html(fig, **_HTML_OPTS)


def _themes_bar(report: ThemeReport) -> str:
    rows = ([(t.theme, t.mention_count, NEG) for t in report.top_complaints[:5]]
            + [(t.theme, t.mention_count, POS) for t in report.top_praises[:5]])
    rows.sort(key=lambda r: r[1])
    fig = go.Figure(go.Bar(
        x=[r[1] for r in rows], y=[r[0] for r in rows], orientation="h",
        marker_color=[r[2] for r in rows],
        text=[r[1] for r in rows], textposition="auto",
    ))
    fig.update_layout(title="Top themes (mentions) — red = complaints, green = praise",
                      height=420, margin=dict(t=50, b=20, l=10, r=10))
    return pio.to_html(fig, **_HTML_OPTS)


def _trend(timeseries: list[tuple]) -> str:
    fig = go.Figure(go.Scatter(
        x=[p[0] for p in timeseries], y=[round(p[1] * 100) for p in timeseries],
        mode="lines+markers", line=dict(color="#2563eb", width=3), marker=dict(size=8),
    ))
    fig.update_layout(title="% positive over time", height=340, yaxis=dict(range=[0, 100], ticksuffix="%"),
                      margin=dict(t=50, b=20, l=10, r=10))
    return pio.to_html(fig, **_HTML_OPTS)


def _theme_list(title: str, themes, color: str) -> str:
    items = "".join(
        f'<li><span class="cnt" style="background:{color}">{t.mention_count}</span>'
        f'<b>{_esc(t.theme)}</b><br><span class="quote">“{_esc(t.example_quote)}”</span></li>'
        for t in themes[:5]
    )
    return f'<div class="card"><h3>{title}</h3><ul class="themes">{items}</ul></div>'


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(product: str, counts: dict, timeseries: list[tuple], report: ThemeReport, path: Path) -> None:
    total = sum(counts.values()) or 1
    pct = {k: round(counts.get(k, 0) / total * 100) for k in ("positive", "negative", "neutral")}
    kpi = lambda label, val, color: (
        f'<div class="kpi"><div class="kpi-val" style="color:{color}">{val}</div>'
        f'<div class="kpi-label">{label}</div></div>')

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Review Insights — {_esc(product)}</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  body {{ margin:0; font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif; background:#f4f5fa; color:#1f2430; }}
  header {{ background:linear-gradient(135deg,#4f46e5,#4338ca); color:#fff; padding:30px 26px; }}
  header h1 {{ margin:0 0 4px; font-size:24px; }} header p {{ margin:0; opacity:.9; }}
  main {{ max-width:1080px; margin:20px auto 60px; padding:0 16px; display:grid; gap:18px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }}
  .kpi {{ background:#fff; border-radius:12px; padding:16px; text-align:center; box-shadow:0 4px 14px rgba(0,0,0,.05); }}
  .kpi-val {{ font-size:30px; font-weight:700; }} .kpi-label {{ color:#6b7280; font-size:13px; margin-top:2px; }}
  .panel {{ background:#fff; border-radius:12px; padding:8px; box-shadow:0 4px 14px rgba(0,0,0,.05); }}
  .two {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  .card {{ background:#fff; border-radius:12px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,.05); }}
  .card h3 {{ margin:0 0 12px; font-size:16px; }}
  ul.themes {{ list-style:none; margin:0; padding:0; }}
  ul.themes li {{ padding:9px 0; border-bottom:1px solid #eef0f4; }}
  .cnt {{ display:inline-block; color:#fff; font-size:12px; font-weight:700; border-radius:999px; padding:1px 9px; margin-right:8px; }}
  .quote {{ color:#6b7280; font-size:13px; font-style:italic; }}
  @media(max-width:720px){{ .kpis,.two{{grid-template-columns:1fr}} }}
</style></head>
<body>
  <header><h1>📊 Review Insights — {_esc(product)}</h1>
  <p>{total} customer reviews analyzed</p></header>
  <main>
    <div class="kpis">
      {kpi("reviews", total, "#1f2430")}
      {kpi("positive", f"{pct['positive']}%", POS)}
      {kpi("negative", f"{pct['negative']}%", NEG)}
      {kpi("neutral", f"{pct['neutral']}%", NEU)}
    </div>
    <div class="two">
      <div class="panel">{_pie(counts)}</div>
      <div class="panel">{_trend(timeseries)}</div>
    </div>
    <div class="panel">{_themes_bar(report)}</div>
    <div class="two">
      {_theme_list("Top complaints", report.top_complaints, NEG)}
      {_theme_list("Top praises", report.top_praises, POS)}
    </div>
  </main>
</body></html>"""
    path.write_text(html, encoding="utf-8")
