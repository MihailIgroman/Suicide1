import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
hours = np.arange(6, 21)
# УФ-індекс у ясний день: рядок - місяць, стовпець - година
peak = np.array([1.2, 2.0, 3.6, 5.2, 6.8, 7.9, 8.4, 7.2, 5.1, 3.0, 1.5, 0.9])
day_shape = np.clip(np.cos((hours - 13) / 7 * np.pi / 2), 0, None) ** 2
uv = (peak.reshape(-1, 1) * day_shape).round()

level_names = ["Low", "Moderate", "High", "Very high", "Extreme"]
level_colors = ["#4EB400", "#F7E400", "#F85900", "#D8001D", "#6B49C8"]

# межі рівнів ВООЗ: кожен інтервал - один колір
bounds = [0, 3, 6, 8, 11, 13]
cmap = ListedColormap(level_colors)
norm = BoundaryNorm(bounds, ncolors=cmap.N)

fig, ax = plt.subplots(figsize=(11, 5.5))
image = ax.imshow(uv, cmap=cmap, norm=norm, aspect="auto")

for row in range(uv.shape[0]):
    for col in range(uv.shape[1]):
        value = uv[row, col]
        # на темних клітинках (дуже високий і вище) - білий текст
        color = "white" if value >= bounds[3] else "black"
        ax.text(col, row, f"{value:.0f}", ha="center", va="center", fontsize=8, color=color)

ax.set_xticks(range(hours.size), [f"{h}:00" for h in hours])
ax.set_yticks(range(len(months)), months)
# білі лінії між клітинками - сітка за допоміжними поділками
ax.set_xticks(np.arange(-0.5, hours.size), minor=True)
ax.set_yticks(np.arange(-0.5, len(months)), minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="both", length=0)
ax.spines[:].set_visible(False)

colorbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.05)
# назви рівнів посередині кожного кольору
middles = [(low + high) / 2 for low, high in zip(bounds[:-1], bounds[1:])]
colorbar.set_ticks(middles, labels=level_names)
colorbar.ax.tick_params(length=0)
colorbar.outline.set_visible(False)

# перший і останній місяць, коли денний максимум - високий або вищий
high_months = np.where(uv.max(axis=1) >= bounds[2])[0]
first, last = months[high_months[0]], months[high_months[-1]]
fig.suptitle(f"From {first} to {last} protect your skin at midday",
             x=0.01, ha="left", fontsize=16, fontweight="bold")
ax.set_title("UV index on a clear day by month and hour", loc="left", color="0.4", pad=10)

fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.subplots_adjust(left=0.035, right=0.93, top=0.86, bottom=0.07)

fig.savefig("task_3.png", dpi=100)
plt.show()
