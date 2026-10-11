import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

x = np.linspace(0, 4, 50)

# графік для чорно-білого друку: лінії розрізняються стилем, маркером
# і відтінком сірого, а не кольором
lines = [
    ("sqrt(x)", np.sqrt(x), "black", "-", "o"),
    ("x / 2", x / 2, "0.35", "--", "s"),
    ("x^2 / 8", x ** 2 / 8, "0.6", ":", "^"),
]

fig, ax = plt.subplots(figsize=(7, 4))
for label, y, color, style, marker in lines:
    # маркер на кожній 7-й точці, щоб не захаращувати лінію
    ax.plot(x, y, color=color, linestyle=style, marker=marker,
            markevery=(7, 7), label=label)

ax.set_xlim(0, 4)
ax.set_ylim(0, 2.05)
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.2f}"))
ax.set_title("Print-friendly lines")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", frameon=False)

fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_6.png", dpi=100)
plt.show()
