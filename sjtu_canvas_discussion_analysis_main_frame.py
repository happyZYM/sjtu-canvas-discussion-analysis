import tkinter as tk
import threading
import requests
from sjtu_login import login_using_cookies
from sjtu_qr_code_login_frame import QRCodeLoginFrame
from sjtu_canvas_discussion_analysis_helper import create_window

class MainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.urls = [
            "https://courses.sjtu.edu.cn/app/oauth/2.0/login?login_type=outer",
            "https://oc.sjtu.edu.cn/login/openid_connect"
        ]

        self.grid(sticky=tk.N+tk.S+tk.W+tk.E)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.qr_code_login_button = tk.Button(
            self,
            command=self.popup_qr_code_login,
            text="登录jAccount (二维码)"
        )
        self.qr_code_login_button.grid(column=0, row=0)

        self.status_label = tk.Label(self, text="未登录")
        self.status_label.grid(column=0, row=1)

        self.analyze_button = tk.Button(
            self,
            command=self.start_analysis,
            text="开始分析",
            state=tk.DISABLED
        )
        self.analyze_button.grid(column=0, row=2)

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
        url = "https://oc.sjtu.edu.cn/api/v1/courses/61525/discussion_topics?exclude_assignment_descriptions=true&exclude_context_module_locked_topics=true&include%5B%5D=sections_user_count&include%5B%5D=sections&include_assignment=true&page=1&per_page=1000&plain_messages=true"
        try:
            response = requests.get(url, cookies=self.cookies)
            response.raise_for_status()
            with open("data1.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            self.master.after(0, lambda: self.status_label.configure(text="讨论主页分析完成，已保存到文件"))
        except Exception as e:
            self.master.after(0, lambda: self.status_label.configure(text=f"讨论主页分析失败：{str(e)}"))
        url = "https://oc.sjtu.edu.cn/api/v1/courses/61525/discussion_topics/135019/view?include_new_entries=1&include_enrollment_state=1&include_context_card_info=1"
        try:
            response = requests.get(url, cookies=self.cookies)
            response.raise_for_status()
            with open("data2.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            self.master.after(0, lambda: self.status_label.configure(text="讨论页面分析完成，已保存到文件"))
        except Exception as e:
            self.master.after(0, lambda: self.status_label.configure(text=f"讨论页面分析失败：{str(e)}"))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("jAccount QR Code Login")
    root.geometry("300x200")
    app = MainFrame(master=root)
    app.mainloop()