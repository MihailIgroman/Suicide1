import numpy as np

STUDENT_NAME = "Andrii Dzhus"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група
N = 10   # номер у списку групи + 5

# генератор створюється один раз на початку скрипта
rng = np.random.default_rng(N)

print(f"{STUDENT_NAME}, {STUDENT_GROUP}, N = {N}")

# --- Завдання 1. Система рівнянь ---
print("--- Task 1 ---")
A = np.array([
    [2.0, 1.0, -1.0],
    [1.0, 3.0, 2.0],
    [3.0, -1.0, 1.0],
])
b = np.array([N, 2 * N, 10.0])

x = np.linalg.solve(A, b)
print(x)
print(A @ x)                   # перевірка підстановкою
print(np.allclose(A @ x, b))

# --- Завдання 2. Матриці ---
print("--- Task 2 ---")
M = np.array([
    [N, 2.0],
    [1.0, 3.0],
])
print(M * M)
print(M @ M)
# M * M множить елементи поелементно (кожен сам на себе),
# а M @ M - матричний добуток "рядок на стовпець".
print(round(np.linalg.det(M), 2))
M_inv = np.linalg.inv(M)
print(M_inv)
print(np.allclose(M @ M_inv, np.eye(2)))

# --- Завдання 3. Аналіз оцінок ---
print("--- Task 3 ---")
grades = np.array([72, 55, 91, 64, 88, 47, 79, 95, 60, 83])
print("mean:  ", grades.mean())
print("median:", np.median(grades))
print("std:   ", round(grades.std(), 2))
print("min:   ", grades.min())
print("max:   ", grades.max())
print("failed:", (grades < 60).sum())
print("excellent:", grades[grades >= 90])
print("best student:", grades.argmax())

# --- Завдання 4. Кидки кубика ---
print("--- Task 4 ---")
rolls = rng.integers(1, 7, size=1000)
print(rolls[:10])
# bincount рахує від 0, тому відкидаємо нульовий елемент
counts = np.bincount(rolls, minlength=7)[1:]
print(counts)
print("mean:", rolls.mean(), "theory:", 3.5)
print("share of 6:", np.mean(rolls == 6), "theory:", round(1 / 6, 4))

# --- Завдання 5. Два кубики ---
print("--- Task 5 ---")
pairs = rng.integers(1, 7, size=(10_000, 2))
sums = pairs.sum(axis=1)
sum_counts = np.bincount(sums, minlength=13)[2:]   # суми від 2 до 12
print(sum_counts)
print("most frequent sum:", sum_counts.argmax() + 2)  # +2, бо індекс 0 - це сума 2
print("P(sum = 7):", np.mean(sums == 7), "theory:", round(6 / 36, 4))
print("P(sum >= 10):", np.mean(sums >= 10))

# --- Завдання 6. Симуляція оцінок групи ---
print("--- Task 6 ---")
scores = rng.normal(70, 12, size=(N + 20, 3))
scores = np.clip(np.round(scores), 0, 100).astype(int)
print(scores.shape)
print(scores[:3])
print("mean per subject:", np.round(scores.mean(axis=0), 2))

student_avg = scores.mean(axis=1)
best = student_avg.argmax()
print("best student:", best, "avg:", round(student_avg[best], 2))
print("avg < 60:", (student_avg < 60).sum())
