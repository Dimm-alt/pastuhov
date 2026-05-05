
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# Настройки
API_URL = "https://api.frankfurter.app/latest?from="
HISTORY_FILE = "history.json"

# Загрузка истории (максимум 10 записей)
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)[-10:]
    return []

# Сохранение истории
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-10:], f, indent=2, ensure_ascii=False)

# Получение курса
def get_rate(from_curr, to_curr):
    try:
        response = requests.get(API_URL + from_curr, timeout=5)
        data = response.json()
        return data["rates"].get(to_curr)
    except:
        messagebox.showerror("Ошибка", "Не удалось получить курс")
        return None

# Конвертация и обновление интерфейса
def convert():
    try:
        amount = float(entry_amount.get())
        if amount <= 0:
            messagebox.showwarning("Ошибка", "Сумма должна быть > 0")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Введите корректное число")
        return

    from_curr = combo_from.get()
    to_curr = combo_to.get()

    if from_curr == to_curr:
        result = amount
    else:
        rate = get_rate(from_curr, to_curr)
        if rate is None:
            return
        result = amount * rate

    # Обновление результата
    result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")


    # Добавление в историю
    history.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "amount": f"{amount:.2f}",
        "from": from_curr,
        "to": to_curr,
        "result": f"{result:.2f}"
    })
    save_history(history)
    update_table()

# Обновление таблицы истории
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for record in history[-10:]:
        tree.insert("", "end", values=(
            record["timestamp"], record["amount"],
            record["from"], record["to"], record["result"]
        ))

# Инициализация GUI
root = tk.Tk()
root.title("Конвертер валют")
root.geometry("650x400")

history = load_history()
currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]  # Базовый набор валют

# Ввод данных
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Сумма:").grid(row=0, column=0, padx=5)
entry_amount = tk.Entry(frame_input, width=12)
entry_amount.grid(row=0, column=1, padx=5)


tk.Label(frame_input, text="Из:").grid(row=0, column=2, padx=5)
combo_from = ttk.Combobox(frame_input, values=currencies, width=8)
combo_from.set("USD")
combo_from.grid(row=0, column=3, padx=5)

tk.Label(frame_input, text="В:").grid(row=0, column=4, padx=5)
combo_to = ttk.Combobox(frame_input, values=currencies, width=8)
combo_to.set("EUR")
combo_to.grid(row=0, column=5, padx=5)

tk.Button(frame_input, text="Конвертировать", command=convert).grid(row=0, column=6, padx=10)

# Результат
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"), fg="darkblue")
result_label.pack(pady=10)


# Таблица истории
frame_history = tk.Frame(root)
frame_history.pack(pady=10, fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame_history, columns=("time", "amount", "from", "to", "result"),
               show="headings", height=8)
tree.heading("time", text="Время")
tree.heading("amount", text="Сумма")
tree.heading("from", text="Из")
tree.heading("to", text="В")
tree.heading("result", text="Результат")
tree.column("time", width=80)
tree.column("amount", width=80)
tree.column("from", width=60)
tree.column("to", width=60)
tree.column("result", width=90)
tree.pack(fill=tk.BOTH, expand=True)

update_table()  # Инициализация таблицы

root.mainloop()
