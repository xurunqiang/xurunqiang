import os
import time
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk


class App:
    def __init__(self, master):
        self.master = master
        master.title("AI助力农作物病害虫识别系统")
        self.time = 0
        self.img_w = 525
        self.img_h = 400

        # 所需加载的模型目录
        self.path = 'yolov8n.pt'
        # 加载预训练模型
        self.model = YOLO(self.path, task='detect')

        # 创建一个 Canvas 控件用于显示分界线和视频
        self.canvas0 = tk.Canvas(master, bg="black")
        self.canvas0.place(x=0, y=50, width=2000, height=5)  # 设置 Canvas 的位置和大小

        # 在 Canvas 上绘制一条水平分界线，模拟标题栏下方的分界线
        self.draw_separator(self.canvas0)

        # 初始化 Canvas 控件并作为类的属性
        self.canvas = tk.Canvas(master, bg="white")
        self.canvas.place(x=28, y=98, width=self.img_w + 12, height=self.img_h + 12)  # 设置 Canvas 的位置和大小
        # 在 Canvas 上绘制一个黑色空心框
        self.canvas.create_rectangle(0, 0, self.img_w + 12, self.img_h + 12,
                                outline="black", width=10, fill='')

        # 初始化 Canvas 控件并作为类的属性
        self.canvas1 = tk.Canvas(master, bg="lightblue")
        self.canvas1.place(x=580, y=98, width=(self.img_w + 12)//1.36, height=(self.img_h + 12)//2)  # 设置 Canvas 的位置和大小
        # 在 Canvas 上绘制一个黑色空心框
        self.canvas1.create_rectangle(2, 2, (self.img_w + 12)//1.36 - 2, (self.img_h + 12)//2 - 2,
                                     outline="black", width=2, fill='')

        # 初始化 Canvas 控件并作为类的属性
        self.canvas2 = tk.Canvas(self.master, bg="orange")
        self.canvas2.place(x=580, y=310, width=(self.img_w + 12) // 1.36,
                           height=(self.img_h + 12) // 1.48)  # 设置 Canvas 的位置和大小
        # 在 Canvas 上绘制一个黑色空心框
        self.canvas2.create_rectangle(2, 2, (self.img_w + 12) // 1.36 - 2, (self.img_h + 12) // 1.48 - 2,
                                      outline="black", width=2, fill='')
        self.num = 1
        # 初始化 Canvas 控件并作为类的属性
        self.canvas3 = tk.Canvas(self.master, bg="white")
        self.canvas3.place(x=590, y=370, width=(self.img_w + 12) // 1.45,
                           height=(self.img_h + 12) // 2.1)  # 设置 Canvas 的位置和大小

        # 创建 Frame 控件作为 Canvas 的孩子，用于放置其他控件
        self.frame1 = tk.Frame(self.canvas3, bg="white")
        self.frame2 = tk.Frame(self.canvas3, bg="white")
        self.canvas3.create_window((80, 0), window=self.frame1, anchor="nw")
        self.canvas3.create_window((0, 0), window=self.frame2, anchor="nw")

        # 创建 Scrollbar 控件
        self.scrollbar = tk.Scrollbar(self.canvas3, orient="vertical", command=self.canvas3.yview)
        self.scrollbar.pack(side="right", fill="y")

        tk.Label(self.canvas2, text="       序号      ", height=2, bg='lightgray').place(x=10, y=25)
        tk.Label(self.canvas2, text="                               文件地址                            ",
                 height=2).place(x=90, y=25)

        # 假定有一些文件路径
        self.file_paths = []  # 初始化为空列表

        # 创建一个 Listbox 用于显示文件路径
        self.listbox = tk.Listbox(self.frame1, width=40, height=11, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox1 = tk.Listbox(self.frame2, width=11, height=11, yscrollcommand=self.scrollbar.set)
        self.listbox1.pack(side="top", fill="both", expand=True)

        # 将 Scrollbar 的命令绑定到两个 Listbox
        self.scrollbar.config(command=self.yview)

        # 绑定 Listbox 的点击事件
        self.listbox.bind('<Double-Button-1>', self.on_listbox_select)

        # 设置初始字体大小
        self.font_size = 12

        # 创建一个标签
        self.main_label = tk.Label(master, text="AI助力农作物病害虫识别系统", font=("Arial", 30), bg="lightgreen")
        self.main_label.pack()

        # 创建一个标签
        self.label = tk.Label(master, text="实时画面", font=(self.get_font()), bg="lightgreen")
        self.label.place(x=256, y=65)
        # 创建一个标签
        self.label1 = tk.Label(master, text="识别结果", font=("Helvetica", 12), bg="lightgreen")
        self.label1.place(x=590, y=90)
        # 创建一个标签
        self.label3 = tk.Label(master, text="识别结果信息", font=("Helvetica", 12), bg="lightgreen")
        self.label3.place(x=590, y=310)
        # 创建一个标签
        self.label2 = tk.Label(master, text="      作者: Remoteness  微信: Remoteness2003", font=("Times", 20),
                               bg="lightgreen")
        self.label2.pack(side="bottom", fill="x", pady=35)

        self.frame3 = tk.Frame(self.canvas1, bg="white")
        self.canvas1.create_window((120, 170), window=self.frame3, anchor="nw")
        # 创建一个标签
        self.label4 = tk.Label(self.frame3, text="耗时：{}s".format(self.time), font=("Times", 18),
                               bg="lightblue", fg='red')
        self.label4.pack(side="bottom", fill="x")

        self.frame4 = tk.Frame(self.canvas1, bg="blue")
        self.canvas1.create_window((20, 20), window=self.frame4, anchor="nw")

        # 创建 Scrollbar 控件
        self.scrollbar2 = tk.Scrollbar(self.frame4, orient="vertical", command=self.canvas1.yview)
        self.scrollbar2.pack(side="right", fill="y")

        # 创建一个 Listbox 用于显示文件路径
        self.listbox2 = tk.Listbox(self.frame4, width=48, height=8, yscrollcommand=self.scrollbar2.set)
        self.listbox2.pack(side="left", fill="both", expand=True)

        # 将 Scrollbar 的命令绑定到 Listbox
        self.scrollbar2.config(command=self.listbox2.yview)

        # 创建一个按钮，点击时会打开文件对话框
        self.button1_img = ImageTk.PhotoImage(Image.open(r"tubiao\i2.png"))
        self.browse_button1 = tk.Button(master, command=self.load_image,
                                        bg="lightgreen", image=self.button1_img)
        self.browse_button1.place(x=30, y=520)

        # 创建一个按钮，点击时会打开文件对话框
        self.button2_img = ImageTk.PhotoImage(Image.open(r"tubiao\v2.png"))
        self.browse_button2 = tk.Button(master, command=self.toggle_video,
                                        bg="lightgreen", image=self.button2_img)
        self.browse_button2.place(x=165, y=520)

        # 创建一个按钮，点击时会打开文件对话框
        self.button3_img = ImageTk.PhotoImage(Image.open(r"tubiao\vi2.png"))
        self.browse_button3 = tk.Button(master, command=self.open_video,
                                        bg="lightgreen", image=self.button3_img)
        self.browse_button3.place(x=300, y=520)

        # 创建一个按钮，点击时会打开文件对话框
        self.button4_img = ImageTk.PhotoImage(Image.open(r"tubiao\f2.png"))
        self.browse_button4 = tk.Button(master, command=self.choose_folder,
                                        bg="lightgreen", image=self.button4_img)
        self.browse_button4.place(x=435, y=520)

        # 创建一个按钮，点击时会打开文件对话框
        self.button5_img = ImageTk.PhotoImage(Image.open(r"tubiao\zuozhe.png"))
        self.browse_button5 = tk.Button(master, bg="lightgreen", image=self.button5_img)
        self.browse_button5.place(x=190, y=600)

        # 初始化图片标签
        self.image_label = tk.Label(master)
        self.image_label.place(x=32, y=102)

        # 初始化 OpenCV 的视频捕获对象        self.cap = cv2.VideoCapture(0)
        self.cap1 = None
        self.cap = None

        # 用于存储 PIL Image 对象
        self.current_image = None

        self.is_video_open = False  # 添加标志变量
        self.folder_paths = []
        # 绑定窗口大小改变事件
        master.bind("<Configure>", self.on_resize)

    def yview(self, *args):
        # 更新两个 Listbox 的滚动状态
        self.listbox.yview(*args)
        self.listbox1.yview(*args)

    def choose_folder(self):
        if not self.is_video_open:
            # 弹出文件夹选择对话框
            folder_path = filedialog.askdirectory(title="Select Folder")
            if folder_path:
                # 列出文件夹中的所有文件
                for file_name in os.listdir(folder_path):
                    # 检查文件扩展名，判断是否是图片或视频文件
                    if file_name.lower().endswith(('.jpg', '.png', '.gif')):
                        # 构建完整的文件路径
                        full_file_name = os.path.join(folder_path, file_name)
                        self.folder_paths.append(full_file_name)
            self.load_folder()
        else:
            messagebox.showerror("Error", "摄像未关闭！")

    def load_folder(self,):
        if len(self.folder_paths) != 0:
            file = self.folder_paths[0]
            self.folder_paths.pop(0)
            self.cap1 = None
            # 使用 PIL 打开图片
            try:
                # 检测图片
                time1 = time.time()
                results = self.model(file)
                time2 = time.time()
                self.time = time2 - time1
                res = results[0].plot()
                cls = results[0].boxes.cls
                names = results[0].names
                self.result_show(cls, names)
                # 转换颜色空间从 BGR 到 RGB
                frame = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.img_w, self.img_h))
                img = Image.fromarray(frame)
                # 将 PIL Image 转换为 Tkinter 的 PhotoImage
                tk_img = ImageTk.PhotoImage(img)
                # 添加文件到 Listbox 和 self.file_paths
                self.listbox.insert(tk.END, file)
                self.listbox1.insert(tk.END, '         ' + str(self.num))
                self.num += 1
                self.file_paths.append(file)  # 添加文件路径到列表
                # 更新 Label 控件的图片
                self.image_label.config(image=tk_img)
                self.image_label.image = tk_img  # 必须保持对图片对象的引用
                self.label4.config(text="耗时：{:.4f}s".format(self.time))
                # 安排下一次播放
                self.master.after(30, self.load_folder)
            except Exception as e:
                print(f"Error loading image: {e}")
        else:
            messagebox.showinfo("Info", "文件读取完毕！")


    def on_listbox_select(self, event):
        # 获取 Listbox 中选中的项的索引
        selection = self.listbox.curselection()
        if selection:
            index = int(selection[0])
            # 打开文件
            file_path = self.file_paths[index]
            # 获取文件的扩展名（不包括点）
            extension = os.path.splitext(file_path)[1][1:].lower()
            if extension in ['jpg', 'png', 'gif']:  # 可以添加更多图片格式
                self.load_image(file_path)
            else:
                self.open_video(file_path)

    def open_video(self, file_path=None):
        if not self.is_video_open:
            if file_path is None:
                # 弹出文件对话框，让用户选择视频文件
                file_path = filedialog.askopenfilename(
                    title="Open Video",
                    filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
                )
                if file_path:
                    # 添加文件到 Listbox 和 self.file_paths
                    self.listbox.insert(tk.END, file_path)
                    self.listbox1.insert(tk.END, '         ' + str(self.num))
                    self.num += 1
                    self.file_paths.append(file_path)  # 添加文件路径到列表
            if file_path:
                try:
                    # 初始化视频捕获对象
                    self.cap1 = cv2.VideoCapture(file_path)
                    self.play_video()
                except Exception as e:
                    messagebox.showerror("Error", f"无法打开视频文件: {e}")
        else:
            messagebox.showerror("Error", "摄像未关闭！")

    def play_video(self):
        if self.cap1 is not None and self.cap1.isOpened():
            ret, frame = self.cap1.read()
            if ret:
                # 转换颜色空间从 BGR 到 RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                time1 = time.time()
                results = self.model(frame)
                time2 = time.time()
                self.time = time2 - time1
                res = results[0].plot()
                cls = results[0].boxes.cls
                names = results[0].names
                self.result_show(cls, names)
                frame = cv2.resize(res, (self.img_w, self.img_h))
                # 转换图片为 PIL Image 对象
                img = Image.fromarray(frame)
                self.current_image = ImageTk.PhotoImage(img)
                # 更新 Label 控件的图片
                self.image_label.config(image=self.current_image)
                self.image_label.image = self.current_image  # 保持对图片对象的引用
                self.label4.config(text="耗时：{:.4f}s".format(self.time))
                # 安排下一次播放
                self.master.after(10, self.play_video)
            else:
                messagebox.showinfo("Info", "视频播放结束。")
                self.close_video()

    def close_video(self):
        if self.cap1 is not None:
            self.cap1.release()  # 释放视频捕获对象

    def draw_separator(self, canvas):
        # 假定分界线的高度为 1，宽度与 Canvas 一致
        separator_line = canvas.create_line(0, 1, canvas.winfo_width(), 1, fill="black")
        # 由于 create_line 返回的是一个标识符，您可以使用它来后续操作线条，如删除
        self.separator_id = separator_line

    def toggle_video(self):
        if not self.is_video_open:
            # 如果摄像头未打开，则打开摄像头并开始播放
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
            self.is_video_open = True
            self.load_video()
        else:
            # 如果摄像头已打开，则停止播放并关闭摄像头
            self.stop_video()
            self.is_video_open = False
            self.cap = None  # 重置 self.cap 为 None
            # 清空图片
            empty_image = Image.new("RGB", (self.img_w, self.img_h), color="white")
            # 将空图片转换为 Tkinter 的 PhotoImage 对象
            self.current_image = ImageTk.PhotoImage(empty_image)
            # 更新 Label 控件的图片
            self.image_label.config(image=self.current_image)
            self.image_label.image = self.current_image  # 保持对图片对象的引用

    def load_video(self):
        if self.is_video_open:
            self.cap1 = None
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 转换颜色空间从 BGR 到 RGB
                time1 = time.time()
                results = self.model(frame)
                time2 = time.time()
                self.time = time2 - time1
                res = results[0].plot()
                cls = results[0].boxes.cls
                names = results[0].names
                self.result_show(cls, names)
                frame = cv2.resize(res, (self.img_w, self.img_h))
                # 转换图片为 PIL Image 对象
                pil_image = Image.fromarray(frame)
                self.current_image = ImageTk.PhotoImage(pil_image)

                # 更新 Label 控件的图片
                self.image_label.config(image=self.current_image)
                self.image_label.image = self.current_image  # 必须保持对图片对象的引用
                self.label4.config(text="耗时：{:.4f}s".format(self.time))
                # 安排下一次播放
                self.master.after(30, self.load_video)
            else:
                messagebox.showerror("Error", "无法读取视频帧。")
                self.stop_video()

    def stop_video(self):
        if self.cap is not None:
            self.cap.release()  # 释放视频捕获对象

    def get_font(self):
        # 根据窗口大小计算字体大小
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        base_size = 10  # 基础字体大小
        scale_factor = min(width, height) / 400  # 假设窗口在400x400时字体大小为base_size
        size = int(base_size * scale_factor)
        return "Helvetica", size  # 返回字体族和大小

    def on_resize(self, event):
        # 窗口大小改变时，更新标签的字体大小
        self.label.config(font=self.get_font())

    def load_image(self, file_path=None):
        if not self.is_video_open:
            if file_path is None:
                # 弹出文件对话框，让用户选择图片文件
                file_path = filedialog.askopenfilename(
                    title="Select Image",
                    filetypes=[("Image files", "*.jpg *.png *.gif"), ("All files", "*.*")]
                )
                if file_path:
                    # 添加文件到 Listbox 和 self.file_paths
                    self.listbox.insert(tk.END, file_path)
                    self.listbox1.insert(tk.END, '         ' + str(self.num))
                    self.num += 1
                    self.file_paths.append(file_path)  # 添加文件路径到列表
            if file_path:
                self.cap1 = None
                # 使用 PIL 打开图片
                try:
                    # 检测图片
                    time1 = time.time()
                    results = self.model(file_path)
                    time2 = time.time()
                    self.time = time2 - time1
                    res = results[0].plot()
                    cls = results[0].boxes.cls
                    names = results[0].names
                    self.result_show(cls, names)
                    # 转换颜色空间从 BGR 到 RGB
                    frame = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (self.img_w, self.img_h))
                    img = Image.fromarray(frame)
                    # 将 PIL Image 转换为 Tkinter 的 PhotoImage
                    tk_img = ImageTk.PhotoImage(img)

                    # 更新 Label 控件的图片
                    self.image_label.config(image=tk_img)
                    self.image_label.image = tk_img  # 必须保持对图片对象的引用
                    self.label4.config(text="耗时：{:.4f}s".format(self.time))
                except Exception as e:
                    print(f"Error loading image: {e}")
        else:
            messagebox.showerror("Error", "摄像未关闭！")

    def result_show(self, cls, names):
        # 初始化一个字典来存储每个类别的数量
        category_counts = {}
        # 清空listbox2的内容
        self.listbox2.delete(0, tk.END)
        # 检查类别索引是否在字典的键中，如果是，则增加计数
        for i in cls:
            category_name = names[int(i)]
            if category_name in category_counts:
                category_counts[category_name] += 1
            else:
                category_counts.setdefault(category_name, 1)

        for j in category_counts:
            self.listbox2.insert(tk.END, str(j) + ':' + str(category_counts[j]))
# 创建主窗口
root = tk.Tk()
root.geometry("1000x700")  # 可以设置初始窗口大小
root.configure(bg="lightgreen")  # 更改整个窗口的背景颜色为浅蓝色
app = App(root)

# 运行事件循环
root.mainloop()

