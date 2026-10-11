import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

cities = ["Lviv", "Poltava", "Kyiv", "Odesa", "Dnipro", "Kharkiv", "Vinnytsia"]
# продажі, тис. грн
sales_2024 = np.array([290, 95, 480, 240, 200, 230, 120])
sales_2025 = np.array([310, 92, 540, 228, 215, 262, 151])

cities = np.array(cities)

fig, (ax_sales, ax_growth) = plt.subplots(
    1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [3, 2]}
)

# --- ліворуч: згруповані стовпчики, міста за продажами 2025 року ---
order = np.argsort(sales_2025)[::-1]
x = np.arange(cities.size)
width = 0.4

bars_2024 = ax_sales.bar(x - width / 2, sales_2024[order], width, color="0.7", label="2024")
bars_2025 = ax_sales.bar(x + width / 2, sales_2025[order], width, color="tab:blue", label="2025")
ax_sales.bar_label(bars_2024, padding=2, fontsize=8, color="0.4")
ax_sales.bar_label(bars_2025, padding=2, fontsize=8)

ax_sales.set_xticks(x, cities[order])
ax_sales.set_ylim(0, 600)
ax_sales.set_ylabel("Sales, thousand UAH")
ax_sales.set_title("Sales by city")
ax_sales.spines[["top", "right"]].set_visible(False)
ax_sales.legend(loc="upper right", ncol=2, frameon=False)

# --- праворуч: зростання, %, впорядковане за зростанням ---
growth = (sales_2025 / sales_2024 - 1) * 100
growth_order = np.argsort(growth)          # barh: найбільше значення - вгорі
values = growth[growth_order]
colors = np.where(values >= 0, "tab:green", "tab:red")

bars = ax_growth.barh(cities[growth_order], values, color=colors, height=0.6)
ax_growth.bar_label(bars, labels=[f"{v:+.1f}%" for v in values], padding=3)
ax_growth.axvline(0, color="black", linewidth=1)

ax_growth.set_xlim(values.min() * 3, values.max() * 1.25)
ax_growth.set_xticks([])
ax_growth.tick_params(axis="y", length=0, labelsize=11)
ax_growth.spines[:].set_visible(False)
ax_growth.set_title("Growth 2025 vs 2024")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_1.png", dpi=100)
plt.show()
