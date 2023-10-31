import socket
import threading
import _tkinter
import mysql.connector
import select
import os
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


#####################  fetch <filename> <username>    ##########################
def fetch_(filename, username):
    client.sendall(str(FETCH).encode(FORMAT))
    client.sendall(username.encode(FORMAT))
    client.recv(1024)
    adr_IP = client.recv(1024).decode(format)
    if(adr_IP == '-1'):
        print(f'{username} mat ket noi')
        return
    


# Create local repository
def create_local_repository(path):
    try:
        os.mkdir(path)
        print(f'Repository created at {path}')
        client.sendall(str(path).encode(FORMAT))
        client.recv(1024)
    except FileExistsError:
        print(f'Repository already exists at {path}')
    except OSError as e:
        print(f'Error creating repository: {str(e)}')

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
            print('Dang nhap thanh cong!')
            break
        else:
            print('Dang nhap that bai!')
    elif(select == '2'):
        print("username:")
        user = input()
        print("password:")
        password = input()
        check = signUp(user, password,client)
        if(check == '1'):
            print('Hay dung lenh create repository <path> de tao local repository.') 
            path = input('Nhap duong dan cho local repository: ')
            create_local_repository(path)
            print('Dang ki thanh cong!')
            break
        else:
            print('Dang ki that bai!')
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
