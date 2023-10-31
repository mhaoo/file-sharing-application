import socket
import threading
import _tkinter
import mysql.connector
import select
import os
import shlex

HOST = "127.0.0.1"
PORT = 1000
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

SIGNUP = "signup"
LOGIN = 'login'
LOGOUT = "logout"
FETCH = 'fetch'

######### login/ sign up #################
def logIn(user, password,client):
    client.sendall(str(LOGIN).encode(FORMAT))
    #send username and password to server
    client.sendall(user.encode(FORMAT))
    client.recv(1024)
    client.sendall(password.encode(FORMAT))
    accepted = client.recv(1024).decode(FORMAT)
    return accepted
    


def signUp(user,password,client):
    client.sendall(str(SIGNUP).encode(FORMAT))
    #send username and password to server
    client.sendall(user.encode(FORMAT))
    client.recv(1024)
    client.sendall(password.encode(FORMAT))
    accepted = client.recv(1024).decode(FORMAT)
    return accepted

######### tạo repo #################
def createLocalRepo(folder, path):
    if not os.path.exists(folder):
        os.mkdir(folder)
        path_to_repository = os.path.abspath("repository")
        client.send(path_to_repository.encode(FORMAT))
        print(f'Local repository đã được tạo tại đường dẫn: {path}')
    else:
        print(f'Đường dẫn {path} đã tồn tại repository, hãy thử đường dẫn khác.')

#####################  fetch <filename> <username>    ##########################
def fetch_(filename, username):
    client.sendall(str(FETCH).encode(FORMAT))
    client.sendall(username.encode(FORMAT))
    client.recv(1024)
    adr_IP = client.recv(1024).decode(format)
    if(adr_IP == '-1'):
        print(f'{username} mat ket noi')
        return
###############################################



######### ket noi #############
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("CLIENT SIDE")
client.connect( (HOST, PORT) )
print("client address:",client.getsockname())
############ main ############

while True:
    print("1.Login")
    print("2.Sign up")
    select = input('nhap lua chon:')
    if(select == '1'):
        print("username:")
        user = input()
        print("password:")
        password = input()
        check = logIn(user, password,client)
        if(check == '1'):
            print('Đăng nhập thành công!')
            break
        else:
            print('Đăng nhập thất bại!')
    elif(select == '2'):
        print("username:")
        user = input()
        print("password:")
        password = input()
        check = signUp(user, password,client)
        if(check == '1'):
            print('Đăng ký thành công!')
            print('Hãy dùng lệnh "create repository <path>" để tạo local repository')
            while True:
                command = input()
                if command.startswith("create repository "):
                    args = shlex.split(command)
                    if len(args) >= 3:
                        path = os.path.join("repository", args[2])
                        createLocalRepo("repository", args[2])
                        break
                    else:
                        print('Lệnh không hợp lệ. Sử dụng lệnh "create repository <path>"')
                else:
                    print('Lệnh không hợp lệ. Sử dụng lệnh "create repository <path>"')
            break
        else:
            print('Đăng ký thất bại!')
########## chuc nang ##############
while True:
    functions = input()
    if(functions == 'logout'):
        client.sendall(str(LOGOUT).encode(FORMAT))
        break
    elif(functions[:9] == 'findOwner'):
        hostname = functions[10:]
    elif(functions[:5] == 'fetch'):
        result = functions.split()
        username = result[2]
        filename = result[1]
        fetch_(filename, username)


print('end')
client.close()
