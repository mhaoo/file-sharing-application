import socket
import threading
import _tkinter
import mysql.connector
import os
import shlex
from shutil import copy2

### mysql
db = mysql.connector.connect(user = 'root', password = 'superhao2001', host = 'localhost', database = "socket_mmt")
print(db)
cursor = db.cursor()

SIGNUP = "signup"
LOGIN = 'login'
LOGOUT = "logout"
FETCH = 'fetch'

##
host = "127.0.0.1" #loopback
port = 1000 
format = "utf8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
###---------------------Login/SignUp----------------###

## dang ki tai khoan
def Insert_New_Account(user,password):
    sql = "INSERT INTO TaiKhoan(username, password, addr_IP, path) VALUES (%s, %s, %s, %s)"
    val = (user, password, "", "")
    cursor.execute(sql, val)
    db.commit() 

#### kiem tra ten dang ki co bi trung
def check_clientSignUp(username):
    if username == "admin":
        return 0
    cursor.execute("select username from TaiKhoan")
    for row in cursor:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            return 0
    return 1

#### Lưu đường dẫn tới thư mục local repo vào database
def Update_repoPath(username, password, addr, path):
    sql = "UPDATE TaiKhoan SET path = %s, addr_IP = %s WHERE username = %s AND password = %s"
    val = (path, addr, username, password)
    cursor.execute(sql, val)
    db.commit()

#### Copy file từ client sang local repository
def publishFile(srcPath, destFileName, userName):
    cursor.execute("SELECT path FROM TaiKhoan WHERE username = %s", (userName,))
    result = cursor.fetchone()
    path_value = result[0]
    destPath = os.path.join(path_value, destFileName)
    copy2(srcPath, destPath)
    sql = "INSERT INTO ds_user(username, file_name) VALUES (%s, %s)"
    val = (userName, destFileName)
    cursor.execute(sql, val)
    db.commit()
    print(f'{userName} đã thêm file {destFileName} vào local repository')
    conn.sendall("OK".encode(format))

Live_Account=[]
ID=[]
Ad=[]
## kiem tra ten dang nhap 
def Check_LiveAccount(username):
    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        if parse_check== username:
            return False
    return True
### log out
def Remove_LiveAccount(conn,addr):
    for row in Live_Account:
        parse= row.find("-")
        parse_check=row[:parse]
        if parse_check== str(addr):
            parse= row.find("-")
            Ad.remove(parse_check)
            username= row[(parse+1):]
            ID.remove(username)
            Live_Account.remove(row)

## check login
def check_clientLogIn(username, password):
    if not Check_LiveAccount(username):
        return 0
    if username == "admin" and password == "database":
        return 1

    cursor.execute("SELECT username FROM TaiKhoan")
    result = cursor.fetchall()

    for row in result:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            cursor.execute("select password from TaiKhoan  where username = %s",(username,))
            parse= str(cursor.fetchone())
            parse_check =parse[2:]
            parse= parse_check.find("'")
            parse_check= parse_check[:parse]
            if password== parse_check:
                return 1
    return 0
## signUp
def clientSignUp(conn, addr):

    user = conn.recv(1024).decode(format)
    print("username: --" + user + "--")

    conn.sendall(user.encode(format))

    pswd = conn.recv(1024).decode(format)
    print("password: --" + pswd + "--")

    accepted = check_clientSignUp(user)
    print("accept:", accepted)

    conn.sendall(str(accepted).encode(format))

    if accepted == 1:
        Insert_New_Account(user, pswd)
        # add client sign up address to live account
        Ad.append(str(addr))
        ID.append(user)
        account = str(Ad[Ad.__len__() - 1]) + "-" + str(ID[ID.__len__() - 1])
        Live_Account.append(account)

        path_to_repository = conn.recv(1024).decode(format)
        conn.sendall(path_to_repository.encode(format))
        parse_check = str(addr)
        parse_check = parse_check[2:]
        parse = parse_check.find("'")
        parse_check = parse_check[:parse]
        print(parse_check)
        Update_repoPath(str(user), str(pswd), str(parse_check), str(path_to_repository))

    print("end-SignUp()")
    return accepted

def new_func(user):
    return user
##login
def clientLogIn(conn):

    user = conn.recv(1024).decode(format)
    print("username:--" + user +"--")
    conn.sendall(user.encode(format))
    pswd = conn.recv(1024).decode(format)
    print("password:--" + pswd +"--")
    accepted = check_clientLogIn(user, pswd)
    if accepted == 1:
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)
    print("accept:", accepted)
    print("end-logIn()")
    return accepted

########   discover ####
def discover(user):
    cursor.execute("select file_name from ds_user  where username = %s",(user,))
    result = cursor.fetchall()
    if len(result) == 0:
        print('Khong tim thay hostname!')
    else:
        print(user, ":", result)

