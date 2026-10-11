import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(42)
groups = ["KI-31", "KI-32", "KI-33", "KI-34"]
scores = [
    rng.normal(71, 11, size=28).clip(0, 100).round(),
    rng.normal(78, 6, size=14).clip(0, 100).round(),
    np.concatenate([rng.normal(58, 6, size=13), rng.normal(87, 4, size=13)]).round(),
    rng.normal(65, 14, size=31).clip(0, 100).round(),
]

# загальні налаштування один раз для всіх Axes
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.grid.axis"] = "y"
plt.rcParams["grid.alpha"] = 0.4

# групи за медіаною, від найбільшої
medians = np.array([np.median(s) for s in scores])
order = np.argsort(medians)[::-1]
ordered_groups = [groups[i] for i in order]
ordered_scores = [scores[i] for i in order]
positions = np.arange(1, len(groups) + 1)
colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

fig, (ax_box, ax_violin) = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)

# --- ліворуч: boxplot + точки ---
ax_box.boxplot(
    ordered_scores,
    positions=positions,
    widths=0.5,
    showmeans=True,
    showfliers=False,
    medianprops={"color": "black"},
    meanprops={"marker": "D", "markerfacecolor": "white",
               "markeredgecolor": "black", "markersize": 7},
)

jitter_rng = np.random.default_rng(0)       # окремий генератор для розкиду точок
for position, data, color in zip(positions, ordered_scores, colors):
    jitter = jitter_rng.uniform(-0.12, 0.12, size=data.size)
    ax_box.scatter(position + jitter, data, s=18, color=color, alpha=0.7, zorder=3)
    ax_box.text(position, 103, f"n={data.size}", ha="center", color="0.4", fontsize=9)

ax_box.set_xticks(positions, ordered_groups)
ax_box.set_ylim(25, 108)
ax_box.set_ylabel("Score")
ax_box.set_title("Exam scores: boxplot + points")

# --- праворуч: violin plot з медіаною та квартилями ---
parts = ax_violin.violinplot(ordered_scores, positions=positions, widths=0.6,
                             showextrema=False)
for body, color in zip(parts["bodies"], colors):
    body.set_facecolor(color)
    body.set_edgecolor("0.3")
    body.set_alpha(0.5)

for position, data in zip(positions, ordered_scores):
    q1, median, q3 = np.percentile(data, [25, 50, 75])
    ax_violin.hlines(median, position - 0.1, position + 0.1, color="black", linewidth=1.5)
    ax_violin.hlines([q1, q3], position - 0.1, position + 0.1, color="0.3",
                     linestyle="--", linewidth=1.5)

ax_violin.set_xticks(positions, ordered_groups)
ax_violin.set_title("Exam scores: violin (median, Q1, Q3)")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_3.png", dpi=100)
plt.show()
