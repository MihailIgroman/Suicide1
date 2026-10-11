import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

# опитування: чому студенти покинули онлайн-курс (одна відповідь на людину)
reasons = [
    "Not enough time because of work or study",
    "Course was too difficult",
    "Lost motivation after the first weeks",
    "Video lectures were too long",
    "Found a better course elsewhere",
    "Technical problems with the platform",
    "Other",
]
counts = np.array([412, 138, 297, 176, 64, 51, 39])

ACCENT = "#D55E00"
GRAY = "0.75"

total = counts.sum()
share = counts / total * 100
# barh малює перший елемент унизу: сортуємо за зростанням, найчастіша - вгорі
order = np.argsort(share)
labels = np.array(reasons)[order]
values = share[order]
top = len(values) - 1

colors = [GRAY] * len(values)
colors[top] = ACCENT

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(labels, values, color=colors, height=0.65)

for index, (bar, value) in enumerate(zip(bars, values)):
    is_top = index == top
    ax.annotate(f"{value:.0f}%", xy=(value, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0), textcoords="offset points", va="center",
                color=ACCENT if is_top else "0.3",
                fontweight="bold" if is_top else "normal")

# частка, яка була б у кожної відповіді за рівномірного розподілу
equal = 100 / len(reasons)
ax.axvline(equal, color="0.3", linestyle=":", linewidth=1)
# x - у даних, y - у частках області графіка: підпис прилип до верху
ax.text(equal, 1.0, f" if all reasons were equal: {equal:.0f}%",
        transform=ax.get_xaxis_transform(), va="top", fontsize=9, color="0.3")

ax.set_xlim(0, values.max() * 1.08)
ax.set_xticks([])
ax.tick_params(axis="y", length=0, labelsize=11)
ax.spines[["top", "right", "bottom"]].set_visible(False)

# заголовок - висновок з найчастішої відповіді
fig.suptitle("Lack of time is the main reason students quit",
             x=0.01, ha="left", fontsize=16, fontweight="bold")
ax.set_title(f"Share of respondents, % (n={total})", loc="left", color="0.4", pad=14)

fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.02, 1, 1))

fig.savefig("task_2.png", dpi=100)
plt.show()
