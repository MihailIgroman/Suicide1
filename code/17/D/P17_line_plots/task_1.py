import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

n = np.arange(1, 31)

# складність алгоритмів: кількість операцій для розміру задачі n
complexities = {
    "O(n)": n,
    "O(n log n)": n * np.log2(n),
    "O(n^2)": n ** 2,
    "O(2^n)": 2.0 ** n,
}

fig, (ax_lin, ax_log) = plt.subplots(1, 2, figsize=(10, 4))

for name, ops in complexities.items():
    ax_lin.plot(n, ops, label=name)
    ax_log.plot(n, ops)

ax_lin.set_ylim(0, 1000)
ax_lin.set_title("Linear scale")

# на логарифмічній шкалі 2^n - пряма: log(2^n) = n * log(2)
ax_log.set_yscale("log")
ax_log.set_title("Log scale")

for ax in (ax_lin, ax_log):
    ax.set_xlim(1, 30)
    ax.set_xlabel("n")
    ax.set_ylabel("Operations")
    ax.grid(True, alpha=0.3)

# одна легенда на всю фігуру, над графіками
fig.legend(loc="upper center", ncol=4, frameon=False)
fig.text(0.01, 0.02, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 0.94))

fig.savefig("task_1.png", dpi=100)
plt.show()
