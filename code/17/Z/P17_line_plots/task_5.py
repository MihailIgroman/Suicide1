import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, PercentFormatter

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

weeks = np.arange(1, 27)
conversion = np.array([2.1, 2.3, 2.2, 2.4, 2.3, 2.6, 2.5, 2.7, 2.6, 2.8, 2.9, 2.7, 3.0,
                       3.1, 2.9, 3.2, 4.4, 3.3, 3.2, 3.4, 3.5, 3.3, 3.6, 3.7, 3.5, 3.8]) / 100
release_week = 12

plt.style.use("ggplot")

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(weeks, conversion, "-o", markersize=4)

ax.axvline(release_week, color="black", linestyle=":", linewidth=1.5)
ax.text(release_week + 0.3, 0.04, "new design")

# пік акції - тиждень з максимальною конверсією
promo = conversion.argmax()
ax.annotate("promo", xy=(weeks[promo], conversion[promo]),
            xytext=(weeks[promo] + 2, conversion[promo]), va="center",
            arrowprops={"arrowstyle": "->", "color": "0.3"})

ax.set_ylim(0.015, 0.05)
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.set_title("Weekly conversion rate")
ax.set_xlabel("Week")
ax.set_ylabel("Conversion")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_5.png", dpi=100)
plt.show()
