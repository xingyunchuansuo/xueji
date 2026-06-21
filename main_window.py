import sys
import io
import tkinter as tk
import json
import requests

def open_main_window(username):

    def load_from_file():
        filename = f"students_{username}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_to_file(students_data):
        filename = f"students_{username}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(students_data, f, ensure_ascii=False, indent=2)

    students = load_from_file()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    root = tk.Tk()
    root.title(f"学迹 - {username}")
    root.geometry("500x450")

    def find_student_by_sid(sid):
        for stu in students:
            if stu['sid'] == sid:
                return stu
        return None
    
    #1. 成绩管理功能
    def manage_message():
        manage_win = tk.Toplevel(root)
        manage_win.title("成绩管理")
        manage_win.geometry("400x350")

        def open_add_window():
            add_win = tk.Toplevel(manage_win)
            add_win.title("录入成绩")
            add_win.geometry("300x300")
            tk.Label(add_win, text="学号").pack(pady=5)
            entry_sid = tk.Entry(add_win)
            entry_sid.pack(pady=5)
            tk.Label(add_win, text="姓名（新学号时必填）").pack(pady=5)
            entry_name = tk.Entry(add_win)
            entry_name.pack(pady=5)
            tk.Label(add_win, text="科目").pack(pady=5)
            entry_subject = tk.Entry(add_win)
            entry_subject.pack(pady=5)
            tk.Label(add_win, text="成绩").pack(pady=5)
            entry_score = tk.Entry(add_win)
            entry_score.pack(pady=5)
            def save_student():
                sid = entry_sid.get()
                name = entry_name.get()
                subject = entry_subject.get()
                score = float(entry_score.get())
                stu = find_student_by_sid(sid)
                if stu is None:
                    stu = {"sid": sid, "name": name, "scores": {}}
                    students.append(stu)
                stu['scores'][subject] = score
                if name:
                    stu['name'] = name
                add_win.destroy()
            tk.Button(add_win, text="保存", command=save_student).pack(pady=10)

        def open_view_window():
            view_win = tk.Toplevel(manage_win)
            view_win.title("查看全部成绩")
            view_win.geometry("500x350")
            if not students:
                tk.Label(view_win, text="暂时没有成绩数据", font=("微软雅黑", 12)).pack(pady=50)
            else:
                tk.Label(view_win, text=f"一共{len(students)}名学生", font=("微软雅黑", 12)).pack(pady=10)
                text_area = tk.Text(view_win, width=55, height=14)
                text_area.pack(pady=10)
                for stu in students:
                    for subject, score in stu['scores'].items():
                        line = f"学号：{stu['sid']}  姓名：{stu['name']}  科目：{subject}  成绩：{score}\n"
                        text_area.insert(tk.END, line)
                text_area.config(state="disabled")

        def open_search_window():
            search_win = tk.Toplevel(manage_win)
            search_win.title("按科目查找")
            search_win.geometry("500x350")
            tk.Label(search_win, text="输入要查找的科目:", font=("微软雅黑", 10)).pack(pady=10)
            entry_subject = tk.Entry(search_win, width=30)
            entry_subject.pack(pady=5)
            result_area = tk.Text(search_win, width=55, height=12)
            result_area.pack(pady=10)
            def do_search():
                result_area.config(state="normal")
                result_area.delete(1.0, tk.END)
                subject = entry_subject.get()
                found_list = []
                for stu in students:
                    if subject in stu['scores']:
                        found_list.append((stu, stu['scores'][subject]))
                if found_list:
                    result_area.insert(tk.END, f"科目'{subject}'的成绩：\n")
                    for stu, score in found_list:
                        line = f"学号：{stu['sid']}  姓名：{stu['name']}  成绩：{score}\n"
                        result_area.insert(tk.END, line)
                else:
                    result_area.insert(tk.END, f"未找到科目'{subject}'的成绩记录。")
                result_area.config(state="disabled")
            tk.Button(search_win, text="查找", command=do_search, width=15).pack(pady=10)

        def open_sort_window():
            sort_win = tk.Toplevel(manage_win)
            sort_win.title("成绩排序")
            sort_win.geometry("400x250")
            tk.Label(sort_win, text="输入要排序的科目:", font=("微软雅黑", 10)).pack(pady=10)
            entry_subject = tk.Entry(sort_win, width=30)
            entry_subject.pack(pady=5)
            result_area = tk.Text(sort_win, width=45, height=8)
            result_area.pack(pady=10)
            def do_sort():
                result_area.config(state="normal")
                result_area.delete(1.0, tk.END)
                subject = entry_subject.get()
                sort_list = []
                for stu in students:
                    if subject in stu['scores']:
                        sort_list.append((stu, stu['scores'][subject]))
                sort_list.sort(key=lambda x: x[1], reverse=True)
                if sort_list:
                    result_area.insert(tk.END, f"科目'{subject}'成绩排序（高分在前）：\n")
                    for stu, score in sort_list:
                        line = f"学号：{stu['sid']}  姓名：{stu['name']}  成绩：{score}\n"
                        result_area.insert(tk.END, line)
                else:
                    result_area.insert(tk.END, f"未找到科目'{subject}'的成绩记录。")
                result_area.config(state="disabled")
            tk.Button(sort_win, text="排序", command=do_sort, width=15).pack(pady=10)

        def open_modify_window():
            modify_win = tk.Toplevel(manage_win)
            modify_win.title("修改成绩")
            modify_win.geometry("400x350")
            result_text = tk.Text(modify_win, width=45, height=8)
            result_text.pack(pady=10)
            tk.Label(modify_win, text="请输入学号：", font=("微软雅黑", 10)).pack(pady=5)
            entry_sid = tk.Entry(modify_win, width=25)
            entry_sid.pack(pady=5)
            tk.Label(modify_win, text="请输入科目：", font=("微软雅黑", 10)).pack(pady=5)
            entry_subject = tk.Entry(modify_win, width=25)
            entry_subject.pack(pady=5)
            tk.Label(modify_win, text="新成绩：", font=("微软雅黑", 10)).pack(pady=5)
            entry_score = tk.Entry(modify_win, width=25)
            entry_score.pack(pady=5)
            def do_modify():
                sid = entry_sid.get()
                subject = entry_subject.get()
                new_score = entry_score.get()
                stu = find_student_by_sid(sid)
                result_text.delete(1.0, tk.END)
                if stu and subject in stu['scores']:
                    if new_score:
                        stu['scores'][subject] = float(new_score)
                    result_text.insert(tk.END, f"修改成功！\n学号:{sid}  姓名：{stu['name']}  科目：{subject}  成绩：{stu['scores'][subject]}\n")
                else:
                    result_text.insert(tk.END, f"未找到学号{sid}的科目'{subject}'的成绩记录。")
            tk.Button(modify_win, text="确认修改", command=do_modify, width=15).pack(pady=10)

        def open_delete_window():
            delete_win = tk.Toplevel(manage_win)
            delete_win.title("删除成绩")
            delete_win.geometry("400x350")
            tk.Label(delete_win, text="请输入学号：", font=("微软雅黑", 12)).pack(pady=5)
            entry_sid = tk.Entry(delete_win, width=30)
            entry_sid.pack(pady=5)
            tk.Label(delete_win, text="请输入要删除的科目：", font=("微软雅黑", 12)).pack(pady=5)
            entry_subject = tk.Entry(delete_win, width=30)
            entry_subject.pack(pady=5)
            result_text = tk.Text(delete_win, width=45, height=10)
            result_text.pack(pady=10)
            def do_delete():
                sid = entry_sid.get()
                subject = entry_subject.get()
                stu = find_student_by_sid(sid)
                result_text.delete(1.0, tk.END)
                if stu and subject in stu['scores']:
                    del stu['scores'][subject]
                    if not stu['scores']:
                        students.remove(stu)
                    result_text.insert(tk.END, f"已删除：学号{sid}的科目'{subject}'成绩。\n")
                else:
                    result_text.insert(tk.END, f"未找到学号{sid}的科目'{subject}'的成绩记录。")
            tk.Button(delete_win, text="确认删除", command=do_delete, font=("微软雅黑", 12)).pack(pady=10)

        tk.Button(manage_win, text="录入成绩", width=15, command=open_add_window).pack(pady=5)
        tk.Button(manage_win, text="查看全部", width=15, command=open_view_window).pack(pady=5)
        tk.Button(manage_win, text="按科目查找", width=15, command=open_search_window).pack(pady=5)
        tk.Button(manage_win, text="成绩排序", width=15, command=open_sort_window).pack(pady=5)
        tk.Button(manage_win, text="修改成绩", width=15, command=open_modify_window).pack(pady=5)
        tk.Button(manage_win, text="删除成绩", width=15, command=open_delete_window).pack(pady=5)


    #2. AI 建议功能
    def open_ai_window():
        ai_win = tk.Toplevel(root)
        ai_win.title("AI学习建议")
        ai_win.geometry("500x450")
        tk.Label(ai_win, text="输入学生学号:", font=("微软雅黑", 10)).pack(pady=5)
        entry_sid = tk.Entry(ai_win, width=30)
        entry_sid.pack(pady=5)
        tk.Label(ai_win, text="输入科目:", font=("微软雅黑", 10)).pack(pady=5)
        entry_subject = tk.Entry(ai_win, width=30)
        entry_subject.pack(pady=5)
        result_text = tk.Text(ai_win, width=55, height=12)
        result_text.pack(pady=10)

        def generate_advice():
            sid = entry_sid.get()
            subject = entry_subject.get()
            stu = find_student_by_sid(sid)
            result_text.delete(1.0, tk.END)
            if stu and subject in stu['scores']:
                score = stu['scores'][subject]
                prompt = f"学生{stu['name']}，科目{subject}，当前成绩{score}分，请给出学习建议。"
                try:
                    response = requests.post(
                        "https://api.deepseek.com/v1/chat/completions",
                        headers={
                            "Authorization": "Bearer sk-90e14be38edc4e9481d2e139e6cd438c",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": "你是一位资深学习教练,请根据学生成绩给出鼓励和具体的学习建议。你的建议应该包含:1.对当前成绩的客观评价 2.具体可操作的改进方向 3.鼓励性的话语。"},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 500
                        },
                        timeout=15
                    )
                    if response.status_code == 200:
                        data = response.json()
                        ai_reply = data['choices'][0]['message']['content']
                    else:
                        ai_reply = f"API调取失败,状态码: {response.status_code}"
                except Exception as e:
                    ai_reply = f"网络请求出错：{str(e)}"
                result_text.insert(tk.END, f"学生姓名：{stu['name']}\n")
                result_text.insert(tk.END, f"科目：{subject}  成绩：{score}分\n\n")
                result_text.insert(tk.END, ai_reply)
            else:
                result_text.insert(tk.END, f"未找到学号{sid}的科目'{subject}'的成绩记录。")

        tk.Button(ai_win, text="生成建议", command=generate_advice, font=("微软雅黑", 15)).pack(pady=10)


    #3. 趋势追踪功能
    def trend_ai_window():
        trend_win = tk.Toplevel(root)
        trend_win.title("趋势追踪")
        trend_win.geometry("400x300")
        tk.Label(trend_win, text="成绩趋势图表功能开发中...", font=("微软雅黑", 12)).pack(pady=50)
        tk.Label(trend_win, text="敬请期待", font=("微软雅黑", 10)).pack(pady=10)


    #4. 本地存储功能
    def store_data():
        store_win = tk.Toplevel(root)
        store_win.title("本地存储")
        store_win.geometry("400x350")
        tk.Label(store_win, text=f"当前用户：{username}", font=("微软雅黑", 12)).pack(pady=10)
        tk.Label(store_win, text=f"数据文件:students_{username}.json", font=("微软雅黑", 10)).pack(pady=10)
        tk.Label(store_win, text=f"已存储 {len(students)} 名学生的成绩记录", font=("微软雅黑", 10)).pack(pady=10)
        # 统计科目
        all_subjects = set()
        for stu in students:
            all_subjects.update(stu['scores'].keys())
        if all_subjects:
            tk.Label(store_win, text=f"包含科目：{', '.join(all_subjects)}", font=("微软雅黑", 10)).pack(pady=10)
        tk.Label(store_win, text="数据将在退出时自动保存", font=("微软雅黑", 10), fg="gray").pack(pady=20)


    #主界面布局
    title_label = tk.Label(root, text=f"学迹 - {username}的学习空间", font=("微软雅黑", 16))
    title_label.pack(pady=15)

    tk.Label(root, text="—— 成绩管理 ——", font=("微软雅黑", 10), fg="gray").pack(pady=5)
    tk.Button(root, text="成绩管理", width=20, command=manage_message).pack(pady=10)

    tk.Label(root, text="—— AI 建议 ——", font=("微软雅黑", 10), fg="gray").pack(pady=5)
    tk.Button(root, text="AI 建议", width=20, command=open_ai_window).pack(pady=10)

    tk.Label(root, text="—— 趋势追踪 ——", font=("微软雅黑", 10), fg="gray").pack(pady=5)
    tk.Button(root, text="趋势追踪", width=20, command=trend_ai_window).pack(pady=10)

    tk.Label(root, text="—— 本地存储 ——", font=("微软雅黑", 10), fg="gray").pack(pady=5)
    tk.Button(root, text="本地存储", width=20, command=store_data).pack(pady=10)

    def on_closing():
        save_to_file(students)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    btn_exit = tk.Button(root, text="退出系统", width=20, command=on_closing)
    btn_exit.pack(pady=20)

    root.mainloop()