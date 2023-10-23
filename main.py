import pandas as pd
import tkinter as tk

# Чтение данных из файла Excel и создание исходного DataFrame
data = pd.read_excel(r'C:\Users\USER\Desktop\код\data.xlsx')
df = pd.DataFrame(data)

# Создание копии DataFrame для обезличивания
depersonalized_df = df.copy()

# Функция для вычисления K-анонимности
def calculate_k_anonymity(quasiidentifiers, k_value):
    left = 1
    right = k_value
    best_k = None

    while left <= right:
        mid = (left + right) // 2
        is_k_anonymous = is_k_anonymous_for_k(depersonalized_df, quasiidentifiers, mid)

        if is_k_anonymous:
            best_k = mid
            left = mid + 1
        else:
            right = mid - 1

    return best_k

# Функция для проверки K-анонимности при заданном K
def is_k_anonymous_for_k(data, quasiidentifiers, k):
    grouped_data = data.groupby(quasiidentifiers).size().reset_index(name='count')
    return all(group['count'] >= k for _, group in grouped_data.iterrows())

# Функция для вывода 5 плохих значений k 
def get_bad_value(data, quasiidentifiers):
    grouped_data = data.groupby(quasiidentifiers).size().reset_index(name='count')
    grouped_data = grouped_data.sort_values(by = 'count')
    return grouped_data['count'][1:6]

# Функция для обфускации электронной почты (оставляем только домен)
def obfuscate_email(email):
    parts = email.split('@')
    if len(parts) == 2:
        return parts[1] 
    else:
        return email  

# Функция для получения времени года на основе месяца
def get_season(date):
    if date.month in [12, 1, 2]:
        return 'Зима'
    elif date.month in [3, 4, 5]:
        return 'Весна'
    elif date.month in [6, 7, 8]:
        return 'Лето'
    else:
        return 'Осень'

# Функция для обезличивания датасета
def anonymize_dataset(selected_quasiidentifiers):
    del depersonalized_df['IP']
    if 'Дата просмотра' in selected_quasiidentifiers:
        depersonalized_df['Дата просмотра'] = pd.to_datetime(df['Дата просмотра'])
        depersonalized_df['Дата просмотра'] = df['Дата просмотра'].apply(get_season)
    if 'Пользователь' in selected_quasiidentifiers:
        depersonalized_df['Пользователь'] = df['Пользователь'].apply(obfuscate_email)
    depersonalized_df.to_excel('depersonalized_data.xlsx', index=False)

# Функция для обработки изменения режима (вычисление K-анонимности или обезличивание)
def start_processing():
    selected_quasiidentifiers = [quasiidentifiers[i] for i in range(len(quasiidentifiers)) if quasiidentifier_vars[i].get()]
    selected_mode = mode_var.get()
    if selected_mode == "Calculate K-Anonymity":
        k_anonymity = calculate_k_anonymity(selected_quasiidentifiers, 10000) 
        # result_label = tk.Label(root, text=f"K-Anonymity: {k_anonymity}")
        print(k_anonymity)
        # result_label.grid(row=4, column=0, columnspan=2)
        bad_values = get_bad_value(depersonalized_df, selected_quasiidentifiers)
        result_label = tk.Label(root, text=f"K-Anonymity: {k_anonymity}\n 5 Плохих Значений Анонимности:\n{bad_values.to_string(index=False)}")
        result_label.grid(row=4, column=0, columnspan=2)
    else:
        anonymize_dataset(selected_quasiidentifiers)
        

# Создание главного окна tkinter
root = tk.Tk()
root.title("K-Anonymity App")

# Фрейм для выбора режима
mode_frame = tk.LabelFrame(root, text="Choose Mode")
mode_frame.grid(row=0, column=0, padx=10, pady=10)

# Переменная для выбора режима
mode_var = tk.StringVar()
mode_var.set("Calculate K-Anonymity")

# Радиокнопки для выбора режима
calculate_k_anon_radio = tk.Radiobutton(mode_frame, text="Calculate K-Anonymity", variable=mode_var, value="Calculate K-Anonymity")
anonymize_radio = tk.Radiobutton(mode_frame, text="Anonymize Dataset", variable=mode_var, value="Anonymize Dataset")

calculate_k_anon_radio.grid(row=0, column=0)
anonymize_radio.grid(row=0, column=1)

# Элементы для вычисления K-анонимности
k_anon_label = tk.Label(root, text="K-Anonymity Value:")
k_anon_entry = tk.Entry(root)

# Элементы для выбора квазидентификаторов
anonymize_label = tk.Label(root, text="Select Quasiidentifiers:")

quasiidentifiers = ["Пользователь", "Дата просмотра"]
quasiidentifier_checkboxes = []

quasiidentifier_vars = [tk.IntVar() for _ in range(len(quasiidentifiers))]

# Флажки для выбора квазидентификаторов
for i, quasiidentifier in enumerate(quasiidentifiers):
    checkbox = tk.Checkbutton(root, text=quasiidentifier, variable=quasiidentifier_vars[i])
    checkbox.grid(row=2 + i, column=1)
    quasiidentifier_checkboxes.append(checkbox)

# Кнопка для запуска обработки
process_button = tk.Button(root, text="Start Processing", command=start_processing)

# Выбор режима "Calculate K-Anonymity" по умолчанию
calculate_k_anon_radio.invoke()

# Размещение кнопки
process_button.grid(row=4, column=0, columnspan=2)

# Запуск главного цикла tkinter
root.mainloop()