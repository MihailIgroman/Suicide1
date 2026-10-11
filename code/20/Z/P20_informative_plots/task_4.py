import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(44)
years = np.arange(2014, 2026)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# відхилення середньомісячної температури від норми 1991-2020, градуси C
# рядок - рік, стовпець - місяць
trend = np.linspace(-0.7, 1.9, len(years)).reshape(-1, 1)
anomaly = (trend + rng.normal(0, 1.1, size=(len(years), 12))).round(1)
anomaly[2, 0] = -3.4    # холодний січень 2016

cmap = plt.get_cmap("RdBu_r")
# нуль - білий; синя і червона частини розтягуються незалежно
norm = TwoSlopeNorm(vmin=anomaly.min(), vcenter=0, vmax=anomaly.max())

fig, (ax_map, ax_year) = plt.subplots(
    1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [4, 1]}
)

image = ax_map.imshow(anomaly, cmap=cmap, norm=norm, aspect="auto")
ax_map.set_xticks(range(len(months)), months)
ax_map.set_yticks(range(len(years)), years)
ax_map.tick_params(length=0)
ax_map.spines[:].set_visible(False)

colorbar_axes = ax_map.inset_axes([0.2, -0.17, 0.6, 0.06])
colorbar = fig.colorbar(image, cax=colorbar_axes, orientation="horizontal")
colorbar.set_label("Deviation from 1991-2020 normal, °C")
colorbar.outline.set_visible(False)

# найхолодніший і найтепліший місяць - знаходимо в коді
box = {"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "0.4"}
arrow = {"arrowstyle": "->", "color": "0.15", "connectionstyle": "arc3,rad=0.3"}
for label, flat_index, xytext in [
    ("coldest", anomaly.argmin(), (3.0, 1.5)),
    ("warmest", anomaly.argmax(), (3.5, -1.5)),
]:
    row, col = np.unravel_index(flat_index, anomaly.shape)
    value = anomaly[row, col]
    ax_map.annotate(f"{label}: {months[col]} {years[row]}\n{value:+.1f} °C",
                    xy=(col, row), xytext=(col + xytext[0], row + xytext[1]),
                    bbox=box, arrowprops=arrow, fontsize=9, va="center")

# праворуч - середнє за рік, тією самою картою і нормуванням
year_mean = anomaly.mean(axis=1)
ax_year.barh(range(len(years)), year_mean, color=cmap(norm(year_mean)), height=0.7)
ax_year.axvline(0, color="0.2", linewidth=1)
for row, value in enumerate(year_mean):
    ax_year.annotate(f"{value:+.1f}", xy=(value, row), xytext=(4 if value >= 0 else -4, 0),
                     textcoords="offset points", va="center",
                     ha="left" if value >= 0 else "right", fontsize=9)

ax_year.set_ylim(len(years) - 0.5, -0.5)            # рядки на рівні теплової карти
ax_year.set_yticks([])
ax_year.spines[["top", "right", "left"]].set_visible(False)
ax_year.set_xlim(min(year_mean.min(), 0) - 0.4, year_mean.max() + 0.5)
ax_year.set_title("Year mean, °C")

warm_years = (year_mean > 0).sum()
fig.suptitle(f"{warm_years} of the last {len(years)} years were warmer than normal",
             x=0.01, ha="left", fontsize=16, fontweight="bold")
ax_map.set_title("Monthly temperature anomaly", loc="left", color="0.4", pad=10)

fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.2, wspace=0.03)

fig.savefig("task_4.png", dpi=100)
plt.show()
