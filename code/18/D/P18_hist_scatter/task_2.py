import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(41)
# час відповіді сервера, ms
before = rng.gamma(3, 40, size=1200)
after = rng.gamma(3, 25, size=400)

samples = {"before": (before, "tab:blue"), "after": (after, "tab:orange")}

fig, (ax_hist, ax_cdf) = plt.subplots(1, 2, figsize=(11, 4))

# ліворуч: інтервали по 20 ms; ваги 1/n, щоб набори різного розміру
# можна було порівнювати
bins_20 = np.arange(0, 501, 20)
for name, (data, color) in samples.items():
    ax_hist.hist(data, bins=bins_20, weights=np.full(data.size, 1 / data.size),
                 color=color, alpha=0.5, label=f"{name} (n={data.size})")

ax_hist.set_xlim(0, 500)
ax_hist.yaxis.set_major_formatter(PercentFormatter(xmax=1))
ax_hist.set_title("Response time")
ax_hist.set_xlabel("Response time, ms")
ax_hist.set_ylabel("Share of requests")
ax_hist.legend()

# праворуч: накопичена частка з кроком 1 ms і 95-й перцентиль;
# спільні інтервали до максимуму обох наборів, щоб лінія не обривалась
bins_1 = np.arange(0, max(before.max(), after.max()) + 2, 1)
for name, (data, color) in samples.items():
    p95 = np.percentile(data, 95)
    ax_cdf.hist(data, bins=bins_1, weights=np.full(data.size, 1 / data.size),
                cumulative=True, histtype="step", linewidth=2, color=color,
                label=f"{name}: p95 = {p95:.0f} ms")
    ax_cdf.axvline(p95, color=color, linestyle=":", linewidth=1)

ax_cdf.axhline(0.95, color="gray", linestyle="--", linewidth=1)
ax_cdf.set_xlim(0, 500)
ax_cdf.set_ylim(0, 1.03)
ax_cdf.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
ax_cdf.set_title("Cumulative distribution")
ax_cdf.set_xlabel("Response time, ms")
ax_cdf.set_ylabel("Share of requests")
ax_cdf.grid(True, alpha=0.3)
ax_cdf.legend(loc="lower right")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_2.png", dpi=100)
plt.show()
