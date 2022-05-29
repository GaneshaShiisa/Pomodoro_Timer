"""Pomodoro Timer

Pomodoro Timerは、いわゆるポモドーロテクニック用のタイマーアプリケーションです。
25分と5分のタイマーが用意されています。

"""
import tkinter
import tkinter.font
import threading
import time
import pyautogui


class Application(tkinter.Frame):
    """
    """
    STATUS_STOP = 0
    STATUS_WORK = 10
    STATUS_WORK_PAUSE = 11
    STATUS_WORK_END = 19
    STATUS_BREAK = 20
    STATUS_BREAK_PAUSE = 21
    STATUS_BREAK_END = 29

    def __init__(self, master=None):
        super().__init__(master)
        master.title("Pomodoro Timer")
        width = 282
        height = 83
        screen_width = self.master.winfo_screenwidth()
        master.geometry(str(width)+"x"+str(height) +
                        "+"+str(screen_width-width-10)+"+0")
        master.resizable(0, 0)
        self.master = master

        # ショートカットの設定
        master.bind("<Alt-w>", self.evt_button_work_start)
        master.bind("<Alt-q>", self.evt_button_break_start)

        # self.create_shortcat(master)
        self.pack(pady=5)
        self.create_widgets()

        # 初期値の設定
        self.base_time = time.time()
        self.pause_time = 0
        self.pause_time_buf = 0
        self.status = self.STATUS_STOP
        self.flash_count = 0
        self.previous_position = pyautogui.position()
        self.active_time = time.time()

        # スケジューラの起動
        self.time_buf = round(time.time(), 0)
        self.time_event()

    # def create_shortcat(self, master):

    def create_widgets(self):
        """Widgetの配置
        """
        font_timer = tkinter.font.Font(family="游ゴシック", size=30, weight="bold")
        self.label_mm = tkinter.Label(
            self, text='{:>2}'.format(0), font=font_timer, width=2, anchor=tkinter.E)
        self.label_mm.grid(row=0, column=0, rowspan=2)
        self.label_colon = tkinter.Label(self, text=':', font=font_timer)
        self.label_colon.grid(row=0, column=1, rowspan=2)
        self.label_ss = tkinter.Label(
            self, text='{:02}'.format(0), font=font_timer, width=2)
        self.label_ss.grid(row=0, column=2, rowspan=2)

        self.blank = tkinter.Label(self, text=' ')
        self.blank.grid(row=0, column=3, rowspan=2)

        font_button = tkinter.font.Font(family="游ゴシック", size=12)
        self.button_work_start = tkinter.Button(
            self, text="作業 ▶", font=font_button, width=6,
            command=self.evt_button_work_start)

        self.button_work_start.grid(row=0, column=4)
        self.button_break_start = tkinter.Button(
            self, text="休憩 ▶", font=font_button, width=6,
            command=self.evt_button_break_start)
        self.button_break_start.grid(row=1, column=4)
        self.button_pause = tkinter.Button(
            self, text="一時停止", font=font_button, width=6,
            command=self.evt_button_pause)
        self.button_pause.grid(row=0, column=5)
        self.button_stop = tkinter.Button(
            self, text="停止", font=font_button, width=6,
            command=self.evt_button_stop)
        self.button_stop.grid(row=1, column=5)

    def set_background_colour(self, color_name):
        """背景色を設定する

        Args:
            color_name (int): 色名称
        """
        self['bg'] = color_name
        self.label_mm['bg'] = color_name
        self.label_colon['bg'] = color_name
        self.label_ss['bg'] = color_name
        self.blank['bg'] = color_name

    def set_window_active(self):
        """Windowのアクティブ化
        """
        # Windowを最前面に移動する
        self.master.attributes("-topmost", True)
        self.master.attributes("-topmost", False)
        # Windowをアクティブにする
        x, y = pyautogui.position()
        pyautogui.moveTo(self.master.winfo_x(), self.master.winfo_y())
        pyautogui.click()
        pyautogui.moveTo(x, y)  # 元の位置にマウスを戻す

    def time_event(self):
        """スケジューラの制御
        """

        tmp = time.time()
        if(tmp - self.time_buf) >= 1:  # 1sec経過した場合
            th = threading.Thread(target=self.main_event)
            th.start()
            self.time_buf += 1
        self.after(1000, self.time_event)

    def main_event(self):
        """メイン処理
        """
        # スクリーンセイバー無効化
        if self.previous_position != pyautogui.position():
            self.previous_position = pyautogui.position()
            self.active_time = time.time()

        if (time.time() - self.active_time) >= 60:
            pyautogui.press("shift")
            self.active_time = time.time()

        # 残り時間の計算
        if self.status == self.STATUS_WORK_PAUSE or self.status == self.STATUS_BREAK_PAUSE:
            pause_time_tmp = time.time() - self.pause_time_buf
        else:
            pause_time_tmp = 0
        remaining_time = int(
            round(self.base_time + self.pause_time + pause_time_tmp - time.time(), 0))
        if remaining_time <= 0:
            remaining_time = 0
            if self.status == self.STATUS_WORK:
                self.status = self.STATUS_WORK_END
                self.button_break_start['state'] = tkinter.NORMAL
                self.flash_count = 0
            elif self.status == self.STATUS_BREAK:
                self.status = self.STATUS_BREAK_END
                self.button_work_start['state'] = tkinter.NORMAL
                self.flash_count = 0

        # 残り時間の描画
        time_mm, time_ss = divmod(remaining_time, 60)
        self.label_mm["text"] = '{:>2}'.format(time_mm)
        self.label_ss["text"] = '{:02}'.format(time_ss)

        # Work完了時のアクション
        if self.status == self.STATUS_WORK_END:
            self.pause_time = 0
            if self.flash_count == 0:
                self.set_window_active()
            #     winsound.PlaySound("Clock-Alarm05.wav",
            #                        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            self.flash_count += 1
            if self.flash_count % 2 == 1:
                self.set_background_colour('red')
            else:
                self.set_background_colour('systemMenu')
            # if self.flash_count >= 15:
            #     winsound.PlaySound(None, winsound.SND_ASYNC)
            if self.flash_count >= 40:
                self.status = self.STATUS_STOP

        # Break完了時のアクション
        if self.status == self.STATUS_BREAK_END:
            self.pause_time = 0
            if self.flash_count == 0:
                self.set_window_active()
            #     winsound.PlaySound("Clock-Alarm05.wav",
            #                        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            self.flash_count += 1
            if self.flash_count % 2 == 1:
                self.set_background_colour('spring green')
            else:
                self.set_background_colour('systemMenu')
            # if self.flash_count >= 10:
                # winsound.PlaySound(None, winsound.SND_ASYNC)
            if self.flash_count >= 40:
                self.status = self.STATUS_STOP

    def evt_button_work_start(self, event=None):
        """「work_start」ボタンが押された時の処理
        """
        # ショートカットで起動した場合の回避
        if self.button_work_start["state"] == tkinter.DISABLED:
            return -1

        if self.status == self.STATUS_WORK_PAUSE:
            self.pause_time += time.time() - self.pause_time_buf
        else:
            self.base_time = time.time() + 25*60
            self.pause_time = 0
            self.pause_time_buf = 0
        self.set_background_colour('systemMenu')
        # winsound.PlaySound(None, winsound.SND_ASYNC)
        self.button_break_start["state"] = tkinter.DISABLED
        self.status = self.STATUS_WORK

    def evt_button_break_start(self, event=None):
        """「break_start」ボタンが押された時の処理
        """
        # ショートカットで起動した場合の回避
        if self.button_break_start["state"] == tkinter.DISABLED:
            return -1

        if self.status == self.STATUS_BREAK_PAUSE:
            self.pause_time += time.time() - self.pause_time_buf
        else:
            self.base_time = time.time() + 5*60
            self.pause_time = 0
            self.pause_time_buf = 0

        self.set_background_colour('systemMenu')
        # winsound.PlaySound(None, winsound.SND_ASYNC)
        self.button_work_start["state"] = tkinter.DISABLED
        self.status = self.STATUS_BREAK

    def evt_button_pause(self):
        """「pause」ボタンが押された時の処理
        """
        if not (self.status == self.STATUS_WORK_PAUSE or self.status == self.STATUS_BREAK_PAUSE):
            self.pause_time_buf = time.time()

        if self.status == self.STATUS_WORK:
            self.status = self.STATUS_WORK_PAUSE
        elif self.status == self.STATUS_BREAK:
            self.status = self.STATUS_BREAK_PAUSE

    def evt_button_stop(self):
        """「stop」ボタンが押された時の処理
        """
        # winsound.PlaySound(None, winsound.SND_ASYNC)
        self.base_time = time.time()
        self.pause_time = 0
        self.pause_time_buf = 0

        self.button_work_start['state'] = tkinter.NORMAL
        self.button_break_start['state'] = tkinter.NORMAL
        self.set_background_colour('systemMenu')

        self.status = self.STATUS_STOP


root = tkinter.Tk()
app = Application(master=root)
app.mainloop()
