import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, PercentFormatter

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(40)
scores = np.clip(rng.normal(68, 14, size=500).round(), 0, 100)
pass_score = 60

bins = np.arange(0, 101, 5)                      # інтервали по 5 балів
total = scores.size
failed = scores[scores < pass_score]
passed = scores[scores >= pass_score]

# вага кожного студента 1/total: висота стовпчика - частка від УСІХ студентів
fig, ax = plt.subplots(figsize=(9, 4))
ax.hist(failed, bins=bins, weights=np.full(failed.size, 1 / total),
        color="tab:red", edgecolor="white",
        label=f"failed ({failed.size / total:.0%})")
ax.hist(passed, bins=bins, weights=np.full(passed.size, 1 / total),
        color="tab:blue", edgecolor="white",
        label=f"passed ({passed.size / total:.0%})")

median = np.median(scores)
ax.axvline(median, color="black", linestyle="--", label=f"median {median:.0f}")

ax.set_xlim(0, 100)
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
ax.set_title(f"Exam scores (n={total})")
ax.set_xlabel("Score")
ax.set_ylabel("Share of students")
ax.grid(axis="y", alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left")

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_1.png", dpi=100)
plt.show()
