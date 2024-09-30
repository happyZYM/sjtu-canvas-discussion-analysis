import tkinter as tk
from tkinter import filedialog
import threading
import requests
from sjtu_login import login_using_cookies
from sjtu_qr_code_login_frame import QRCodeLoginFrame
from sjtu_canvas_discussion_analysis_helper import create_window
import json
import re
from datetime import datetime

class MainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.urls = [
            "https://courses.sjtu.edu.cn/app/oauth/2.0/login?login_type=outer",
            "https://oc.sjtu.edu.cn/login/openid_connect"
        ]

        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)
        self.columnconfigure(0, weight=1)
        for i in range(5):
            self.rowconfigure(i, weight=1)

        self.qr_code_login_button = tk.Button(
            self,
            command=self.popup_qr_code_login,
            text="登录jAccount (二维码)"
        )
        self.qr_code_login_button.grid(column=0, row=0)

        self.status_label = tk.Label(self, text="未登录")
        self.status_label.grid(column=0, row=1)

        self.course_id_label = tk.Label(self, text="课程数字ID：")
        self.course_id_label.grid(column=0, row=2, sticky=tk.W)
        self.course_id_entry = tk.Entry(self)
        self.course_id_entry.grid(column=0, row=3, sticky=tk.W+tk.E)
        self.course_id_entry.insert(0, "61525")

        self.analyze_button = tk.Button(
            self,
            command=self.start_analysis,
            text="开始分析",
            state=tk.DISABLED
        )
        self.analyze_button.grid(column=0, row=4)

        self.save_button = tk.Button(
            self,
            command=self.save_results,
            text="保存结果",
            state=tk.DISABLED
        )
        self.save_button.grid(column=0, row=5)

        self.cookies = None

    def popup_qr_code_login(self):
        window = create_window(self.master)
        window.geometry("300x300")
        QRCodeLoginFrame(
            self.urls[0],
            self.update_cookies_and_refresh,
            window
        )

    def update_cookies_and_refresh(self, cookies):
        login_using_cookies(self.urls[1], cookies)
        self.cookies = cookies
        self.refresh_status_label()
        self.analyze_button.config(state=tk.NORMAL)

    def refresh_status_label(self):
        if self.cookies:
            self.status_label.configure(text="已登录")
        else:
            self.status_label.configure(text="未登录")

    def start_analysis(self):
        if self.cookies:
            thread = threading.Thread(target=self.download_and_save_page)
            thread.start()
            self.status_label.configure(text="正在分析...")

    def download_and_save_page(self):
        course_id = self.course_id_entry.get()
        url = f"https://oc.sjtu.edu.cn/api/v1/courses/{course_id}/discussion_topics?exclude_assignment_descriptions=true&exclude_context_module_locked_topics=true&include%5B%5D=sections_user_count&include%5B%5D=sections&include_assignment=true&page=1&per_page=1000&plain_messages=true"
        try:
            response = requests.get(url, cookies=self.cookies)
            response.raise_for_status()
            discussion_list_raw = json.loads(response.text)
            self.master.after(0, lambda: self.status_label.configure(text="讨论主页分析完成"))
        except Exception as e:
            self.master.after(0, lambda: self.status_label.configure(text=f"讨论主页分析失败：{str(e)}"))
            return

        discussion_list = []
        for item in discussion_list_raw:
            topic_id = re.search(r'/(\d+)$', item["url"]).group(1)
            discussion_list.append({
                "title": item["title"],
                "url": item["url"],
                "topic_id": topic_id
            })

        # with open("discussion_list.json", "w", encoding="utf-8") as f:
            # json.dump(discussion_list, f, ensure_ascii=False, indent=2)

        for index, topic in enumerate(discussion_list):
            topic_id = topic["topic_id"]
            url = f"https://oc.sjtu.edu.cn/api/v1/courses/{course_id}/discussion_topics/{topic_id}/view?include_new_entries=1&include_enrollment_state=1&include_context_card_info=1"
            try:
                response = requests.get(url, cookies=self.cookies)
                response.raise_for_status()
                topic_data_raw = json.loads(response.text)
                topic["topic_data_raw"] = topic_data_raw
                
                # Save each topic's data to a separate file
                # with open(f"topic_{topic_id}_raw.json", "w", encoding="utf-8") as f:
                    # json.dump(topic_data_raw, f, ensure_ascii=False, indent=2)
                
                self.master.after(0, lambda: self.status_label.configure(text=f"已分析 {index + 1}/{len(discussion_list)} 个讨论主题"))
            except Exception as e:
                self.master.after(0, lambda: self.status_label.configure(text=f"讨论主题 {topic_id} 分析失败：{str(e)}"))

        self.master.after(0, lambda: self.status_label.configure(text="所有讨论主题数据下载完毕，开始统计..."))
        student_dict = {}
        none_student_list=[]
        for index, topic in enumerate(discussion_list):
            topic_data_raw = topic["topic_data_raw"]
            participants_list = topic_data_raw["participants"]
            for participant in participants_list:
                student_id = participant["id"]
                if student_id not in student_dict:
                    student_dict[student_id] = {
                        "name": participant["display_name"],
                        "total_posts": 0,
                        "total_replies": 0
                    }
                if not participant["is_student"]:
                    none_student_list.append(student_id)
            posts_list = topic_data_raw["view"]
            for post in posts_list:
                if "deleted" in post and post["deleted"]:
                    continue
                student_dict[post["user_id"]]["total_posts"] += 1
                if "replies" not in post:
                    continue
                replies_list = post["replies"]
                for reply in replies_list:
                    if "deleted" in reply and reply["deleted"]:
                        continue
                    student_dict[reply["user_id"]]["total_replies"] += 1
        for none_student in none_student_list:
            if none_student in student_dict:
                student_dict.pop(none_student)
        # with open("student_dict.json", "w", encoding="utf-8") as f:
            # json.dump(student_dict, f, ensure_ascii=False, indent=2)
        self.student_dict = student_dict
        self.master.after(0, lambda: self.status_label.configure(text="统计完毕"))
        self.master.after(0, lambda: self.save_button.config(state=tk.NORMAL))
        self.course_id = course_id
    def save_results(self):
        current_date = datetime.now().strftime("%Y%m%d")
        default_filename = f"student_discussion_data_{self.course_id}_{current_date}.json"
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                                                initialfile=default_filename)
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.student_dict, f, ensure_ascii=False, indent=2)
            self.master.after(0, lambda: self.status_label.configure(text=f"结果已保存到 {file_path}"))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("jAccount QR Code Login")
    root.geometry("300x300")
    app = MainFrame(master=root)
    app.mainloop()