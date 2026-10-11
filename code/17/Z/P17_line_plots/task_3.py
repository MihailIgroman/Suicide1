import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

# місяць, з якого діє тариф, і ціна за kWh
tariff_months = [1, 5, 10, 12]
tariff_prices = [2.64, 4.32, 4.80, 4.80]

months = np.arange(1, 13)
usage = np.array([285, 262, 231, 198, 160, 131, 118, 126, 158, 205, 247, 279])
norm = 200

fig, (ax_tariff, ax_usage) = plt.subplots(
    2, 1, figsize=(8, 6), sharex=True, gridspec_kw={"height_ratios": [1, 2]}
)

# ступінчастий графік: ціна діє з місяця зміни до наступної зміни
ax_tariff.step(tariff_months, tariff_prices, where="post", color="black")
ax_tariff.plot(tariff_months, tariff_prices, "o", color="black")
ax_tariff.set_ylim(2, 5.5)
ax_tariff.yaxis.set_major_formatter(StrMethodFormatter("{x:.2f} UAH"))
ax_tariff.set_title("Electricity tariff, per kWh")
ax_tariff.grid(True, alpha=0.3)

ax_usage.plot(months, usage, "-o", color="black", label="usage")
ax_usage.axhline(norm, color="gray", linestyle="--", label="norm")
# interpolate=True домальовує заливку до точки перетину з нормою
ax_usage.fill_between(months, usage, norm, where=usage > norm, interpolate=True,
                      color="tab:red", alpha=0.3, label="over norm")
ax_usage.fill_between(months, usage, norm, where=usage < norm, interpolate=True,
                      color="tab:green", alpha=0.3, label="under norm")
ax_usage.set_ylim(100, 320)
ax_usage.set_xticks(months)
ax_usage.set_xlabel("Month")
ax_usage.set_ylabel("Usage, kWh")
ax_usage.set_title("Monthly usage")
ax_usage.grid(True, alpha=0.3)
ax_usage.legend(loc="upper center", ncol=4, frameon=False)

fig.text(0.01, 0.015, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout()

fig.savefig("task_3.png", dpi=100)
plt.show()
