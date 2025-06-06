from customtkinter import*
from socket import*
from threading import*
from PIL import Image
import base64
import io

class RegisterWindow(CTk):

    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title("Реєстрація")
        self.username = None
        self.label = CTkLabel(self, text="Вхід в LogiTalk",
                              font=("Arial", 20, "bold"))
        self.label.pack(pady=40)

        self.name_entry = CTkEntry(self, placeholder_text="Введіть ім'я")
        self.name_entry.pack()
        self.host_entry = CTkEntry(self, placeholder_text="Введіть хост сервера")
        self.host_entry.pack()
        self.port_entry = CTkEntry(self, placeholder_text="Введіть порт сервера")
        self.port_entry.pack()

        self.btn_submit = CTkButton(self, text="Зареєструватися" , command = self.start_chat)
        self.btn_submit.pack(pady=5)

    def start_chat(self):
        self.username = self.name_entry.get()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host_entry.get(), int(self.port_entry.get())))
            hello = f"TEXT@{self.username}[SYSTEM]{self.username} приєднався до чату\n"
            self.sock.send(hello.encode())

            self.destroy()

            win = MainWindow(self.sock, self.username)
            win.mainloop()

        # threading.Thread(target=self.recv_message, daemon=True).start()
        except:
            print("Не вдалося підключитися до сервера")

class MainWindow(CTk):
    def __init__(self , sock , username):
        super().__init__()
        self.sock = sock
        self.username = username
        self.geometry('400x300')

        self.frame = CTkFrame (self , fg_color = 'light blue' , width=200 , height = self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width = 0)
        self.frame.place(x=0 ,  y=0)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame, text='Введіть налаштування')
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack()

        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0 , y=0)

        self.chat_text = CTkTextbox(self , state = "disabled")
        self.chat_text.place(x=0 , y=30)

        self.massage_input = CTkEntry(self , placeholder_text = "Введіть повідомлення")
        self.massage_input.place(x=0 , y=250)

        #self.btn_safe = CTkButton(self.frame,text = "Зберегти" command=self.save_name)
        #self.btn_safe.pack()
        self.send_btn = CTkButton(self , text='▶️' , width=30 , command = self.send_massage)
        self.send_btn.place(x=200 , y=250)

        #self.adaptive_ui()

        self.label_theme = CTkOptionMenu(self.frame , values = ["Темна" , "Світла"] , command = self.change_theme)
        self.label_theme.pack(side = "bottom" , pady =20 )
        self.theme = None
        self.username = "Roma"
        try:
            self.sock = socket(AF_INET , SOCK_STREAM)
            self.sock.conect(('localhost' , 8080))
            hello = f"TEXT@{self.username}@[SYSTEM]{self.username}приєднався до чату! \n"
            self.sock.send(hello.encode())
        except:
            self.add_massage("Не вдалося підключитися до сервера")

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += 5
            self.frame.configure(width=self.frame_width,height=self.winfo_height())
            if self.frame_width >=30:
                self.btn.configure(width = self.frame_width , text = '◀️')
            
        if self.is_show_menu:
            self.after(10, self.show_menu)

    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= 5
            self.frame.configure(width=self.frame_width,height=self.winfo_height())
            if self.frame_width >=30:
                self.btn.configure(width = self.frame_width , text = '▶️')
            
        if not self.is_show_menu:
            self.after(10, self.close_menu)

    # def adaptive_ui(self):
    #     self.chat_text.configure(width=self.winfo_width()-self.frame.winfo_width(),height=self.winfo_height()-self.message_input.winfo_height()-30)
    #     self.chat_text.place(x=self.frame.winfo_width())
    #     self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.send_btn.winfo_width())
    #     self.message_input.place(x=self.frame.winfo_width(),y=self.winfo_height()-self.send_btn.winfo_height())
    #     self.send_btn.place(x=self.winfo_width()-self.send_btn.winfo_width(),y=self.winfo_height()-self.send_btn.winfo_height())
    #     self.after(20,self.adaptive_ui)

   

    def change_theme(self , value):
        if value == "Темна":
            set_appearance_mode("Dark")
        else:
            set_appearance_mode("Light")
        
    def add_massage(self , text):
        self.chat_text.configure(state = "normal")
        self.chat_text.insert(END , text + "\n")
        self.chat_text.configure(state = "disable")

    def send_massage(self):
        massage = self.massage_input.get()
        #self.username = self.entry.get()
        if massage:
            self.add_massage(f"{self.username}:{massage}")
            data = f"TEXT@{self.username}@{massage}\n"
            try:
                self.sock.senddall(data.encode())
            except:
                pass
            self.massage_input.delete(0 , END)


    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break

        self.sock.close()
    def handle_line(self , line):
        if not line:
            return

        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")

            elif msg_type == "IMAGE":
                if len(parts) >= 4:
                    author = parts[1]
                    filename = parts[2]
                    b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img, size=(300, 300))
                    self.add_message(f"{author}{filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка зображення: {e}")

        else:
            self.add_message(line)

    def save_name(self):
        new_name = self.entry.get()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")
reg_win = RegisterWindow()
reg_win.mainloop()