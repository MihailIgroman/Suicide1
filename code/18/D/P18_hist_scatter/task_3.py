import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(42)
# кількість переглядів відео
views = rng.lognormal(mean=8, sigma=1.8, size=3000)

fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(11, 4))

ax_lin.hist(views, bins=50, color="tab:blue", edgecolor="white")
ax_lin.set_title("Linear bins")
ax_lin.set_xlabel("Views")
ax_lin.set_ylabel("Videos")

# 42 логарифмічні інтервали: 43 межі від 10^0 до 10^7
log_bins = np.logspace(0, 7, 43)
ax_log.hist(views, bins=log_bins, color="tab:blue", edgecolor="white")
ax_log.set_xscale("log")

median = np.median(views)
mean = views.mean()
ax_log.axvline(median, color="tab:red", linestyle="--", label=f"median {median:,.0f}")
ax_log.axvline(mean, color="black", linestyle=":", label=f"mean {mean:,.0f}")
ax_log.set_title("Log bins")
ax_log.set_xlabel("Views")
ax_log.legend(loc="upper left")

for ax in (ax_lin, ax_log):
    ax.spines[["top", "right"]].set_visible(False)

fig.suptitle(f"Video views (n={views.size})")
fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_3.png", dpi=100)
plt.show()
