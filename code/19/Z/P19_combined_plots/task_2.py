import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]
# витрати студента, грн
expenses = {
    "Rent": np.array([4500, 4500, 4500, 4500, 4500, 4500, 4800, 4800, 4800]),
    "Food": np.array([3200, 3400, 3300, 4100, 3000, 3100, 3300, 3200, 3400]),
    "Transport": np.array([600, 650, 700, 750, 700, 650, 600, 550, 500]),
    "Fun": np.array([900, 700, 600, 2100, 400, 800, 700, 900, 1100]),
}
budget = 10000

plt.style.use("ggplot")

fig, (ax_bars, ax_pie) = plt.subplots(
    1, 2, figsize=(12, 4.5), gridspec_kw={"width_ratios": [2, 1]}
)

# --- ліворуч: стовпчики зі стеком ---
x = np.arange(len(months))
bottom = np.zeros(len(months))
colors = {}
for name, values in expenses.items():
    bars = ax_bars.bar(x, values, bottom=bottom, width=0.7, label=name)
    colors[name] = bars.patches[0].get_facecolor()
    bottom += values

totals = bottom
# підписи сум над останнім (верхнім) шаром стеку
ax_bars.bar_label(bars, labels=[f"{t:,.0f}" for t in totals], padding=3,
                  fontsize=8, fontweight="bold")

ax_bars.axhline(budget, color="black", linestyle="--", linewidth=1)
ax_bars.text(-0.4, budget + 150, f"budget {budget:,}", fontsize=9)

ax_bars.set_xticks(x, months)
# місяці з перевищенням бюджету - червоним
for label, total in zip(ax_bars.get_xticklabels(), totals):
    if total > budget:
        label.set_color("tab:red")

ax_bars.set_ylim(0, totals.max() * 1.1)
ax_bars.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax_bars.set_ylabel("UAH")
ax_bars.set_title("Monthly expenses", pad=28)

# легенда у зворотному порядку: як шари стеку, згори вниз
handles, labels = ax_bars.get_legend_handles_labels()
ax_bars.legend(handles[::-1], labels[::-1], loc="lower center",
               bbox_to_anchor=(0.5, 1.0), ncol=4, frameon=False, fontsize=9)

# --- праворуч: кільцева діаграма за весь рік ---
year_totals = {name: values.sum() for name, values in expenses.items()}
grand_total = sum(year_totals.values())

ax_pie.pie(
    list(year_totals.values()),
    labels=list(year_totals.keys()),
    colors=[colors[name] for name in year_totals],
    autopct="%.0f%%",
    pctdistance=0.8,
    startangle=90,
    counterclock=False,
    wedgeprops={"width": 0.4, "edgecolor": "white"},
    textprops={"fontsize": 9},
)
ax_pie.text(0, 0, f"{grand_total:,}\nUAH", ha="center", va="center",
            fontsize=13, fontweight="bold")
ax_pie.set_title("Share of the year")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_2.png", dpi=100)
plt.show()
