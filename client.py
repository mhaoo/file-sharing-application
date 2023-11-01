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
USER = ''

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
def createLocalRepo(pathRepo, path):
    if not os.path.exists(pathRepo):
        os.mkdir(pathRepo)
        path_to_repository = os.path.abspath(pathRepo)
        client.send(path_to_repository.encode(FORMAT))
        print(f'Local repository đã được tạo tại đường dẫn: {path}')
    else:
        print(f'Đường dẫn {path} đã tồn tại repository, hãy thử đường dẫn khác.')

######### publish ###########
# def publish_file(src_path, dest_filename):
#     if not os.path.isfile(src_path):
#         print(f"File '{src_path}' không tồn tại hoặc sai đường dẫn.")
#         return

#     client.sendall(f"publish {src_path} {dest_filename}".encode(FORMAT))
#     response = client.recv(1024).decode(FORMAT)
#     if response == "OK":
#         print(f"File '{src_path}' published as '{dest_filename}' in the repository.")
#     else:
#         print(f"Failed to publish file.")

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
        USER = user
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
        USER = user
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
                        path = os.path.join(args[2], "repository")
                        createLocalRepo(path, args[2])
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
    elif(functions[:5] == 'fetch'):
        result = functions.split()
        username = result[2]
        filename = result[1]
        fetch_(filename, username)
    elif functions.startswith("findOwner"):
        filename = functions[10:]
        client.sendall(str("findOwner " + filename).encode(FORMAT))

        result_str = client.recv(1024).decode(FORMAT)
        if (result_str == "Not user"):
            print(result_str)
        else:
            result = result_str.split('\n')
            for item in result:
                print(item) 
    elif functions.startswith("publish"):
        args = functions.split()
        if len(args) == 3:
            src_path = args[1]
            dest_filename = args[2]
            client.sendall(str("publish" + " " + src_path + " " + dest_filename + " " + USER).encode(FORMAT))
            result = client.recv(1024).decode(FORMAT)
            if result == "OK":
                print(f'Đã thêm file {dest_filename} vào local repository')
            else:
                print(f'Thêm file {dest_filename} vào local repository thất bại')
        else:
            print('Lệnh không hợp lệ. Sử dụng lệnh "publish <path-to-filename1> <filename2>"')

print('end')
client.close()