def sendOwnerInform(conn,addr):
    username = conn.recv(1024).decode(format)
    conn.sendall(username.encode(format))
    check_live = Check_LiveAccount(username)
    if check_live == False:
        cursor.execute("select adr_IP from ds_user  where username = %s",(username,))
        parse= str(cursor.fetchone())
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        conn.sendall(parse_check.encode(format))
    else:
        conn.sendall('-1'.encode(format))

###---------------list------------------###

def listUser():
    cursor.execute("select username from taikhoan")
    result = cursor.fetchall()
    if len(result) == 0:
        print('Khong tim thay hostname!')
    else:
        for row in result:
            print(row[0])  

def listUserO ():
    for row in Live_Account:
        ip, id= row.split("-")
        print(id)

def listUserA ():
    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        print(parse_check)
        discover(parse_check)

###-------------get-----------_###
def getUserInform (user):
    check = Check_LiveAccount(user)
    if check == False:
        for row in Live_Account:
            ip, id= row.split("-")
            if id== user: 
                print(ip)
    else:
        print(user ,' not connect')

def getOwner (filename):
    cursor.execute("select username from ds_user  where file_name = %s",  (filename,))
    result=cursor.fetchall()
    if not result:
        conn.sendall("Not user".encode(format))
    else:
        
        result_str = "\n".join([str(row[0]) for row in result]) 
        conn.sendall(result_str.encode(format)) 


# ######## check conn############
# def check_connections(user):
#     if(not Live_Account):
#         print(user ,' not connect')
#     else:     
#         for row in Live_Account:
#             parse= row.find("-")
#             parse_check=row[(parse+1):]
#             if parse_check== user:
#                 print(user, ' connect') 
#             else:
#                 print(user ,' not connect')

####--------------xu li-------####
def handleClient(conn, addr):
    print("connection:",conn.getsockname())
    ################ login /signUp #############
    while True:
       try:
            option = conn.recv(1024).decode(format)
            if option == LOGIN:
                Ad.append(str(addr))
                check = clientLogIn(conn)
                if(check == 1):
                    conn.sendall(str(check).encode(format))
                    print('Dang nhap thanh cong!')
                    print("")
                    break
                else:
                    conn.sendall(str(check).encode(format))
                    print('Dang nhap that bai!')
                    print("")
            elif option == SIGNUP:
                check = clientSignUp(conn, addr)
                if(check == 1):
                    print('Dang ki thanh cong!')
                    print("")
                    break
                else:
                    conn.sendall(str(check).encode(format))
                    print('Dang ki that bai!')
                    print("")
       except:
            print(conn.getsockname(), "not connection")
            Remove_LiveAccount(conn,addr)
            conn.close()
            return
     ########### chuc nang #################
    while True:
            try:
                option = conn.recv(1024).decode(format)
                parts = option.split(" ")
                if(option == LOGOUT):
                    Remove_LiveAccount(conn,addr)
                    break
                elif(option == FETCH):
                    sendOwnerInform(conn,addr)
                elif option.startswith("findOwner"):
                    filename = option[10:]
                    getOwner(filename)
                elif len(parts) == 4 and parts[0] == "publish":
                    src_path = parts[1]
                    dest_filename = parts[2]
                    username = parts[3]
                    publishFile(src_path, dest_filename, username)
            except:
                print(conn.getsockname(), "not connection")
                Remove_LiveAccount(conn,addr)
                return

    print("end-thread:", conn.getsockname())
    conn.close()


def server_command_thread():
    while True:
        server_command = input()
        if (server_command[:4] == 'ping'):
            host_name = server_command[5:]
            check = Check_LiveAccount(host_name)
            if check == False:
                 print(host_name, ' connect') 
            else:
                 print(host_name ,' not connect')

        elif(server_command[:8] == 'discover'):
            host_name = server_command[9:]
            discover(host_name)
        elif(server_command[:9] == 'listUserO'):
            listUserO()
        elif(server_command[:9] == 'listUserA'):
            listUserA()
            
        elif(server_command[:8] == 'listUser'):
            listUser()
        elif(server_command[:12] == 'getUserInform'):
            username = server_command[13:]
            getUserInform(username)
        elif(server_command[:8] == 'getOwner'):
            filename = server_command[9:]
            getOwner(filename)


            
###----------------main------------------###


s.bind((host, port))
s.listen()
print("SERVER SIDE")
print("server:", host, port)
print("Waiting for Client")
thread_server = threading.Thread(target=server_command_thread)
thread_server.daemon = False
thread_server.start()
while True:
    try:
        conn, addr = s.accept()
        thread_client = threading.Thread(target=handleClient, args=(conn,addr))
        thread_client.daemon = False
        thread_client.start()
    except:
         print("Error")
    

s.close()