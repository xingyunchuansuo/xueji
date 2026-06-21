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
    root.title("学生信息管理系统")
    root.geometry("500x450")

    def open_add_window():
        add_win = tk.Toplevel(root)
        add_win.title("录入学生")
        add_win.geometry("300x250")

        tk.Label(add_win, text="姓名").pack(pady=5)
        entry_name = tk.Entry(add_win)
        entry_name.pack(pady=5)

        tk.Label(add_win, text="学号").pack(pady=5)
        entry_sid = tk.Entry(add_win)
        entry_sid.pack(pady=5)

        tk.Label(add_win, text="成绩").pack(pady=5)
        entry_score = tk.Entry(add_win)
        entry_score.pack(pady=5)  
        def save_student():
            name = entry_name.get()
            sid = entry_sid.get()
            score = float(entry_score.get())
            stu = {"name": name, "sid": sid, "score": score}
            students.append(stu)
            print(f"已录入：{stu}")   
            add_win.destroy()       

        tk.Button(add_win, text="保存", command=save_student).pack(pady=10)



    def open_view_window():
        view_win = tk.Toplevel(root)
        view_win.title("查看全部学生")
        view_win.geometry("400x300")

        if not students:
            tk.Label(view_win, text="暂时没有学生数据", font=("微软雅黑", 12)).pack(pady=50)
        else:
            tk.Label(view_win, text=f"一共{len(students)}个学生", font=("微软雅黑", 12)).pack(pady=10)
            text_area = tk.Text(view_win, width=45, height=12)
            text_area.pack(pady=10)
            for stu in students:
                line = f"姓名：{stu['name']}  学号：{stu['sid']}  成绩：{stu['score']}\n"
                text_area.insert(tk.END, line)
            text_area.config(state="disabled") 



    def open_search_window():
        search_win = tk.Toplevel(root)
        search_win.title("按姓名查找学生")
        search_win.geometry("400x300")

        tk.Label(search_win, text="输入要查找的姓名或关键字:", font=("微软雅黑", 10)).pack(pady=10)
        entry_keyword = tk.Entry(search_win, width=30)
        entry_keyword.pack(pady=5)

        result_area = tk.Text(search_win, width=45, height=10)
        result_area.pack(pady=10)

        def do_search():
            result_area.config(state="normal")
            result_area.delete(1.0, tk.END)
            keyword = entry_keyword.get()
            found_list = []
            for stu in students:
                if keyword in stu['name']:
                    found_list.append(stu)
            if found_list:
                result_area.insert(tk.END, f"找到了 {len(found_list)} 条匹配记录:\n")
                for stu in found_list:
                    line = f"姓名：{stu['name']}  学号：{stu['sid']}  成绩：{stu['score']}\n"
                    result_area.insert(tk.END, line)
            else:
                result_area.insert(tk.END, f"未找到姓名包含 '{keyword}' 的学生。")
            result_area.config(state="disabled")

        tk.Button(search_win, text="查找", command=do_search, width=15).pack(pady=10)



    def open_sort_window():

        sort_win = tk.Toplevel(root)
        sort_win.title("排序")
        sort_win.geometry("400x300")

        if not students:
            tk.Label(sort_win, text="暂时没有学生数据", font=("微软雅黑", 12)).pack(pady=50)
        else:
            tk.Label(sort_win, text="按成绩排序（高分在前）", font=("微软雅黑", 12)).pack(pady=10)
            sorted_students = sorted(students, key=lambda stu: stu["score"], reverse=True)
            text_area = tk.Text(sort_win, width=45, height=12)
            text_area.pack(pady=10)
            for stu in sorted_students:          
                line = f"姓名：{stu['name']}  学号：{stu['sid']}  成绩：{stu['score']}\n"
                text_area.insert(tk.END, line)
            text_area.config(state="disabled")  



    def open_modify_window():
        modify_win = tk.Toplevel(root)
        modify_win.title("修改学生数据")
        modify_win.geometry("400x450")

        result_text = tk.Text(modify_win, width=45, height=8)
        result_text.pack(pady=10)

        tk.Label(modify_win, text="请输入要修改的学生学号：", font=("微软雅黑", 10)).pack(pady=5)
        entry_sid = tk.Entry(modify_win, width=25)
        entry_sid.pack(pady=5)

        tk.Label(modify_win, text="新姓名（留空则不修改）：", font=("微软雅黑", 10)).pack(pady=5)
        entry_name = tk.Entry(modify_win, width=25)
        entry_name.pack(pady=5)

        tk.Label(modify_win, text="新成绩（留空则不修改）：", font=("微软雅黑", 10)).pack(pady=5)
        entry_score = tk.Entry(modify_win, width=25)
        entry_score.pack(pady=5)

        def do_modify():
            sid = entry_sid.get()
            new_name = entry_name.get()
            new_score = entry_score.get()
            found = False
            for stu in students:
                if stu['sid'] == sid:
                    found = True
                    if new_name:
                        stu['name'] = new_name
                    if new_score:
                        stu['score'] = float(new_score)
                    line = f"姓名：{stu['name']}  学号：{stu['sid']}  成绩：{stu['score']}\n"
                    result_text.delete(1.0, tk.END)
                    result_text.insert(tk.END, "修改成功！\n")
                    result_text.insert(tk.END, line)
                    break
            if not found:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"未找到学号为 {sid} 的学生。")

        tk.Button(modify_win, text="确认修改", command=do_modify, width=15).pack(pady=10)


                
    def open_delete_window():
        delete_win = tk.Toplevel(root)
        delete_win.title("删除学生")
        delete_win.geometry("400x350")

        tk.Label(delete_win, text="请输入你要删除的学生的学号：", font=("微软雅黑", 12)).pack(pady=10)
        entry_sid = tk.Entry(delete_win, width=30)
        entry_sid.pack(pady=5)

        result_text = tk.Text(delete_win, width=45, height=12)
        result_text.pack(pady=10)

        def do_delete():
            sid = entry_sid.get()
            found = False
            for stu in students:
                if sid == stu['sid']:
                    found = True
                    students.remove(stu)
                    result_text.delete(1.0, tk.END) 
                    result_text.insert(tk.END, f"已删除：{stu['name']}(学号 {sid})\n\n")
                    break  
            if not found:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"未找到学号为 {sid} 的学生。\n")
            else:
                result_text.insert(tk.END, "当前学生列表：\n")
                for stu in students:
                    line = f"姓名：{stu['name']}  学号：{stu['sid']}  成绩：{stu['score']}\n"
                    result_text.insert(tk.END, line)

        tk.Button(delete_win, text="确认删除", command=do_delete, font=("微软雅黑", 12)).pack(pady=10)
            


    def open_ai_window():
        ai_win = tk.Toplevel(root)
        ai_win.title("AI学习建议")
        ai_win.geometry("500x400")

        tk.Label(ai_win,text="输入学生学号:",font=("微软雅黑",10)).pack(pady=10)
        entry_sid = tk.Entry(ai_win,width=30)
        entry_sid.pack(pady=5)

        result_text = tk.Text(ai_win,width = 45,height=12)
        result_text.pack(pady=10)

        def generate_advice():
            sid = entry_sid.get()
            found =False
            for stu in students:
                if sid == stu['sid']:
                    found =True
                    prompt = f"学生{stu['name']},当前成绩{stu['score']}分,请给出学习建议。"
                    try:
                        response = requests.post("https://httpbin.org/post",
                                                json={"prompt":prompt},
                                                timeout=5
                        )
                        if response.status_code==200:
                            data = response.json()
                            ai_reply = f"AI已收到你的问题:{data['json']['prompt']}\n\n"
                            ai_reply += "(这是模拟AI回复。接入真实API后,这里会显示真正的学习建议。)"
                        else:
                            ai_reply = f"API调取失败,状态码: {response.status_code}"
                    except Exception as e:
                        ai_reply = f"网络请求出错：{str(e)}"
                    result_text.delete(1.0,tk.END)
                    result_text.insert(tk.END,f"学生姓名:{stu['name']}\n")
                    result_text.insert(tk.END,f"当前成绩:{stu['score']}分\n\n")
                    result_text.insert(tk.END,ai_reply)
                    break
            if not found:
                result_text.delete(1.0,tk.END)
                result_text.insert(tk.END,f"未找到学号为 {sid} 的学生。")

        tk.Button(ai_win,text="生成建议",command=generate_advice,font=("微软雅黑",15)).pack(pady=10)



    title_label = tk.Label(root, text="学生信息管理系统", font=("微软雅黑", 16))
    title_label.pack(pady=20)

    btn_add = tk.Button(root, text="录入学生", width=20, command=open_add_window)
    btn_add.pack(pady=5)

    btn_view = tk.Button(root, text="查看全部", width=20, command=open_view_window)
    btn_view.pack(pady=5)

    btn_search = tk.Button(root, text="按姓名查找", width=20, command=open_search_window)
    btn_search.pack(pady=5)

    btn_sort = tk.Button(root, text="按成绩顺序排序", width=20, command=open_sort_window)
    btn_sort.pack(pady=5)

    btn_modify = tk.Button(root, text="修改姓名或成绩信息", width=20, command=open_modify_window)
    btn_modify.pack(pady=5)

    btn_delete = tk.Button(root, text="删除学生信息", width=20, command=open_delete_window)
    btn_delete.pack(pady=5)

    btn_ai = tk.Button(root,text="AI学习建议",width=20,command=open_ai_window)
    btn_ai.pack(pady=5)

    def on_closing():
        save_to_file(students)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    btn_exit = tk.Button(root, text="退出系统", width=20, command=on_closing)
    btn_exit.pack(pady=20)

    root.mainloop()