"""
ui/theme.py — Shared theme helpers.
Design language: Premium Corporate / MercadoXR
Scientific, Clean, High Contrast.
"""
import plotly.graph_objects as go


# ── Plotly dark layout template ────────────────────────────────────────────
PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",          # transparente
    plot_bgcolor="rgba(25,25,25,0.6)",      # glass panel gris
    font=dict(family="Inter, -apple-system, sans-serif", color="#6b7280", size=12),
    title=dict(
        font=dict(color="#ffffff", size=14, family="Outfit, Inter, sans-serif"),
        x=0.02,
        xanchor="left",
        pad=dict(t=10, b=10)
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",   # cuadrícula gris muy tenue
        zeroline=False,
        tickfont=dict(color="#4b5563", size=11),
        title=dict(font=dict(color="#6b7280")),
        linecolor="rgba(255,255,255,0.06)",
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",   # cuadrícula gris
        zeroline=False,
        tickfont=dict(color="#4b5563", size=11),
        title=dict(font=dict(color="#6b7280")),
        linecolor="rgba(255,255,255,0.06)",
        showgrid=True,
    ),
    legend=dict(
        bgcolor="rgba(25,25,25,0.8)",
        bordercolor="rgba(255,255,255,0.06)",
        borderwidth=1,
        font=dict(color="#9ca3af", size=11),
        x=0.01, y=0.99,
        xanchor="left", yanchor="top",
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="rgba(15,15,15,0.95)",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(color="#d1d5db", size=12),
    ),
    margin=dict(l=48, r=24, t=52, b=44),
)


def apply_dark_theme(fig: go.Figure, **layout_overrides) -> go.Figure:
    """
    Apply the MercadoXR-inspired dark theme to a Plotly figure.
    """
    merged = {**PLOTLY_DARK, **layout_overrides}
    fig.update_layout(**merged)
    return fig


# ── Color palette (Serio y distinguible) ──────────────────────────────────
BRAND_COLORS = [
    "#ffffff",  # Blanco brillante
    "#3b82f6",  # Azul Real
    "#10b981",  # Verde Esmeralda
    "#f59e0b",  # Ámbar
    "#8b5cf6",  # Violeta
    "#ec4899",  # Rosa
    "#06b6d4",  # Cian
    "#f97316",  # Naranja
]

BENCH_COLORS = BRAND_COLORS


def dark_table_html(df) -> str:
    """
    Render a pandas DataFrame as a dark HTML table.
    """
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{v}</td>" for v in row.values)
        rows_html += f"<tr>{cells}</tr>"

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return (
        '<div class="dark-table-wrap">'
        "<table>"
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
        "</div>"
    )
