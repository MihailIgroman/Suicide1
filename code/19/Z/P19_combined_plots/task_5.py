import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import StrMethodFormatter

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(45)
platforms = ["Android", "iOS", "Web"]
# активні користувачі за тиждень, тис.
weeks = np.arange(1, 53)
users = pd.DataFrame({
    "Android": 20 + 0.35 * weeks + rng.normal(0, 1.2, size=52),
    "iOS": 12 + 0.25 * weeks + rng.normal(0, 0.9, size=52),
    "Web": 18 - 0.12 * weeks + rng.normal(0, 1.0, size=52),
}, index=weeks)
# тиждень 30: збій серверів
users.loc[30] *= 0.7

# 3000 сесій: платформа і тривалість, хв
n = 3000
sessions = pd.DataFrame({
    "platform": rng.choice(platforms, size=n, p=[0.5, 0.3, 0.2]),
})
median_minutes = sessions["platform"].map({"Android": 6, "iOS": 8, "Web": 4})
sessions["minutes"] = (median_minutes * rng.lognormal(0, 0.7, size=n)).round(1)

plt.style.use("seaborn-v0_8-whitegrid")
colors = {"Android": "tab:blue", "iOS": "tab:orange", "Web": "tab:green"}

fig, axes = plt.subplot_mosaic(
    [["area", "area", "change"],
     ["box", "bar", "change"]],
    figsize=(14, 7.5),
    gridspec_kw={"width_ratios": [1, 1, 0.85]},
)

# --- активні користувачі: площі зі стеком ---
ax = axes["area"]
ax.stackplot(weeks, [users[p] for p in platforms], labels=platforms,
             colors=[colors[p] for p in platforms], alpha=0.85)
total = users.sum(axis=1)
outage_week = total.diff().idxmin()           # тиждень з найбільшим падінням
ax.annotate("server outage", xy=(outage_week, total[outage_week] + 9),
            xytext=(outage_week + 5, 90), ha="center", va="center", fontsize=9,
            arrowprops={"arrowstyle": "->", "color": "black"})
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], loc="upper left", frameon=True)
ax.set_xlim(weeks[0], weeks[-1])
ax.set_ylim(0, 100)
ax.set_title("Weekly active users by platform")
ax.set_xlabel("Week")
ax.set_ylabel("Thousand users")

# --- зміна загальної кількості до попереднього тижня ---
ax = axes["change"]
change = total.diff().dropna()
change_colors = np.where(change >= 0, "tab:green", "tab:red")
ax.barh(change.index, change.to_numpy(), color=change_colors, height=0.8)
ax.axvline(0, color="black", linewidth=1)
ax.set_ylim(change.index[-1] + 0.5, change.index[0] - 0.5)   # перший тиждень угорі
ax.set_title("Weekly change of total")
ax.set_xlabel("Thousand users")
ax.set_ylabel("Week")

# --- тривалість сесій: boxplot на логарифмічній шкалі ---
ax = axes["box"]
groups = [sessions.loc[sessions["platform"] == p, "minutes"] for p in platforms]
box = ax.boxplot(groups, patch_artist=True, widths=0.5,
                 medianprops={"color": "black"},
                 flierprops={"marker": "o", "markersize": 4, "alpha": 0.3,
                             "markerfacecolor": "none", "markeredgecolor": "0.4"})
for patch, platform in zip(box["boxes"], platforms):
    patch.set_facecolor(colors[platform])
ax.set_xticks(range(1, len(platforms) + 1), platforms)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:g}"))
ax.set_title("Session duration")
ax.set_ylabel("Minutes (log scale)")

# --- середня тривалість зі стандартною похибкою ---
ax = axes["bar"]
stats = sessions.groupby("platform")["minutes"].agg(["mean", "std", "count"]).loc[platforms]
stats["se"] = stats["std"] / np.sqrt(stats["count"])
bars = ax.bar(platforms, stats["mean"], yerr=stats["se"], capsize=6,
              color=[colors[p] for p in platforms], alpha=0.9)
ax.bar_label(bars, labels=[f"{m:.1f}\nn={c}" for m, c in zip(stats["mean"], stats["count"])],
             padding=12)
ax.set_ylim(0, 14)
ax.set_title("Mean session duration (error bars: SE)")
ax.set_ylabel("Minutes")

fig.suptitle("Mobile app: 2025 report (simulated data)", fontweight="bold")
fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_5.png", dpi=100)
plt.show()
