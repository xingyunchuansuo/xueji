import tkinter as tk
from tkinter import messagebox
import json
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

def login():
    username = entry_username.get()
    password = entry_password.get()

    if not username.strip():
        messagebox.showwarning("提示", "请输入账号")
        return
    if not password.strip():
        messagebox.showwarning("提示", "请输入密码")
        return

    found = False
    for user in users:
        if username == user['username']:
            found = True
            if password == user['password']:
                messagebox.showinfo("欢迎回来", f"欢迎回来，{username}")
            else:
                messagebox.showwarning("密码错误", "请重新输入密码")
            break

    if not found:
        new_user = {"username": username, "password": password}
        users.append(new_user)
        save_users(users) 
        messagebox.showinfo("欢迎", f"已为你创建新账号：{username}")

    print(f"用户 {username} 登录成功")


root = tk.Tk()
root.title("学迹 - 登录")
root.geometry("400x350")

tk.Label(root, text="学迹 - 智能学习助手", font=("微软雅黑", 16)).pack(pady=20)
tk.Label(root, text="请输入你的账号：", font=("微软雅黑", 10)).pack(pady=5)

entry_username = tk.Entry(root, width=30)
entry_username.pack(pady=5)

tk.Label(root, text="请输入你的密码：", font=("微软雅黑", 10)).pack(pady=5)

entry_password = tk.Entry(root, width=30, show="*")
entry_password.pack(pady=5)

tk.Button(root, text="登录", command=login, width=15).pack(pady=20)

root.mainloop()