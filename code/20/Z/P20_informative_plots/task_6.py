import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(46)
# кількість відвідувачів сайту бібліотеки за день, 2025 рік
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
day = np.arange(dates.size)
season = 1 + 0.25 * np.cos(2 * np.pi * (day - 20) / 365)      # влітку менше
weekday_factor = np.where(dates.dayofweek >= 5, 0.55, 1.0)
visits = pd.Series(
    4200 * season * weekday_factor * rng.lognormal(0, 0.08, size=dates.size),
    index=dates,
)
visits["2025-09-01":] *= 1.35                       # новий навчальний рік
visits["2025-04-14"] = 90                           # збій сервера
visits["2025-11-20"] *= 2.0                         # розсилка про нові книги
visits = visits.round()

# палітра Okabe-Ito
BLUE = "#0072B2"
ORANGE = "#E69F00"

thousands = FuncFormatter(lambda value, _pos: f"{value / 1000:.0f}k")

fig, (ax, ax_week) = plt.subplots(
    1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [3, 1]}
)

# --- ліворуч: щоденні відвідування й ковзне середнє ---
rolling = visits.rolling(7, center=True).mean()
ax.plot(visits.index, visits, color="0.75", linewidth=0.8, label="daily")
ax.plot(rolling.index, rolling, color=BLUE, linewidth=2.5, label="7-day average")

summer_start, summer_end = pd.Timestamp("2025-07-01"), pd.Timestamp("2025-09-01")
ax.axvspan(summer_start, summer_end, color="0.95", zorder=0)
ax.text(summer_start + (summer_end - summer_start) / 2, 0.97, "summer break",
        transform=ax.get_xaxis_transform(), ha="center", va="top", color="0.4", fontsize=9)

# події знаходимо в даних: мінімум - збій, максимум - розсилка
box = {"boxstyle": "round,pad=0.4", "facecolor": "white", "edgecolor": "0.6"}
outage_day, peak_day = visits.idxmin(), visits.idxmax()
ax.annotate(f"server outage\n{outage_day:%d %b}: {visits[outage_day]:,.0f} visits",
            xy=(outage_day, visits[outage_day]), xytext=(outage_day + pd.Timedelta(days=12), 1900),
            bbox=box, fontsize=9, va="center",
            arrowprops={"arrowstyle": "->", "connectionstyle": "angle,angleA=180,angleB=90",
                        "color": "0.2"})
ax.annotate(f"newsletter\n{peak_day:%d %b}: {visits[peak_day]:,.0f} visits",
            xy=(peak_day, visits[peak_day]), xytext=(peak_day - pd.Timedelta(days=75), 12_300),
            bbox=box, fontsize=9, va="center",
            arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=-0.1", "color": "0.2"})

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.yaxis.set_major_formatter(thousands)
ax.set_xlim(dates[0], dates[-1])
ax.set_ylim(0, visits.max() * 1.05)
ax.grid(axis="y", color="0.9")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", ncol=2, frameon=False)

new_year_mean = visits["2025-09-01":].mean()
first_half_mean = visits["2025-01-01":"2025-06-30"].mean()
growth = (new_year_mean / first_half_mean - 1) * 100
ax.set_title(f"Daily visits; after 1 Sep the average is {growth:+.0f}% vs Jan-Jun",
             loc="left", color="0.4", pad=10)

# --- праворуч: середнє за днем тижня ---
weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
by_weekday = visits.groupby(visits.index.dayofweek).mean()
colors = [ORANGE if index >= 5 else BLUE for index in by_weekday.index]
bars = ax_week.bar(weekday_names, by_weekday.to_numpy(), color=colors, width=0.7)
ax_week.bar_label(bars, labels=[f"{v / 1000:.1f}k" for v in by_weekday], padding=3)

ax_week.set_yticks([])
ax_week.spines[["top", "right", "left"]].set_visible(False)
ax_week.tick_params(axis="x", length=0)

weekend_drop = (by_weekday.loc[5:].mean() / by_weekday.loc[:4].mean() - 1) * 100
ax_week.set_title(f"Average by weekday; weekends {weekend_drop:+.0f}%",
                  loc="left", color="0.4", pad=10)

fig.suptitle("Library website: the new academic year brought more readers",
             x=0.01, ha="left", fontsize=16, fontweight="bold")
fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.subplots_adjust(left=0.03, right=0.995, top=0.86, bottom=0.08, wspace=0.01)

fig.savefig("task_6.png", dpi=100)
plt.show()
