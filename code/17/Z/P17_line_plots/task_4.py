import matplotlib.pyplot as plt

STUDENT_NAME = "Andrii Zelyuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група

cities = {
    "Kyiv": [-3.5, -2.4, 2.1, 9.4, 15.6, 19.0, 20.8, 20.0, 14.8, 8.6, 2.7, -1.6],
    "Lviv": [-2.9, -1.8, 2.3, 8.3, 13.6, 16.6, 18.2, 17.6, 13.2, 8.3, 3.3, -1.1],
    "Odesa": [-0.9, -0.3, 3.4, 9.3, 15.5, 20.0, 22.8, 22.4, 17.3, 11.5, 5.9, 1.3],
    "Kharkiv": [-5.5, -4.9, 0.1, 8.4, 15.2, 18.8, 20.9, 20.0, 14.1, 7.6, 1.2, -3.1],
    "Dnipro": [-3.9, -3.2, 1.8, 10.1, 16.5, 20.2, 22.5, 21.8, 16.0, 9.0, 2.5, -1.8],
    "Uzhhorod": [-1.9, 0.1, 5.2, 11.2, 16.1, 19.4, 21.1, 20.6, 15.8, 10.2, 4.5, -0.3],
}
months = list(range(1, 13))
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

JULY = 6   # індекс липня
# порядок у легенді = порядок ліній у липні, від найтеплішого
by_july = sorted(cities, key=lambda name: cities[name][JULY], reverse=True)

fig, (ax_all, ax_three) = plt.subplots(2, 1, figsize=(9, 8))

for name in by_july:
    ax_all.plot(months, cities[name], label=name)

ax_all.set_title("Six cities")
ax_all.legend(title="City", loc="upper left", bbox_to_anchor=(1.02, 1))

# три міста з підписами біля кінців ліній замість легенди
three = ["Odesa", "Kyiv", "Lviv"]
# зсув підписів по y, щоб вони не налізали один на одного
nudge = {"Odesa": 0.0, "Kyiv": -0.8, "Lviv": 0.8}

for name in three:
    line, = ax_three.plot(months, cities[name])
    ax_three.annotate(name, xy=(months[-1], cities[name][-1] + nudge[name]),
                      xytext=(6, 0), textcoords="offset points",
                      color=line.get_color(), va="center")

# найвища температура серед трьох міст - знаходимо в коді
hottest = max(three, key=lambda name: max(cities[name]))
peak = max(cities[hottest])
peak_month = months[cities[hottest].index(peak)]
ax_three.annotate(f"max {peak} C", xy=(peak_month, peak),
                  xytext=(peak_month + 2, peak + 1.2),
                  arrowprops={"arrowstyle": "->", "color": "black"})

ax_three.set_ylim(-5, 27)
ax_three.set_title("Three cities")
ax_three.spines[["top", "right"]].set_visible(False)

for ax in (ax_all, ax_three):
    ax.set_xticks(months)
    ax.set_xticklabels(month_names)
    ax.set_ylabel("Temperature, C")
    ax.grid(True, alpha=0.3)

fig.text(0.01, 0.01, f"{STUDENT_NAME}, {STUDENT_GROUP}", fontsize=8, color="gray")
fig.tight_layout()

fig.savefig("task_4.png", dpi=100)
plt.show()
