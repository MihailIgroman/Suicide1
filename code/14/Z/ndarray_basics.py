import numpy as np

STUDENT_NAME = "Andrii Zeliuk"   # ім'я та прізвище транслітерацією
STUDENT_GROUP = "IT-41"   # група
N = 11   # номер у списку групи + 5

print(f"{STUDENT_NAME}, {STUDENT_GROUP}, N = {N}")

# --- Завдання 1. Перший масив ---
print("--- Task 1 ---")
a = np.arange(1, N + 1)
print(a)
print("shape:", a.shape)
print("size: ", a.size)
print("dtype:", a.dtype)

# --- Завдання 2. Масиви-заготовки ---
print("--- Task 2 ---")
print(np.zeros((3, 4)))
print(np.ones((2, N), dtype=int))
print(np.full((2, 2), N))
print(np.eye(N))

# --- Завдання 3. Послідовності ---
print("--- Task 3 ---")
print(np.linspace(0, 1, N))
print(np.arange(0, 21, 2))

# --- Завдання 4. Форма ---
print("--- Task 4 ---")
numbers = np.arange(1, 13)
print(numbers)

matrix = numbers.reshape(3, 4)
print(matrix)
print(matrix.shape)

table_4x3 = numbers.reshape(4, 3)
print(table_4x3)
print(table_4x3.shape)

# -1: NumPy сам обчислює кількість стовпців (12 / 2 = 6)
table_2 = numbers.reshape(2, -1)
print(table_2)
print(table_2.shape)

# --- Завдання 5. Арифметика (поелементно, без циклів) ---
print("--- Task 5 ---")
print(a * 2)
print(a + 10)
print(a ** 2)
print(a / N)  # ділення "/" завжди дає float64
print((a ** 2).sum())

# --- Завдання 6. Температура за тиждень ---
print("--- Task 6 ---")
temps = np.array([10.5, 12.0, 9.5, 13.0, 15.5, 11.5, 8.0])
print(temps.min())
print(temps.max())
print(temps.mean())
print(temps.argmax())  # індекс (номер) найтеплішого дня, нумерація з 0
warm = temps > N
print(warm)
print(warm.sum())  # True рахується як 1
print(temps * 9 / 5 + 32)

# --- Завдання 7. Осі ---
print("--- Task 7 ---")
print(matrix.sum())
print(matrix.sum(axis=0))  # по стовпцях: рядки "згортаються"
print(matrix.sum(axis=1))  # по рядках: стовпці "згортаються"
