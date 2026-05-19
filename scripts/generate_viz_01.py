"""
Proposal static viz #1 — The Game Over Time (Visual 1 from team proposal).

Static stand-in for the planned D3 animated line chart with metric dropdown.
Shows league-average 3PA per team per game, 1996–2024, with Curry-era annotation.

Data:
  - Brescou/NBA-dataset-stats-player-team (1996–97 through 2022–23)
  - NocturneBear/NBA-Data-2010-2024 (2023–24 supplement)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BRESCOU_PATH = ROOT / "data" / "team_stats_traditional_rs.csv"
NOCTURNE_PATH = ROOT / "data" / "regular_season_totals_2010_2024.csv"
OUT_PATH = ROOT / "visuals" / "viz_01_game_over_time.png"

CURRY_ERA_SEASON = "2015-16"


def load_league_3pa_by_season() -> pd.DataFrame:
    trad = pd.read_csv(BRESCOU_PATH, usecols=["SEASON", "FG3A"])
    league = (
        trad.groupby("SEASON", as_index=False)
        .agg(avg_3pa=("FG3A", "mean"))
        .sort_values("SEASON")
    )

    # Append 2023-24 from game-level totals if not already present
    if league["SEASON"].iloc[-1] != "2023-24":
        games = pd.read_csv(NOCTURNE_PATH, usecols=["SEASON_YEAR", "FG3A"])
        y2024 = (
            games[games["SEASON_YEAR"] == "2023-24"]
            .groupby("SEASON_YEAR", as_index=False)
            .agg(avg_3pa=("FG3A", "mean"))
            .rename(columns={"SEASON_YEAR": "SEASON"})
        )
        league = pd.concat([league, y2024], ignore_index=True)

    league["season_start"] = league["SEASON"].str.slice(0, 4).astype(int)
    return league


def plot_game_over_time(season: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11, 6))

    x = range(len(season))
    y = season["avg_3pa"]

    # Curry era shading (2015-16 onward)
    curry_idx = season.index[season["SEASON"] == CURRY_ERA_SEASON][0]
    ax.axvspan(curry_idx, len(season) - 1, color="#c8102e", alpha=0.08, zorder=0)
    ax.axvline(curry_idx, color="#c8102e", linestyle="--", linewidth=1.5, alpha=0.85)

    ax.plot(
        x,
        y,
        color="#1d428a",
        linewidth=2.8,
        marker="o",
        markersize=6,
        markerfacecolor="#1d428a",
        markeredgewidth=0,
        zorder=3,
    )

    # Curry era callout
    curry_y = season.loc[season["SEASON"] == CURRY_ERA_SEASON, "avg_3pa"].iloc[0]
    ax.annotate(
        "Curry era\n(3-point explosion\naccelerates)",
        xy=(curry_idx, curry_y),
        xytext=(curry_idx + 2.5, curry_y + 4),
        fontsize=10,
        color="#8b0000",
        arrowprops=dict(arrowstyle="->", color="#c8102e", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="#c8102e", alpha=0.95),
    )

    first, last = season.iloc[0], season.iloc[-1]
    ax.annotate(
        f"{first['avg_3pa']:.1f}",
        xy=(0, first["avg_3pa"]),
        xytext=(8, -14),
        textcoords="offset points",
        fontsize=9,
        color="#444444",
    )
    ax.annotate(
        f"{last['avg_3pa']:.1f}",
        xy=(len(season) - 1, last["avg_3pa"]),
        xytext=(-10, 10),
        textcoords="offset points",
        ha="right",
        fontsize=9,
        color="#444444",
    )

    ax.set_title(
        "Visual 1 — The Game Over Time",
        fontsize=17,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Season", fontsize=12)
    ax.set_ylabel("League avg. 3-point attempts per team per game", fontsize=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels(season["SEASON"], rotation=50, ha="right", fontsize=8)
    ax.set_ylim(12, 40)

    era_patch = mpatches.Patch(color="#c8102e", alpha=0.25, label="Curry era (2015–16+)")
    ax.legend(handles=[era_patch], loc="upper left", frameon=True, fontsize=9)

    fig.text(
        0.01,
        0.01,
        "Proposal static mock-up · Final version: D3 dropdown (3PA, pace, PPG, midrange) + hover/click\n"
        "Sources: Brescou/NBA-dataset-stats-player-team; NocturneBear/NBA-Data-2010-2024",
        fontsize=7.5,
        color="#666666",
    )

    fig.tight_layout()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    plot_game_over_time(load_league_3pa_by_season())
