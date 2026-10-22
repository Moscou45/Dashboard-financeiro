from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

BLUE = "#526bff"
TEAL = "#29b6a6"
RED = "#ef6a72"
GOLD = "#f5b544"
PALETTE = [BLUE, TEAL, GOLD, RED, "#9270db", "#47a8e8", "#8bc34a", "#ff8a65"]


def _finish(fig, title: str):
    fig.patch.set_facecolor("white")
    fig.suptitle(title, x=0.04, ha="left", fontsize=13, fontweight="bold", color="#243147")
    fig.tight_layout(rect=(0, 0, 1, .93))
    return fig


def bars3d(labels, series, title, series_names, colors=None, currency=True):
    colors = colors or [BLUE, RED, TEAL]
    fig = plt.figure(figsize=(8.2, 3.5))
    ax = fig.add_subplot(111, projection="3d")
    x = np.arange(len(labels))
    width = .62 / max(1, len(series))
    vals = np.asarray(series, dtype=float)
    floor = min(0.0, float(np.nanmin(vals)) * 1.05) if vals.size else 0.0
    for i, values in enumerate(series):
        y = np.full(len(labels), i * width)
        heights = np.asarray(values, dtype=float) - floor
        ax.bar3d(x - .3 + i * width, y, np.full(len(labels), floor), width * .9, width * .85, heights,
                 color=colors[i % len(colors)], shade=True, alpha=.95, zsort="average")
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_yticks(np.arange(len(series_names)) * width + width / 2, series_names, fontsize=8)
    ax.set_zlim(floor, max(1.0, float(np.nanmax(vals)) * 1.13))
    ax.set_zlabel("R$" if currency else "Quantidade", labelpad=2, fontsize=8)
    ax.view_init(elev=22, azim=-57)
    ax.grid(True, alpha=.18)
    ax.xaxis.pane.set_alpha(.04); ax.yaxis.pane.set_alpha(.02); ax.zaxis.pane.set_alpha(.02)
    ax.tick_params(axis="z", labelsize=7, pad=0)
    return _finish(fig, title)


def pie3d(labels, values, title):
    vals = np.asarray(values, dtype=float)
    keep = vals > 0
    labels = [l for l, k in zip(labels, keep) if k]
    vals = vals[keep]
    fig = plt.figure(figsize=(5.8, 3.5))
    ax = fig.add_subplot(111, projection="3d")
    if vals.size == 0:
        ax.text2D(.3, .5, "Sem dados no período", transform=ax.transAxes, color="#738094")
    else:
        theta = np.r_[0, np.cumsum(vals / vals.sum() * 2 * np.pi)]
        radius, height = 1.0, .14
        for i, (start, end) in enumerate(zip(theta[:-1], theta[1:])):
            angles = np.linspace(start, end, max(16, int((end-start)*30)))
            top = [(radius*np.cos(a), radius*np.sin(a), height) for a in angles]
            bottom = [(x, y, 0) for x, y, _ in top]
            side1 = [(radius*np.cos(start), radius*np.sin(start), 0), (radius*np.cos(end), radius*np.sin(end), 0), (radius*np.cos(end), radius*np.sin(end), height), (radius*np.cos(start), radius*np.sin(start), height)]
            faces = [top + [(0, 0, height)], bottom + [(0, 0, 0)], side1]
            for a, b in zip(angles[:-1], angles[1:]):
                faces.append([(radius*np.cos(a), radius*np.sin(a), 0), (radius*np.cos(b), radius*np.sin(b), 0), (radius*np.cos(b), radius*np.sin(b), height), (radius*np.cos(a), radius*np.sin(a), height)])
            ax.add_collection3d(Poly3DCollection(faces, facecolors=PALETTE[i % len(PALETTE)], edgecolors="white", linewidths=.5))
        ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_zlim(0, .5)
        ax.view_init(elev=27, azim=-55); ax.set_axis_off()
        ax.legend([f"{n} — R$ {v:,.2f}" for n, v in zip(labels, vals)], loc="center left", bbox_to_anchor=(.83, .5), frameon=False, fontsize=8)
    return _finish(fig, title)


def line_chart(frame: pd.DataFrame, title: str):
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.plot(frame["month_label"], frame["revenue"], marker="o", lw=2, color=BLUE, label="Receitas")
    ax.plot(frame["month_label"], frame["expenses"], marker="o", lw=2, color=RED, label="Despesas")
    ax.fill_between(np.arange(len(frame)), frame["revenue"].to_numpy(), alpha=.10, color=BLUE)
    ax.set_xticks(np.arange(len(frame)), frame["month_label"], fontsize=8)
    ax.grid(axis="y", alpha=.18); ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.set_ylabel("R$"); ax.spines[["top", "right"]].set_visible(False)
    return _finish(fig, title)
