"""Shared manuscript figure style rules for BMC Geriatrics outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.text import Text


MANUSCRIPT_WIDTH_MM = 180.0
MANUSCRIPT_MAX_HEIGHT_MM = 170.0
MM_PER_INCH = 25.4

MANUSCRIPT_WIDTH_IN = MANUSCRIPT_WIDTH_MM / MM_PER_INCH
MANUSCRIPT_MAX_HEIGHT_IN = MANUSCRIPT_MAX_HEIGHT_MM / MM_PER_INCH

MANUSCRIPT_FONT_FAMILY = "Arial"
MANUSCRIPT_FONT_PT = 7.0
PANEL_LABEL_FONT_PT = 8.0

_ARIAL_CANDIDATES = [
    Path("/mnt/c/Windows/Fonts/arial.ttf"),
    Path("/mnt/c/Windows/Fonts/arialbd.ttf"),
    Path("/mnt/c/Windows/Fonts/ariali.ttf"),
    Path("/mnt/c/Windows/Fonts/arialbi.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/ariali.ttf"),
    Path("C:/Windows/Fonts/arialbi.ttf"),
]


def register_arial() -> None:
    """Register Windows Arial fonts for WSL/Matplotlib without installing packages."""
    found = False
    for font_path in _ARIAL_CANDIDATES:
        if font_path.exists():
            font_manager.fontManager.addfont(str(font_path))
            found = True
    if not found:
        raise RuntimeError(
            "Arial font files were not found. Expected /mnt/c/Windows/Fonts/arial*.ttf "
            "or C:/Windows/Fonts/arial*.ttf."
        )
    font_manager.findfont(MANUSCRIPT_FONT_FAMILY, fallback_to_default=False)


def manuscript_figsize(width_in: float, height_in: float) -> tuple[float, float]:
    """Scale a source figure to 180 mm wide while respecting the 170 mm height cap."""
    if width_in <= 0 or height_in <= 0:
        raise ValueError("Figure dimensions must be positive.")
    scale = MANUSCRIPT_WIDTH_IN / width_in
    scaled_width = MANUSCRIPT_WIDTH_IN
    scaled_height = height_in * scale
    if scaled_height > MANUSCRIPT_MAX_HEIGHT_IN:
        scale = MANUSCRIPT_MAX_HEIGHT_IN / height_in
        scaled_width = width_in * scale
        scaled_height = MANUSCRIPT_MAX_HEIGHT_IN
    return scaled_width, scaled_height


def apply_manuscript_figure_style() -> None:
    """Apply the locked journal figure typography and editable-vector settings."""
    register_arial()
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "font.family": MANUSCRIPT_FONT_FAMILY,
            "font.sans-serif": [MANUSCRIPT_FONT_FAMILY],
            "font.size": MANUSCRIPT_FONT_PT,
            "axes.labelsize": MANUSCRIPT_FONT_PT,
            "axes.titlesize": MANUSCRIPT_FONT_PT,
            "xtick.labelsize": MANUSCRIPT_FONT_PT,
            "ytick.labelsize": MANUSCRIPT_FONT_PT,
            "legend.fontsize": MANUSCRIPT_FONT_PT,
            "legend.title_fontsize": MANUSCRIPT_FONT_PT,
            "figure.titlesize": MANUSCRIPT_FONT_PT,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.usetex": False,
        }
    )


def _is_panel_label(text: str) -> bool:
    clean = text.strip()
    return len(clean) == 1 and clean.isalpha()


def normalize_manuscript_text(fig: mpl.figure.Figure) -> None:
    """Normalize all existing text artists after a capsule script has drawn them."""
    for artist in fig.findobj(match=Text):
        label = artist.get_text()
        if not label:
            continue
        artist.set_fontfamily(MANUSCRIPT_FONT_FAMILY)
        artist.set_fontstyle("normal")
        if _is_panel_label(str(label)):
            artist.set_fontsize(PANEL_LABEL_FONT_PT)
            artist.set_fontweight("bold")
        else:
            artist.set_fontsize(MANUSCRIPT_FONT_PT)


def finalize_manuscript_figure(fig: mpl.figure.Figure) -> None:
    """Set final dimensions and normalize typography before export."""
    width, height = fig.get_size_inches()
    fig.set_size_inches(*manuscript_figsize(float(width), float(height)), forward=True)
    normalize_manuscript_text(fig)


def save_manuscript_figure(
    fig: mpl.figure.Figure,
    png_path: Path,
    pdf_path: Path,
    svg_path: Path,
    *,
    preview_dpi: int = 300,
) -> None:
    """Save preview PNG plus editable PDF/SVG using the locked manuscript style."""
    finalize_manuscript_figure(fig)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=preview_dpi)
    fig.savefig(pdf_path)
    fig.savefig(svg_path)


FIGURE_RULE_SUMMARY = (
    "Main figure width 180 mm; maximum height 170 mm; Arial; ordinary text 7 pt; "
    "panel labels 8 pt bold upright; PDF uses Type 42 fonts; SVG preserves text."
)
