import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import StrMethodFormatter

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(38)
dates = pd.date_range("2025-08-01", periods=120, freq="D")
day = np.arange(120)
visits = 500 + 5 * day + rng.normal(0, 60, size=120)
visits[dates.dayofweek >= 5] *= 0.6

# сервер не працював: дні з індексами 40..44
visits[40:45] = np.nan

daily = pd.Series(visits, index=dates)
# ковзне середнє за 7 днів; NaN не нулі, тож вікно з <4 значень дає розрив
rolling = daily.rolling(7, min_periods=4).mean()

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(daily.index, daily, color="tab:blue", linewidth=0.8, alpha=0.6, label="daily")
ax.plot(rolling.index, rolling, color="tab:blue", linewidth=2.5, label="7-day mean")

# смуга простою: дні без даних, по півдня з кожного боку
half_day = pd.Timedelta(hours=12)
down = dates[daily.isna().to_numpy()]
down_start, down_end = down[0] - half_day, down[-1] + half_day
ax.axvspan(down_start, down_end, color="tab:red", alpha=0.12, linewidth=0)
ax.text(down_start + (down_end - down_start) / 2, 270, "server down",
        color="tab:red", ha="center", va="center")

locator = mdates.MonthLocator()
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax.set_xlim(dates[0], dates[-1])
ax.set_ylim(bottom=0)
ax.set_title("Site visits")
ax.set_ylabel("Visitors per day")
ax.grid(axis="y", alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower right", frameon=False)

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_2.png", dpi=100)
plt.show()
