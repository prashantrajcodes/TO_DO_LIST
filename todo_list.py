import json
import os
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# Setup root 
try:
    from ttkthemes import ThemedTk
    root = ThemedTk(theme="arc")
except Exception:
    root = tk.Tk()

root.title("To-Do List")
root.geometry("490x450")
root.resizable(True, True)

FILE = "todo_list.json"

# Data helpers 
def load_tasks():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [{"text": str(d.get("text", "")), "done": bool(d.get("done", False))}
                    for d in data if isinstance(d, dict)]
    except Exception:
        return []

def save_tasks(tasks):
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Save error", str(e))

tasks = load_tasks()   # list of dicts

# UI building 
top = ttk.Frame(root, padding=12)
top.pack(fill="x")

entry = ttk.Entry(top)
entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

def add_task(event=None):
    txt = entry.get().strip()
    if not txt:
        messagebox.showwarning("Empty", "Enter a task")
        return
    tasks.append({"text": txt, "done": False})
    entry.delete(0, "end")
    refresh()
    save_tasks(tasks)

add_btn = ttk.Button(top, text="Add Task", command=add_task)
add_btn.pack(side="right")
entry.bind("<Return>", add_task)

mid = ttk.Frame(root, padding=(12, 0))
mid.pack(fill="both", expand=True)

listbox = tk.Listbox(mid, font=(None, 12), activestyle="none", selectmode=tk.SINGLE)
listbox.pack(side="left", fill="both", expand=True)

scroll = ttk.Scrollbar(mid, orient="vertical", command=listbox.yview)
scroll.pack(side="right", fill="y")
listbox.config(yscrollcommand=scroll.set)

# Features logic functions
def refresh():
    listbox.delete(0, "end")
    for t in tasks:
        mark = "✔ " if t.get("done") else "◻ "
        listbox.insert("end", mark + t.get("text", ""))

def selected_index():
    sel = listbox.curselection()
    return sel[0] if sel else None

def toggle_done(event=None):
    i = selected_index()
    if i is None:
        messagebox.showinfo("Select", "Select a task")
        return
    tasks[i]["done"] = not tasks[i].get("done", False)
    refresh()
    save_tasks(tasks)

def edit_task():
    i = selected_index()
    if i is None:
        messagebox.showinfo("Select", "Select a task")
        return
    current = tasks[i].get("text", "")
    new = simpledialog.askstring("Edit", "Modify task:", initialvalue=current, parent=root)
    if new is None:  # user cancelled
        return
    new = new.strip()
    if not new:
        messagebox.showwarning("Empty", "Task cannot be empty")
        return
    tasks[i]["text"] = new
    refresh()
    save_tasks(tasks)

def delete_task():
    i = selected_index()
    if i is None:
        messagebox.showinfo("Select", "Select a task")
        return
    if messagebox.askyesno("Delete", "Delete selected task?"):
        tasks.pop(i)
        refresh()
        save_tasks(tasks)

def clear_all():
    if not tasks:
        return
    if messagebox.askyesno("Clear", "Clear all tasks?"):
        tasks.clear()
        refresh()
        save_tasks(tasks)

# Buttons 
bot = ttk.Frame(root, padding=12)
bot.pack(fill="x")

style = ttk.Style()
style.configure("Green.TButton", background="#70e2f3", foreground="#e9482c")
style.map("Green.TButton", background=[("active", "#70e2f3")])

btn = lambda txt, cmd: ttk.Button(bot, text=txt, style="Green.TButton", command=cmd)

btn("Done/Undone", toggle_done).grid(row=0, column=0, sticky="ew", padx=4, pady=2)
btn("Edit",        edit_task).grid(row=0, column=1, sticky="ew", padx=4, pady=2)
btn("Delete",      delete_task).grid(row=0, column=2, sticky="ew", padx=4, pady=2)
btn("Clear All",   clear_all).grid(row=0, column=3, sticky="ew", padx=4, pady=2)

for i in range(4):
    bot.columnconfigure(i, weight=1)
# double click toggles
listbox.bind("<Double-Button-1>", toggle_done)

# right-click menu
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Done", command=toggle_done)
menu.add_command(label="Edit", command=edit_task)
menu.add_command(label="Delete", command=delete_task)

def show_menu(e):
    idx = listbox.nearest(e.y)
    listbox.selection_clear(0, "end")
    listbox.selection_set(idx)
    menu.tk_popup(e.x_root, e.y_root)

listbox.bind("<Button-3>", show_menu)

# initial fill and quit handler
refresh()
def on_close():
    save_tasks(tasks)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    root.mainloop()