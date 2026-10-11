import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(44)
regions = ["North", "South", "East", "West", "Center", "Online"]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# план і факт продажів, тис. грн: рядок - регіон, стовпець - місяць
plan = np.array([120, 90, 100, 80, 150, 60]).reshape(-1, 1) * np.ones(12)
trend = np.array([-0.06, 0.02, 0.0, -0.10, 0.04, 0.03]).reshape(-1, 1) * np.arange(12) / 11
fact = plan * (1 + trend + rng.normal(0, 0.05, size=(6, 12)))

deviation = (fact / plan - 1) * 100                       # відхилення за місяць, %
year_deviation = (fact.sum(axis=1) / plan.sum(axis=1) - 1) * 100

# шкала симетрична відносно нуля: 0 - білий
limit = np.abs(deviation).max()

fig, (ax_map, ax_year) = plt.subplots(
    1, 2, figsize=(13, 4.5), gridspec_kw={"width_ratios": [3, 1]}
)

# --- ліворуч: теплова карта ---
image = ax_map.imshow(deviation, cmap="RdBu", vmin=-limit, vmax=limit, aspect="auto")
for row in range(deviation.shape[0]):
    for col in range(deviation.shape[1]):
        value = deviation[row, col]
        color = "white" if abs(value) > 0.6 * limit else "black"
        # спершу округлення, потім знак: -0.3 показується як +0, а не -0
        ax_map.text(col, row, f"{round(value):+d}", ha="center", va="center",
                    color=color, fontsize=9)

ax_map.set_xticks(range(len(months)), months)
ax_map.set_yticks(range(len(regions)), regions)
ax_map.tick_params(length=0)
ax_map.spines[:].set_visible(False)
ax_map.set_title("Sales vs plan by month, %")

# шкала кольорів під картою; inset_axes не зменшує саму карту,
# тож рядки карти й графік праворуч лишаються на одній висоті
colorbar_axes = ax_map.inset_axes([0.25, -0.21, 0.5, 0.06])
colorbar = fig.colorbar(image, cax=colorbar_axes, orientation="horizontal")
colorbar.set_label("Deviation from plan, %")

# --- праворуч: відхилення за рік (lollipop) ---
y = np.arange(len(regions))
year_colors = np.where(year_deviation >= 0, "tab:blue", "tab:red")
ax_year.hlines(y, 0, year_deviation, color=year_colors, linewidth=2)
ax_year.scatter(year_deviation, y, color=year_colors, s=60, zorder=3)
ax_year.axvline(0, color="black", linewidth=1)

for yi, value in zip(y, year_deviation):
    offset = 8 if value >= 0 else -8
    ax_year.annotate(f"{value:+.1f}%", xy=(value, yi), xytext=(offset, 0),
                     textcoords="offset points", va="center",
                     ha="left" if value >= 0 else "right", fontsize=9)

span = np.abs(year_deviation).max() * 2.2
ax_year.set_xlim(-span, span)
ax_year.set_ylim(len(regions) - 0.5, -0.5)          # North угорі, як у теплової карти
ax_year.set_xticks([])
ax_year.set_yticks([])
ax_year.spines[:].set_visible(False)
ax_year.set_title("Year total vs plan")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=0.3, wspace=0.08)

fig.savefig("task_4.png", dpi=100)
plt.show()
