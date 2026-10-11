import numpy as np

STUDENT_NAME = "Andrii Zeliuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група
N = 11   # номер у списку групи + 5

print(f"{STUDENT_NAME}, {STUDENT_GROUP}, N = {N}")

# --- Завдання 1. Індексація одновимірного масиву ---
print("--- Task 1 ---")
data = np.arange(10, 10 + N)
print(data)
print(data[0], data[-1], data[-3], data[N // 2])
data[0] = 0
print(data)

# --- Завдання 2. Зрізи ---
print("--- Task 2 ---")
print(data[:3])     # перші три
print(data[-3:])    # останні три
print(data[::2])    # кожен другий
print(data[::-1])   # у зворотному порядку
print(data[1:-1])   # без першого й останнього

# --- Завдання 3. Перегляд і копія ---
print("--- Task 3 ---")
view = data[:3]
copy = data[:3].copy()
view[0] = -100
print("data:", data)
print("view:", view)
print("copy:", copy)
print(view.base is data, copy.base is None)
# data змінився, бо зріз view - це перегляд тих самих даних у пам'яті,
# а copy() створив окремий масив із власними даними.

# --- Завдання 4. Матриця: індексація та зрізи ---
print("--- Task 4 ---")
table = np.arange(1, 21).reshape(4, 5)
print(table)
print(table[2, 3])       # один індекс через кому
print(table[1])          # другий рядок (індекс 1)
print(table[:, 2])       # третій стовпець (індекс 2)
print(table[1:3, 2:5])   # рядки 1-2, стовпці 2-4
print(table[-1, ::-1])   # останній рядок задом наперед

# --- Завдання 5. Запис через зріз: рамка ---
print("--- Task 5 ---")
frame = np.zeros((5, 5), dtype=int)
frame[0] = 1        # перший рядок
frame[-1] = 1       # останній рядок
frame[:, 0] = 1     # перший стовпець
frame[:, -1] = 1    # останній стовпець
frame[2, 2] = N     # центр
print(frame)

# --- Завдання 6. Булева маска ---
print("--- Task 6 ---")
temps = np.array([-6.0, -3.5, 2.0, 9.5, 15.5, 19.0, 22.5, 21.5, 15.0, 8.5, 2.5, -2.5])
mask = temps > N
print(mask)
print(temps[mask])
print(mask.sum())
print(temps[mask].mean())
print(np.where(mask)[0])

# --- Завдання 7. Комбіновані умови та np.where ---
print("--- Task 7 ---")
in_range = (temps >= N) & (temps <= 2 * N)
print(temps[in_range])
print(temps[~in_range])
labels = np.where(temps > N, "warm", "cold")
print(labels)
no_negative = np.where(temps < 0, 0.0, temps)
print(no_negative)
