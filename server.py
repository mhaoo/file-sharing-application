import socket
import threading
import _tkinter
import mysql.connector

### mysql
db = mysql.connector.connect(user = 'root', password = 'superhao2001', host = 'localhost', database = "socket_mmt")
print(db)
cursor = db.cursor()

SIGNUP = "signup"
LOGIN = 'login'
LOGOUT = "logout"


##
host = "127.0.0.1" #loopback
port = 1000 
format = "utf8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
###---------------------Login/SignUp----------------###

## dang ki tai khoan
def Insert_New_Account(user,password):
    sql = "INSERT INTO TaiKhoan(username, password) VALUES (%s, %s)"
    val = (user, password)
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
def Insert_ds_user(adr, username, path):
    sql = "INSERT INTO ds_user(adr_IP, username ,file_name, path) VALUES (%s, %s, %s, %s)"
    val = (str(adr), username, "", path)
    cursor.execute(sql, val)
    db.commit()

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

## chek login
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
    print("username:--" + user +"--")

    conn.sendall(user.encode(format))

    pswd = conn.recv(1024).decode(format)
    print("password:--" + pswd +"--")

    accepted = check_clientSignUp(user)
    print("accept:", accepted)

    conn.sendall(str(accepted).encode(format)) #new

    if accepted == 1:
        Insert_New_Account(user, pswd)
        # add client sign up address to live account
        Ad.append(str(addr))
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)

        path_to_repository = conn.recv(1024).decode(format)
        conn.sendall(path_to_repository.encode(format))
        parse_check = str(addr)
        parse_check = parse_check[2:]
        parse = parse_check.find("'")
        parse_check = parse_check[:parse]
        print(parse_check)
        Insert_ds_user(str(parse_check), str(user), str(path_to_repository))

    print("end-SignUp()")
    return accepted

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

######## check conn############
def check_connections(user):
    if(not Live_Account):
        print(user ,' not connect')
    else:     
        for row in Live_Account:
            parse= row.find("-")
            parse_check=row[(parse+1):]
            if parse_check== user:
                print(user, ' connect') 
            else:
                print(user ,' not connect')

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
                    conn.sendall(str(check).encode(format))
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
                if(option == LOGOUT):
                    Remove_LiveAccount(conn,addr)
                    break


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
            check_connections(host_name)

       # elif(server_command[:8] == 'discover '):

            
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