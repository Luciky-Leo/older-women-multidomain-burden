from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "manuscript" / "bmc_geriatrics_submission_burden_profiles_rescue"
OUT = ROOT / "outputs" / "phase45_workflow_schematic"


STEM = "supplementary_figure_s5_workflow_schematic"


def wrap_preserving_manual_breaks(text: str, width: int) -> str:
    if "\n" in text:
        return "\n".join(textwrap.fill(part, width=width) for part in text.splitlines())
    return textwrap.fill(text, width=width)


def setup_fonts() -> None:
    for candidate in [
        Path("/mnt/c/Windows/Fonts/arial.ttf"),
        Path("/mnt/c/Windows/Fonts/Arial.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]:
        if candidate.exists():
            font_manager.fontManager.addfont(str(candidate))
            break
    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.linewidth": 0.6,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
        }
    )


def draw_box(ax, x, y, w, h, step, title, detail, face, edge, badge_color) -> None:
    shadow = FancyBboxPatch(
        (x + 0.006, y - 0.010),
        w,
        h,
        boxstyle="round,pad=0.010,rounding_size=0.026",
        linewidth=0,
        edgecolor="none",
        facecolor="#000000",
        alpha=0.065,
        mutation_aspect=1,
        zorder=0,
    )
    ax.add_patch(shadow)
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.010,rounding_size=0.026",
        linewidth=0.95,
        edgecolor=edge,
        facecolor=face,
        mutation_aspect=1,
        zorder=1,
    )
    ax.add_patch(box)

    badge = Circle(
        (x + 0.038, y + h - 0.058),
        0.033,
        facecolor=badge_color,
        edgecolor=badge_color,
        linewidth=0,
        zorder=2,
    )
    ax.add_patch(badge)
    ax.text(
        x + 0.038,
        y + h - 0.060,
        str(step),
        ha="center",
        va="center",
        color="white",
        fontsize=8.2,
        fontweight="bold",
        zorder=3,
    )
    ax.text(
        x + 0.075,
        y + h - 0.040,
        wrap_preserving_manual_breaks(title, width=19),
        ha="left",
        va="top",
        fontsize=6.4,
        fontweight="bold",
        color="#111418",
        linespacing=1.08,
        zorder=3,
    )
    ax.text(
        x + w / 2,
        y + h * 0.385,
        textwrap.fill(detail, width=24),
        ha="center",
        va="center",
        fontsize=5.55,
        color="#111418",
        linespacing=1.12,
        zorder=3,
    )


def arrow(ax, start, end, color="#5d656c", rad=0.0) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=3.0,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=0,
            shrinkB=0,
            zorder=2.5,
        )
    )


def render() -> None:
    setup_fonts()
    PKG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(180 / 25.4, 92 / 25.4))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1.025)
    ax.set_ylim(0, 1)
    ax.axis("off")

    steps = [
        (
            1,
            "Source cohorts",
            "CHARLS, ELSA, HRS, KLoSA, LASI, MHAS and SHARE cleaned cohort inputs.",
            "#f6f7f8",
            "#6b737a",
            "#646c73",
        ),
        (
            2,
            "Women 50+\nscreen",
            "Cohort-specific baseline or analysis wave; source-screen denominator kept separate.",
            "#eaf8f9",
            "#1a6269",
            "#166a70",
        ),
        (
            3,
            "Sex coding confirmation",
            "Local Stata value labels and do-files confirm ragender=0 as women.",
            "#eaf8f9",
            "#1a6269",
            "#166a70",
        ),
        (
            4,
            "Four-domain\nharmonization",
            "Functional, cognitive, affective, cardiometabolic and chronic-disease burden scores.",
            "#f1faee",
            "#557a3f",
            "#4f7d38",
        ),
        (
            5,
            "Evidence-tier\nlock",
            "Strict core, functional bridge, baseline-only and validation-downgraded tiers fixed before claims.",
            "#fff4df",
            "#c38424",
            "#cf850f",
        ),
        (
            6,
            "Descriptive GMM\naudit",
            "Class selection, convergence, bootstrap stability, cross-method agreement and covariance diagnostics.",
            "#fff4df",
            "#c38424",
            "#cf850f",
        ),
        (
            7,
            "LFO functional-\nchange association",
            "Leave-functional-domain-out profiles tested against functional-change outcomes in strict-core cohorts.",
            "#fff0ec",
            "#b9685b",
            "#c04f45",
        ),
        (
            8,
            "Unresolved guardrails",
            "Survey-design recovery, hard-outcome harmonization, sex interaction, calibration and decision-curve audits.",
            "#f6f7f8",
            "#8d9398",
            "#858d94",
        ),
    ]

    w = 0.215
    h = 0.315
    xs = [0.030, 0.285, 0.540, 0.795]
    top_y = 0.610
    bottom_y = 0.135
    positions = [
        (xs[0], top_y),
        (xs[1], top_y),
        (xs[2], top_y),
        (xs[3], top_y),
        (xs[3], bottom_y),
        (xs[2], bottom_y),
        (xs[1], bottom_y),
        (xs[0], bottom_y),
    ]

    for step, pos in zip(steps, positions):
        draw_box(ax, pos[0], pos[1], w, h, *step)

    centers = [(x + w / 2, y + h / 2) for x, y in positions]
    # Top row left-to-right.
    for i in range(3):
        arrow(
            ax,
            (positions[i][0] + w + 0.004, centers[i][1]),
            (positions[i + 1][0] - 0.004, centers[i + 1][1]),
        )
    # Turn down from step 4 to step 5.
    arrow(
        ax,
        (centers[3][0], positions[3][1] - 0.004),
        (centers[4][0], positions[4][1] + h + 0.004),
        rad=0.0,
    )
    # Bottom row right-to-left.
    for i in range(4, 7):
        arrow(
            ax,
            (positions[i][0] - 0.004, centers[i][1]),
            (positions[i + 1][0] + w + 0.004, centers[i + 1][1]),
        )

    for ext in ["pdf", "svg", "png"]:
        target = PKG / f"{STEM}.{ext}"
        fig.savefig(target, dpi=300 if ext == "png" else None)
        mirror = OUT / f"{STEM}.{ext}"
        fig.savefig(mirror, dpi=300 if ext == "png" else None)
    plt.close(fig)

    brief = OUT / "framework_figure_brief.md"
    brief.write_text(
        "\n".join(
            [
                "# Supplementary Figure S5 Workflow Schematic",
                "",
                "Role: reviewer-facing workflow schematic.",
                "Subtype: linear audit chain with evidence guardrail checkpoints.",
                "Claim boundary: arrows show processing order only; they do not imply causal or predictive superiority.",
                "Runtime: Python matplotlib via WSL Ubuntu and research-py312.",
                "OpenAI image2 reference: outputs/phase45_workflow_schematic/openai_image2_reference.png.",
                "Output size: 180 mm width, 92 mm height.",
                "Exports: editable PDF, editable SVG text, 300 dpi PNG preview.",
                "",
                "Steps:",
                "1. Source cohorts",
                "2. Women 50+ screen",
                "3. Sex coding confirmation",
                "4. Four-domain harmonization",
                "5. Evidence-tier lock",
                "6. Descriptive GMM audit",
                "7. LFO functional-change association",
                "8. Unresolved guardrails",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(PKG / f"{STEM}.pdf")
    print(PKG / f"{STEM}.svg")
    print(PKG / f"{STEM}.png")
    print(brief)


if __name__ == "__main__":
    render()
