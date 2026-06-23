import sys
import io
import tkinter as tk
import json
import requests
from datetime import datetime
import matplotlib.pyplot as plt


def open_main_window(username):
    
    #加载函数
    def load_from_file():
        filename = f"students_{username}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    #保存函数
    def save_to_file(data):
        filename = f"students_{username}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    subject_records = load_from_file()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    root = tk.Tk()
    root.title(f"学迹 - {username}")
    root.geometry("500x500")

    #核心辅助函数：根据科目名查找对应的记录项
    def find_subject(subject):
        for item in subject_records:
            if item['subject'] == subject:
                return item
        return None

    #1. 成绩管理功能
    def manage_message():
        manage_win = tk.Toplevel(root)
        manage_win.title("成绩管理")
        manage_win.geometry("400x350")
    
        # 录入成绩窗口
        def open_add_window():
            add_win = tk.Toplevel(manage_win)
            add_win.title("录入成绩")
            add_win.geometry("300x250")
            tk.Label(add_win, text="科目").pack(pady=5)
            entry_subject = tk.Entry(add_win)
            entry_subject.pack(pady=5)
            tk.Label(add_win, text="成绩").pack(pady=5)
            entry_score = tk.Entry(add_win)
            entry_score.pack(pady=5)
            def save_score():
                subject = entry_subject.get()
                try:
                    score = float(entry_score.get())
                except ValueError:
                    return
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                item = find_subject(subject)
                if item:
                    item['history'].append({"score": score, "time": now})
                else:
                    subject_records.append({
                        "subject": subject,
                        "history": [{"score": score, "time": now}]
                    })
                add_win.destroy()
            tk.Button(add_win, text="保存", command=save_score).pack(pady=10)

        # 查看全部成绩窗口
        def open_view_window():
            view_win = tk.Toplevel(manage_win)
            view_win.title("查看全部成绩")
            view_win.geometry("500x350")
            if not subject_records:
                tk.Label(view_win, text="暂时没有成绩记录", font=("微软雅黑", 12)).pack(pady=50)
            else:
                tk.Label(view_win, text="所有科目成绩总览", font=("微软雅黑", 12)).pack(pady=10)
                text_area = tk.Text(view_win, width=55, height=14)
                text_area.pack(pady=10)
                for item in subject_records:
                    text_area.insert(tk.END, f"【{item['subject']}】\n")
                    for r in item['history']:
                        text_area.insert(tk.END, f"  成绩：{r['score']}分  时间：{r['time']}\n")
                    text_area.insert(tk.END, "\n")
                text_area.config(state="disabled")

        # 按科目查找窗口
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
                item = find_subject(subject)
                if item:
                    result_area.insert(tk.END, f"科目 '{subject}' 的历史成绩：\n")
                    for i, r in enumerate(item['history']):
                        date = r['time'][:10]
                        label = f"{date}-{i+1}"
                        result_area.insert(tk.END, f"  {label}  成绩：{r['score']}分\n")
                else:
                    result_area.insert(tk.END, f"未找到科目 '{subject}' 的成绩记录。")
                result_area.config(state="disabled")
            tk.Button(search_win, text="查找", command=do_search, width=15).pack(pady=10)

        # 排序成绩窗口
        def open_sort_window():
            sort_win = tk.Toplevel(manage_win)
            sort_win.title("成绩排序")
            sort_win.geometry("400x350")
            tk.Label(sort_win, text="输入要排序的科目:", font=("微软雅黑", 10)).pack(pady=10)
            entry_subject = tk.Entry(sort_win, width=30)
            entry_subject.pack(pady=5)
            result_area = tk.Text(sort_win, width=45, height=8)
            result_area.pack(pady=10)
            def do_sort():
                result_area.config(state="normal")
                result_area.delete(1.0, tk.END)
                subject = entry_subject.get()
                item = find_subject(subject)
                if item:
                    sorted_list = sorted(item['history'], key=lambda r: r['score'], reverse=True)
                    result_area.insert(tk.END, f"科目 '{subject}' 成绩排序（高分在前）：\n")
                    for r in sorted_list:
                        result_area.insert(tk.END, f"  成绩：{r['score']}分  时间：{r['time']}\n")
                else:
                    result_area.insert(tk.END, f"未找到科目 '{subject}' 的成绩记录。")
                result_area.config(state="disabled")
            tk.Button(sort_win, text="排序", command=do_sort, width=15).pack(pady=10)

        # 修改成绩窗口
        def open_modify_window():
            modify_win = tk.Toplevel(manage_win)
            modify_win.title("修改成绩")
            modify_win.geometry("500x400")

            tk.Label(modify_win, text="输入科目名称:", font=("微软雅黑", 10)).pack(pady=5)
            entry_subject = tk.Entry(modify_win, width=25)
            entry_subject.pack(pady=5)

            result_text = tk.Text(modify_win, width=55, height=8)
            result_text.pack(pady=10)

            def query_records():
                result_text.config(state="normal")
                result_text.delete(1.0, tk.END)
                subject = entry_subject.get()
                item = find_subject(subject)
                if item:
                    result_text.insert(tk.END, f"科目 '{subject}' 的历史记录：\n")
                    current_date = ""
                    daily_index = 0
                    for r in item['history']:
                        date = r['time'][:10]
                        if date != current_date:
                            current_date = date
                            daily_index = 1
                        else:
                            daily_index += 1
                        label = f"{date}-{daily_index}"
                        result_text.insert(tk.END, f"  {label}  成绩：{r['score']}分\n")
                else:
                    result_text.insert(tk.END, f"未找到科目 '{subject}' 的成绩记录。")
                result_text.config(state="disabled")

            def do_modify():
                subject = entry_subject.get()
                item = find_subject(subject)
                if not item:
                    result_text.config(state="normal")
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "请先查询科目记录。")
                    result_text.config(state="disabled")
                    return
                
                user_input = entry_label.get()
                try:
                    parts = user_input.rsplit("-", 1)
                    target_date = parts[0]
                    target_num = int(parts[1])
                except (ValueError, IndexError):
                    result_text.config(state="normal")
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "输入格式错误。")
                    result_text.config(state="disabled")
                    return
                
                try:
                    new_score = float(entry_score.get())
                except ValueError:
                    return
                
                current_date = ""
                daily_index = 0
                found = False
                for idx, r in enumerate(item['history']):
                    date = r['time'][:10]
                    if date != current_date:
                        current_date = date
                        daily_index = 1
                    else:
                        daily_index += 1
                    if date == target_date and daily_index == target_num:
                        item['history'][idx]['score'] = new_score
                        found = True
                        result_text.config(state="normal")
                        result_text.delete(1.0, tk.END)
                        result_text.insert(tk.END, f"修改成功！\n{user_input}  新成绩：{new_score}分")
                        result_text.config(state="disabled")
                        break
                if not found:
                    result_text.config(state="normal")
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "未找到匹配的记录。")
                    result_text.config(state="disabled")

            tk.Button(modify_win, text="查询记录", command=query_records, width=15).pack(pady=5)
            
            tk.Label(modify_win, text="输入要修改的记录标识(如 2026-06-22-1):", font=("微软雅黑", 10)).pack(pady=5)
            entry_label = tk.Entry(modify_win, width=25)
            entry_label.pack(pady=5)
            
            tk.Label(modify_win, text="新成绩:", font=("微软雅黑", 10)).pack(pady=5)
            entry_score = tk.Entry(modify_win, width=25)
            entry_score.pack(pady=5)
            
            tk.Button(modify_win, text="确认修改", command=do_modify, width=15).pack(pady=5)

        # 删除成绩窗口
        def open_delete_window():
            delete_win = tk.Toplevel(manage_win)
            delete_win.title("删除成绩")
            delete_win.geometry("500x400")
            
            tk.Label(delete_win, text="输入科目名称:", font=("微软雅黑", 10)).pack(pady=5)
            entry_subject = tk.Entry(delete_win, width=25)
            entry_subject.pack(pady=5)
            
            result_text = tk.Text(delete_win, width=55, height=8)
            result_text.pack(pady=10)

            def query_records():
                result_text.config(state="normal")
                result_text.delete(1.0, tk.END)
                subject = entry_subject.get()
                item = find_subject(subject)
                if item:
                    result_text.insert(tk.END, f"科目 '{subject}' 的历史记录：\n")
                    current_date = ""
                    daily_index = 0
                    for r in item['history']:
                        date = r['time'][:10]
                        if date != current_date:
                            current_date = date
                            daily_index = 1
                        else:
                            daily_index += 1
                        label = f"{date}-{daily_index}"
                        result_text.insert(tk.END, f"  {label}  成绩：{r['score']}分\n")
                else:
                    result_text.insert(tk.END, f"未找到科目 '{subject}' 的成绩记录。")
                result_text.config(state="disabled")

            def do_delete():
                subject = entry_subject.get()
                item = find_subject(subject)
                if not item:
                    result_text.config(state="normal")
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "请先查询科目记录。")
                    result_text.config(state="disabled")
                    return
                
                user_input = entry_label.get()
                try:
                    parts = user_input.rsplit("-", 1)
                    target_date = parts[0]
                    target_num = int(parts[1])
                except (ValueError, IndexError):
                    result_text.config(state="normal")
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "输入格式错误。")
                    result_text.config(state="disabled")
                    return
                
                current_date = ""
                daily_index = 0
                found = False
                for idx, r in enumerate(item['history']):
                    date = r['time'][:10]
                    if date != current_date:
                        current_date = date
                        daily_index = 1
                    else:
                        daily_index += 1
                    if date == target_date and daily_index == target_num:
                        removed = item['history'].pop(idx)
                        if not item['history']:
                            subject_records.remove(item)
                        found = True
                        result_text.config(state="normal")
                        result_text.delete(1.0, tk.END)
                        result_text.insert(tk.END, f"已删除：{subject} {removed['score']}分")
                        result_text.config(state="disabled")
                        break
                if not found:
                    result_text.config(state="normal")
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "未找到匹配的记录。")
                    result_text.config(state="disabled")

            tk.Button(delete_win, text="查询记录", command=query_records, width=15).pack(pady=5)
            
            tk.Label(delete_win, text="输入要删除的记录标识(如 2026-06-22-1):", font=("微软雅黑", 10)).pack(pady=5)
            entry_label = tk.Entry(delete_win, width=25)
            entry_label.pack(pady=5)

            tk.Button(delete_win, text="确认删除", command=do_delete, width=15).pack(pady=5)

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
        tk.Label(ai_win, text="输入科目（分析该科目历史成绩）:", font=("微软雅黑", 10)).pack(pady=5)
        entry_subject = tk.Entry(ai_win, width=30)
        entry_subject.pack(pady=5)
        result_text = tk.Text(ai_win, width=55, height=14)
        result_text.pack(pady=10)

        def generate_advice():
            btn_ai_analysis.config(state=tk.DISABLED)
            subject = entry_subject.get()
            item = find_subject(subject)
            if not item:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"未找到科目 '{subject}' 的成绩记录。")
                btn_ai_analysis.config(state=tk.NORMAL)
                return
            scores = [r['score'] for r in item['history']]
            prompt = f"我最近在科目'{subject}'上的成绩记录如下：\n"
            for r in item['history']:
                prompt += f"- {r['time']}: {r['score']}分\n"
            prompt += "\n请根据以上成绩变化趋势,给出学习建议(包括趋势分析、薄弱点、改进方向、鼓励的话语)。"
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
                            {"role": "system", "content": "你是一位资深学习顾问，擅长根据成绩变化趋势给出具体学习建议。"},
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
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"科目：{subject}\n")
            result_text.insert(tk.END, f"历史成绩：{', '.join(map(str, scores))}\n\n")
            result_text.insert(tk.END, ai_reply)
            btn_ai_analysis.config(state=tk.NORMAL)

        btn_ai_analysis = tk.Button(ai_win, text="生成建议", command=generate_advice, font=("微软雅黑", 15))
        btn_ai_analysis.pack(pady=10)


    #3. 趋势追踪功能
    def trend_ai_window():
        trend_win = tk.Toplevel(root)
        trend_win.title("趋势追踪")
        trend_win.geometry("800x750")

        tk.Label(trend_win, text="输入科目(绘制成绩趋势图)", font=("微软雅黑", 10)).pack(pady=5)
        entry_subject = tk.Entry(trend_win, width=30)
        entry_subject.pack(pady=5)

        canvas_frame = tk.Frame(trend_win)

        result_text = tk.Text(trend_win, width=70, height=8)

        def create_trend_chart():
            for widget in canvas_frame.winfo_children():
                widget.destroy()

            subject = entry_subject.get()
            item = find_subject(subject)
            if not item:
                tk.messagebox.showwarning("提示", f"未找到科目 '{subject}' 的成绩记录。")
                return

            scores = []
            times = []
            for i, r in enumerate(item['history']):
                scores.append(r['score'])
                times.append(f"第{i+1}次")

            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False

            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(times, scores, marker='o', color='blue')
            ax.set_title(f"{subject}成绩趋势")
            ax.set_xlabel("考试次数")
            ax.set_ylabel("成绩")

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        def generate_advice():
            btn_ai_analysis.config(state=tk.DISABLED)
            subject = entry_subject.get()
            item = find_subject(subject)
            if not item:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"未找到科目 '{subject}' 的成绩记录。")
                btn_ai_analysis.config(state=tk.NORMAL)
                return
            scores = [r['score'] for r in item['history']]
            prompt = f"我最近在科目'{subject}'上的成绩记录如下：\n"
            for r in item['history']:
                prompt += f"- {r['time']}: {r['score']}分\n"
            prompt += "\n请根据以上成绩变化趋势,给出学习建议(包括趋势分析、薄弱点、改进方向、鼓励的话语)。"
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
                            {"role": "system", "content": "你是一位资深学习顾问，擅长根据成绩变化趋势给出具体学习建议。"},
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
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f"科目：{subject}\n")
            result_text.insert(tk.END, f"历史成绩：{', '.join(map(str, scores))}\n\n")
            result_text.insert(tk.END, ai_reply)
            btn_ai_analysis.config(state=tk.NORMAL)

        btn_frame = tk.Frame(trend_win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="生成趋势图", command=create_trend_chart, font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=10)
        btn_ai_analysis = tk.Button(btn_frame, text="生成AI分析", command=generate_advice, font=("微软雅黑", 10))
        btn_ai_analysis.pack(side=tk.LEFT, padx=10)

        canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        result_text.pack(pady=10, fill=tk.X)

    #4. 本地存储功能
    def store_data():
        store_win = tk.Toplevel(root)
        store_win.title("本地存储")
        store_win.geometry("400x350")
        tk.Label(store_win, text=f"当前用户：{username}", font=("微软雅黑", 12)).pack(pady=10)
        tk.Label(store_win, text=f"数据文件:students_{username}.json", font=("微软雅黑", 10)).pack(pady=10)
        total_count = sum(len(item['history']) for item in subject_records)
        tk.Label(store_win, text=f"共 {total_count} 条成绩记录，{len(subject_records)} 个科目", font=("微软雅黑", 10)).pack(pady=10)
        if subject_records:
            subjects_list = [item['subject'] for item in subject_records]
            tk.Label(store_win, text=f"包含科目：{', '.join(subjects_list)}", font=("微软雅黑", 10)).pack(pady=10)
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
        save_to_file(subject_records)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    btn_exit = tk.Button(root, text="退出系统", width=20, command=on_closing)
    btn_exit.pack(pady=20)

    root.mainloop()