import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

rng = np.random.default_rng(45)
# лабораторна робота: розтягнення пружини під вагою вантажів
mass = np.arange(50, 551, 50) / 1000            # маса вантажу, кг
g = 9.81
force = mass * g                                 # сила, Н
k_true = 24.0                                    # жорсткість пружини, Н/м
x = force / k_true * 100 + rng.normal(0, 0.25, size=mass.size)   # видовження, см
x[-1] += 2.4     # останній вантаж: пружина вийшла за межу пружності
x_err = 0.3      # похибка лінійки, см

MAIN = "#0072B2"
EXCLUDED = "#D55E00"

# найменші квадрати за всіма точками, крім останньої: F = slope * x + intercept
fit_x, fit_f = x[:-1], force[:-1]
slope, intercept = np.polyfit(fit_x, fit_f, 1)
k = slope * 100                                  # Н/см -> Н/м
residuals = force - (slope * x + intercept)

fig, (ax, ax_res) = plt.subplots(
    2, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
)

ax.axline((0, intercept), slope=slope, color=MAIN, linewidth=1.2,
          label=rf"$F = k\,x$,  $k = {k:.1f}$ N/m")
ax.errorbar(fit_x, fit_f, xerr=x_err, fmt="o", color=MAIN, ecolor="0.5", capsize=3,
            label="measurements")
ax.errorbar(x[-1], force[-1], xerr=x_err, fmt="o", color=EXCLUDED, ecolor="0.5",
            capsize=3, markerfacecolor="white", label="excluded from fit")
ax.annotate("elastic limit\nexceeded", xy=(x[-1], force[-1]),
            xytext=(x[-1] - 2, force[-1] - 1.2), color=EXCLUDED, fontsize=9,
            arrowprops={"arrowstyle": "->", "color": EXCLUDED,
                        "connectionstyle": "arc3,rad=0.2"})

ax.set_xlim(0, 27)
ax.set_ylim(0, 6)
ax.set_ylabel("Force $F = mg$, N")
ax.legend(loc="upper left", frameon=False)
ax.set_title(r"Hooke's law: spring constant from $F(x)$", loc="left", fontweight="bold")

# залишки: виміряна сила мінус значення на прямій
ax_res.axhline(0, color="0.3", linewidth=1)
ax_res.vlines(x, 0, residuals, color="0.5", linewidth=1.5)
ax_res.plot(x[:-1], residuals[:-1], "o", color=MAIN, markersize=5)
ax_res.plot(x[-1], residuals[-1], "o", color=EXCLUDED, markerfacecolor="white", markersize=5)
ax_res.set_ylabel(r"$\Delta F$, N")
ax_res.set_xlabel("Extension $x$, cm")

# поділки: основні 5 см і 1 Н, допоміжні 1 см і 0.25 Н; сітка для обох
ax_res.xaxis.set_major_locator(MultipleLocator(5))
ax_res.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(0.25))
for axis in (ax, ax_res):
    axis.grid(which="major", color="0.8")
    axis.grid(which="minor", color="0.93")

fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_5.png", dpi=100)
plt.show()
