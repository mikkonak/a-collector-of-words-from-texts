import os
import threading
import string
import tkinter as tk
from tkinter import filedialog, messagebox
import platform  # Добавлен импорт модуля platform

def read_words_from_file(file_path, words_set):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().split()
        cleaned_words = [word.strip(string.punctuation) for word in words if word.strip(string.punctuation)]
        with words_set_lock:
            words_set.update(cleaned_words)

def process_path(path, words_set):
    if os.path.isfile(path):
        read_words_from_file(path, words_set)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.txt'):
                    read_words_from_file(os.path.join(root, file), words_set)

def start_processing(input_paths, output_folder):
    if not input_paths or not output_folder:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите входные пути и выходную папку.")
        return

    words_set = set()
    global words_set_lock
    words_set_lock = threading.Lock()

    threads = []
    for path in input_paths:
        thread = threading.Thread(target=process_path, args=(path, words_set))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    sorted_words = sorted(words_set)

    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "output.txt")
    with open(output_file, 'w', encoding='utf-8') as file:
        for word in sorted_words:
            file.write(word + '\n')

    if platform.system() == "Windows":
        os.startfile(output_folder)
    elif platform.system() == "Darwin":
        os.system(f"open {output_folder}")
    else:
        os.system(f"xdg-open {output_folder}")
    messagebox.showinfo("Завершено", "Обработка завершена. Результаты сохранены в " + output_file)

def add_input_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
    for path in file_paths:
        if path:
            input_paths.append(path)
            input_paths_listbox.insert(tk.END, path)

def add_input_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        input_paths.append(folder_path)
        input_paths_listbox.insert(tk.END, folder_path)

def set_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        global output_folder
        output_folder = folder
        output_folder_label.config(text="Выходная папка: " + output_folder)

def on_start():
    start_processing(input_paths, output_folder)

# Создаем графический интерфейс
root = tk.Tk()
root.title("Обработка текстовых файлов")

input_paths = []
output_folder = ""

# Элементы интерфейса
input_paths_frame = tk.Frame(root)
input_paths_frame.pack(padx=10, pady=10)

input_paths_label = tk.Label(input_paths_frame, text="Входные пути (файлы и папки):")
input_paths_label.pack(anchor="w")

input_paths_listbox = tk.Listbox(input_paths_frame, height=10, width=50)
input_paths_listbox.pack()

add_input_files_button = tk.Button(input_paths_frame, text="Добавить файлы", command=add_input_files)
add_input_files_button.pack(pady=5)

add_input_folder_button = tk.Button(input_paths_frame, text="Добавить папку", command=add_input_folder)
add_input_folder_button.pack(pady=5)

output_folder_frame = tk.Frame(root)
output_folder_frame.pack(padx=10, pady=10)

output_folder_label = tk.Label(output_folder_frame, text="Выходная папка:")
output_folder_label.pack(anchor="w")

set_output_folder_button = tk.Button(output_folder_frame, text="Выбрать выходную папку", command=set_output_folder)
set_output_folder_button.pack(pady=5)

start_button = tk.Button(root, text="Начать обработку", command=on_start)
start_button.pack(pady=20)

root.mainloop()
