import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

years = np.arange(2018, 2026)
# заяви вступників за спеціальностями, тис.
applications = {
    "Computer Science": np.array([41, 46, 52, 61, 66, 74, 81, 88]),
    "Economics": np.array([58, 55, 53, 50, 47, 46, 44, 43]),
    "Law": np.array([52, 53, 55, 54, 56, 55, 57, 58]),
    "Medicine": np.array([35, 37, 40, 44, 43, 45, 47, 48]),
    "Psychology": np.array([22, 24, 27, 30, 32, 34, 35, 36]),
    "Philology": np.array([30, 29, 27, 26, 24, 23, 21, 20]),
}
highlight = "Computer Science"

HIGHLIGHT_COLOR = "#0072B2"
GRAY = "0.7"
TEXT_GRAY = "0.4"

# загальні налаштування рамок - один раз для всієї фігури
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.spines.left"] = False

fig, ax = plt.subplots(figsize=(10, 5.5))

# спершу сірі лінії, виділена - поверх них
for name, values in applications.items():
    if name == highlight:
        continue
    ax.plot(years, values, color=GRAY, linewidth=1.5)
    ax.annotate(f"{name} {values[-1]}", xy=(years[-1], values[-1]), xytext=(8, 0),
                textcoords="offset points", va="center", color=TEXT_GRAY, fontsize=10)

main = applications[highlight]
ax.plot(years, main, color=HIGHLIGHT_COLOR, linewidth=3, zorder=3)
ax.plot(years[0], main[0], "o", color=HIGHLIGHT_COLOR, zorder=3)
ax.annotate(f"{main[0]}", xy=(years[0], main[0]), xytext=(0, -12),
            textcoords="offset points", ha="center", va="top", color=HIGHLIGHT_COLOR)
ax.annotate(f"{highlight} {main[-1]}", xy=(years[-1], main[-1]), xytext=(8, 0),
            textcoords="offset points", va="center", color=HIGHLIGHT_COLOR,
            fontweight="bold", fontsize=10)

ax.set_xlim(years[0] - 0.15, years[-1])
ax.set_ylim(0, 100)
ax.set_xticks(years)
ax.tick_params(axis="y", length=0)
ax.grid(axis="y", color="0.9")

# заголовок - висновок; кратність зростання рахується з даних
growth = main[-1] / main[0]
fig.suptitle(f"{highlight} applications grew {growth:.1f}x since {years[0]}",
             x=0.01, ha="left", fontsize=16, fontweight="bold")
ax.set_title("Applications by specialty, thousands", loc="left", color=TEXT_GRAY, pad=10)

fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.subplots_adjust(left=0.035, right=0.815, top=0.86, bottom=0.08)

fig.savefig("task_1.png", dpi=100)
plt.show()
