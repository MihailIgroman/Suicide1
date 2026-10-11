import matplotlib.pyplot as plt
import numpy as np

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група
N = 11   # номер у списку групи + 5

rng = np.random.default_rng(N)   # генератор створюється один раз

AUTHOR = f"{STUDENT_NAME}, {STUDENT_GROUP}"

# --- Завдання 1. Лінійний графік ---
x = np.linspace(-10, 10, 100)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, x ** 2, label="x^2")
ax.plot(x, N * x, linestyle="--", label="N*x")
ax.set_title(AUTHOR)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
ax.grid(True)
fig.savefig("task_1.png", dpi=150)

# --- Завдання 2. Температура ---
# середня температура за місяцями (придумані дані для міста Kovel)
city = "Kovel"
temps = np.array([-4.1, -3.0, 1.5, 8.2, 14.1, 17.3, 19.0, 18.2, 13.1, 7.6, 2.4, -1.9])
months = np.arange(1, 13)
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
year_mean = temps.mean()

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(months, temps, marker="o", label="monthly mean")
ax.axhline(year_mean, linestyle="--", color="gray", label=f"year mean {year_mean:.1f} C")
ax.set_xticks(months)
ax.set_xticklabels(month_names)
ax.set_title(f"Average temperature, {city}")
ax.set_xlabel("Month")
ax.set_ylabel("Temperature, C")
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig("task_2.png", dpi=150)

# --- Завдання 3. Стовпчикова діаграма ---
activities = ["sleep", "study", "gym", "series", "cooking", "walks", "music"]
hours = np.array([54, 25, 7, 9, 5, 6, 11])

# barh малює перший елемент унизу, тому сортуємо за зростанням:
# найбільше значення опиниться вгорі
order = np.argsort(hours)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(np.array(activities)[order], hours[order], color="tab:blue")
ax.bar_label(bars, padding=3)
ax.set_title("Hours per week")
ax.set_xlabel("Hours")
ax.set_ylabel("Activity")
ax.set_xlim(0, hours.max() * 1.15)
fig.savefig("task_3.png", dpi=150)

# --- Завдання 4. Гістограма ---
heights = rng.normal(170 + N, 8, size=1000)
mean_height = heights.mean()
median_height = np.median(heights)

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(heights, bins=25, color="tab:blue", edgecolor="white")
ax.axvline(mean_height, color="tab:red", linewidth=2, label=f"mean {mean_height:.1f}")
ax.axvline(median_height, color="tab:orange", linestyle="--", linewidth=2,
           label=f"median {median_height:.1f}")
ax.set_title(f"Height distribution, n={heights.size}")
ax.set_xlabel("Height, cm")
ax.set_ylabel("Count")
ax.legend()
fig.savefig("task_4.png", dpi=150)

# --- Завдання 5. Scatter ---
x_points = rng.uniform(0, 10, 50)
y_points = N + 3 * x_points + rng.normal(0, 4, 50)
above = y_points > y_points.mean()       # булева маска

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x_points[above], y_points[above], color="tab:green", marker="^",
           label="above mean y")
ax.scatter(x_points[~above], y_points[~above], color="tab:purple", marker="o",
           label="below or equal mean y")
ax.axhline(y_points.mean(), color="gray", linestyle=":", linewidth=1)
ax.set_title("Scatter: y = N + 3x + noise")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig("task_5.png", dpi=150)

r = np.corrcoef(x_points, y_points)[0, 1]
print(f"Correlation x-y: {r:.2f}")

plt.show()
