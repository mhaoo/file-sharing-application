import socket
import threading
import _tkinter
import select
import os
import shlex
from shutil import copy2
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk 
import threading
from tkinter import filedialog
#HOST = "192.168.137.1"  ###### IP cua server #######
HOST = "localhost"

PORT = 10001
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

SIGNUP = "signup"
LOGIN = 'login'
LOGOUT = "logout"
FETCH = 'fetch'
USER = " "

#########################
LARGE_FONT = ("verdana", 13,"bold")
ADMIN_USERNAME = 'admin'
ADMIN_PSWD = 'database'
#########################
class sharing_file_app(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.frames = {}
        for F in (StartPage, HomePage, CreateRepository):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)

    def showFrame(self, container):
        frame = self.frames[container]
        if container== HomePage:
            self.geometry("600x520")
        elif container == CreateRepository:
            self.geometry("500x200")
        else:
            self.geometry("500x200")
        frame.tkraise()    
    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            try:
                option = 'quit'
                client.sendall(option.encode(FORMAT))
            except:
                pass
        
        
    def logIn(self,curFrame,sck):
        global USER
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()
           
            
            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 
            USER = user
            #notice server for starting log in
            option = LOGIN
            sck.sendall(option.encode(FORMAT))

            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("server responded")

            
            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "1":
                self.showFrame(HomePage)    
                curFrame.entry_pswd.delete(0, tk.END)
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "user already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")



    def signUp(self,curFrame, sck):
        global USER
        try:
        
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()
            
            
            if pswd == "":
                curFrame.label_notice["text"] = "password cannot be empty"
                return 
            USER = user
            #notice server for starting log in
            option = SIGNUP
            sck.sendall(option.encode(FORMAT))
            
            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("server responded")

            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)



            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == '1':
                self.showFrame(CreateRepository)
                curFrame.entry_pswd.delete(0, tk.END)
                curFrame.label_notice["text"] = ""
            else:
                curFrame.label_notice["text"] = "username already exists"

        except:
            curFrame.label_notice["text"] = "Error 404: Server is not responding"
            print("404")

    def create_repository(self,curFrame, sck):
        folder_path = filedialog.askdirectory(title="Select Folder")
        folder_path  = folder_path.replace( "/","\\")
        sck.sendall(folder_path.encode(FORMAT))
        sck.recv(1024)
        self.showFrame(HomePage)     

    def log_out(self,curFrame, sck):
            try:
                sck.sendall("logout".encode(FORMAT))
                accepted = sck.recv(1024).decode(FORMAT)
                if accepted == "True":
                    self.showFrame(StartPage)
                    curFrame.label_notice["text"] = ""
            except:
                  curFrame.label_notice["text"] = "Error: Server is not responding"
        
    
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        controller.title("File-Sharing Application")
        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_user = tk.Label(self, text="username ",fg='#20639b',bg="bisque2",font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',bg="bisque2",font='verdana 10 ')

        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        button_sign = tk.Button(self,text="SIGN UP",bg="#20639b",fg='floral white', command=lambda: controller.signUp(self, client)) 
        button_sign.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        button_sign.pack()   

class CreateRepository(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        controller.title("File-Sharing Application")
        label_title = tk.Label(self, text="CREATE REPOSITORY", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_title.pack()
        choose_folder_button = tk.Button(self, text="Chọn Thư Mục", command=lambda: controller.create_repository(self, client))
        choose_folder_button.pack(pady=20)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        controller.title("File-Sharing Application")
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        
        self.entry_search = tk.Entry(self)
        button_search = tk.Button(self, text="Search for File",bg="#20639b",fg='#f5ea54', command=self.findOwner)
        button_listall = tk.Button(self, text="List All",bg="#20639b",fg='#f5ea54', command=self.list_all)
        button_public = tk.Button(self, text="Publish", bg="#20639b",fg='#f5ea54', command=self.publish)  #####
        button_back = tk.Button(self, text="Log Out",bg="#20639b",fg='#f5ea54', command=lambda: controller.log_out(self,client))
        label_title.pack(pady=10)
        button_back.configure(width=10)
        self.entry_search.pack()
        button_search.configure(width=10) 
        button_listall.configure(width=10) 
        button_public.configure(width=10)
        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.pack(pady=4)

        button_search.pack(pady=3)
        button_listall.pack(pady=3)
        button_public.pack(pady=3)
        button_back.pack(pady=3)
        
        self.frame_list = tk.Frame(self, bg="steelblue1")
        self.tree = ttk.Treeview(self.frame_list)
        self.tree["column"] = ("Filename", "Username", "Status")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Filename", anchor='c', width=200)
        self.tree.column("Username", anchor='c', width=200)
        self.tree.column("Status", anchor='c', width=100)
        self.tree.heading("0", text="", anchor='c')
        self.tree.heading("Filename", text="Filename", anchor='c')
        self.tree.heading("Username", text="Username", anchor='c')
        self.tree.heading("Status", text="Status", anchor='c')
        scrollbar = ttk.Scrollbar(self.frame_list, orient=tk.VERTICAL, command= self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(pady=3)
        delete_button = tk.Button(self.frame_list, text="Download", command= self.func_fetch)
        delete_button.pack()
    
        self.label_notice_2 = tk.Label(self, text="", bg="bisque2" )
        self.label_notice_2.pack(pady=1)


        self.frame_publish = tk.Frame(self, bg="bisque2")
        
        self.label_repo = tk.Label(self.frame_publish, text = 'My Local Repository: ', wraplength=600)
        self.label_repo.pack(pady=3)

        select_button = tk.Button(self.frame_publish, text="Select File",bg="#20639b",fg='#f5ea54', command= self.select_file)
        select_button.configure(width=10) 
        select_button.pack(pady=3)

        self.file_path_label = tk.Label(self.frame_publish, text="Selected File: ", wraplength=600)
        
        self.file_new_name = tk.Label(self.frame_publish, text="New name",fg='#20639b',bg="bisque2", wraplength=600)

        self.new_name = tk.Entry(self.frame_publish)
     
        self.add_button = tk.Button(self.frame_publish, text="Add",bg="#20639b",fg='#f5ea54', command= self.add_button_)
        self.add_button.configure(width=10) 


    def list_all(self):
        global USER
        try:
            self.tree.delete(*self.tree.get_children())
            client.sendall('list_all'.encode(FORMAT))
            client.recv(1024)
            client.sendall(USER.encode(FORMAT))
            
            # self.frame_list_all.pack_forget()
            check = 0
            while True:
                msg = client.recv(1024).decode(FORMAT)
                client.sendall('list_all'.encode(FORMAT))
                words = client.recv(1024).decode(FORMAT)
                if msg == 'kethuc':
                    break
                else:
                    check = check + 1
                    filename = msg.split()
                    for word in filename:
                        row_data = (word, words, "")
                        self.tree.insert("", "end", values=row_data)
            if(check == 0):
                self.label_notice["text"] = "There are no user sharing the file"
                
            else:
                self.frame_publish.pack_forget()
                self.frame_list.pack()

        except:
                self.label_notice["text"] = "Error"
            



    def add_button_(self, path_seclect):
        global USER
        file_name = self.new_name.get()
        if file_name == "":
            self.label_notice["text"] = "Fields cannot be empty"
            return 
        
        client.sendall(str("publish" + " " + file_name + " " + USER).encode(FORMAT))
       
        result = client.recv(1024).decode(FORMAT)

        copy2(path_seclect, result)
        self.label_notice["text"] = "Completed!"
        self.frame_publish.pack_forget()

        self.file_path_label.config(text="Selected File: ")
        self.new_name.delete(0, tk.END)
        self.add_button.pack_forget()
        self.new_name.pack_forget()
        self.file_new_name.pack_forget()
        self.file_path_label.pack_forget()

    
        


    def select_file(self):
        file_path = filedialog.askopenfilename()
        self.file_path_label.config(text="Selected File: " + file_path)
        self.add_button.config(command=lambda: self.add_button_(str(file_path)))
        self.file_path_label.pack(pady=4)
        self.file_new_name.pack(pady=(3, 0))
        self.new_name.pack(pady=4)
        self.add_button.pack(pady=4)
        
        


    def publish(self):
        tep = self.path_repo()
        repo = 'My Local Repository: ' +  tep
        self.label_repo.config(text = repo)

        self.frame_list.pack_forget()
        self.frame_publish.pack()
        
        
    def path_repo(self):
        global USER
        option = 'path_repo' + ' ' + USER
        client.sendall(option.encode(FORMAT))
        path = client.recv(1024).decode(FORMAT)
        client.sendall(path.encode(FORMAT))
        replaced_string = path.replace('\\\\', '\\')
        return replaced_string

   
    def func_fetch(self):
        selected_items = self.tree.selection()
        if selected_items:
            for item in selected_items:
                filename, username, status = self.tree.item(item)['values']

            client.sendall(str(FETCH).encode(FORMAT))
            client.sendall(username.encode(FORMAT))
            client.recv(1024)
            adr_IP = client.recv(1024).decode(FORMAT)
            client.sendall('thanhcong'.encode(FORMAT))
            if(adr_IP == '-1'):
                print(f'{username} mat ket noi')
                self.label_notice["text"] = f'{username} not online'
                return
            path_des = client.recv(1024).decode(FORMAT)
            client.sendall(USER.encode(FORMAT))
            path_my = client.recv(1024).decode(FORMAT)
            client.sendall('thanhcong'.encode(FORMAT))
            path_des = path_des + '\\\\' 
            path_des = path_des + str(filename)
            path_my = path_my + '\\\\'
            path_my = path_my + str(filename)

            sock = socket.socket()
            print ("Socket created successfully.")
            port = 8000
            sock.connect((adr_IP, port))
            print('Connection Established.')
            sock.sendall(path_des.encode(FORMAT))
            sock.recv(1024)
            with open(path_my, 'wb') as file:
        
             while True:
                data = sock.recv(1024)
                if not data:
                    break
                file.write(data)
               
                sock.send('ok'.encode(FORMAT))
            print('File has been received successfully.')

            self.tree.set(item, "Status", "Complete!")

            file.close()
            sock.close()
            print('Connection Closed.')
      
        else:
            print("No item selected.")
            self.label_notice["text"] = "No item selected."




    def findOwner(self):
        global USER
        try:
            self.tree.delete(*self.tree.get_children())
            self.label_notice["text"] = ""
            filename = self.entry_search.get()   
            if (filename == ""):
                self.label_notice["text"] = "Field cannot be empty"
                return
            option = "findOwner " + str(filename)
            client.sendall(option.encode(FORMAT))
            client.recv(1024)
            client.sendall(USER.encode(FORMAT))
        
            msg = client.recv(1024).decode(FORMAT)
            client.sendall('thanh cong'.encode(FORMAT))
            
            if(msg == "Not user"):
                self.label_notice["text"] = f"There are no user sharing the file {filename}"
                return
            words = msg.split()
            
            for word in words:
                row_data = (filename, words, "")
                self.tree.insert("", "end", values=row_data)
        
            self.frame_publish.pack_forget()
            self.frame_list.pack()
                
        except:
                 self.label_notice["text"] = "Error"


############# luong client - client #########   
def handle_client(conn,addr):
    print('Connected with ', addr)
    data = conn.recv(1024).decode(FORMAT)
    conn.sendall('thanhcong'.encode(FORMAT))
    
    with open(data, 'rb') as file:
      
        # file_size = os.path.getsize(data)
        # conn.send(str(file_size).encode(FORMAT))
    
        while True:
            data = file.read(1024)
            if not data:
                break
            conn.sendall(data)
            conn.recv(1024).decode(FORMAT)
        print('File has been sent successfully.')
    
    conn.close()
    file.close()
    print('File has been transferred successfully.')

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def clien_cnn_client():
    sock = socket.socket()
    print ("Socket created successfully.")
    port = 8000
    IP_user = get_ip()
    #IP_user = "127.0.0.1"
    sock.bind((IP_user, port))
    sock.listen()
    print('Socket is listening...')
    while True:
        try:
            conn, addr = sock.accept()
            thread_client = threading.Thread(target=handle_client, args=(conn,addr))
            thread_client.daemon = False
            thread_client.start()
        except:
            print("Error")
            sock.close()

    





client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("CLIENT SIDE")
client.connect( (HOST, PORT) )
print("client address:",client.getsockname())



thread_server = threading.Thread(target = clien_cnn_client)
thread_server.daemon = False
thread_server.start()


app = sharing_file_app()

#main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()
    print('end')