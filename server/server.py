import socket
from _thread import *

clients = {}
protocol = {
    "fromServer": {
        "req": "REQUEST",                               # serwer
        "accepted": "ACCEPTED",                         # serwer
        "connectFeedback": "CONNECT_OK",                # serwer
        "connectionEstablished": "CONNECTION_ESTABLISHED", # serwer
        "welcome": "WELCOME",                           # serwer
        "newUser": "NEW_USER",                          # serwer
        "usersList": "ONLINE_LIST",                     # serwer
        "userDisconnected": "INTERLOCUTOR_EXIT",        # serwer
        "disconnected": "DISCONNECT_SUCCESS",           # serwer
        "serverError": "SERVER_ERROR",                  # serwer
        "notConnected": "NO_FRIENDS?",                  # serwer
        "receivedMessage": "MESSAGE",                   # serwer
        "userLeft": "USER_LEFT",                        # serwer
        "alreadyLoggedIn": "ALREADY_LOGGED_IN",         # serwer
        "userNotFound": "USER_NOT_FOUND",               # serwer
        "wrongPassword": "WRONG_PASSWORD",              # serwer
        "usernameTaken": "USERNAME_TAKEN",
        "notLoggedIn": "NOT_LOGGED_IN",
        "registerSuccess": "REGISTER_SUCCESS",
    },
    "fromClient": {
        "send": "SEND",                                 # klient
        "accept": "ACCEPT",                             # klient
        "connect": "CONNECT",                           # klient
        "disconnect": "DISCONNECT",                     # klient
        "getUsers": "GET_ONLINE",                       # klient
        "login": "LOGIN",
        "register": "REGISTER",
        "sendKey:": "SEND_KEY",
    }

}


def on_new_client(clientsocket, addr, id):
    global current_client_id
    try:
        # clientsocket.send(bytes("WELCOME " + str(id) + '\n', "utf-8"))
        # clientsocket.send(bytes("ONLINE_LIST" + str(list(clients.keys())), "utf-8"))
        #clientsocket.send(bytes(protocol["fromServer"]["connectionEstablished"], "utf-8")) # TODO: not needed?
        while True:
            msg = clientsocket.recv(1024)
            print(str(id) + ': ' + msg.decode("utf-8"))
            if msg.decode().startswith(protocol["fromClient"]["login"]):
                if id != -1:
                    clientsocket.send(bytes(protocol["fromServer"]["alreadyLoggedIn"], "utf-8"))
                else:
                    credentials = msg.decode().split()
                    if len(credentials) != 3:
                        clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
                    else:
                        users_db = open("./users_pseudo_db", "r")
                        user_exists = False
                        for line in users_db:
                            words = line.split()
                            if words[1] == credentials[1]:
                                user_exists = True
                                if words[2] == credentials[2]:
                                    id = int(words[0])
                                    if id in clients:
                                        clients[id]["socket"].append(clientsocket)
                                    else:
                                        clients[id] = ({"socket": [clientsocket], "requests": [], "connected": -1})
                                    clientsocket.send(bytes(protocol["fromServer"]["welcome"] + ' ' + words[0] + ' ' + words[1] + ' ' + str(list(clients.keys())), "utf-8"))
                                    for client in clients:
                                        if clients[client]["connected"] == -1 and client != id:
                                            for sock in clients[client]["socket"]:
                                                sock.send(bytes(protocol["fromServer"]["newUser"] + ' ' + str(id), "utf-8"))
                                    break
                                else:
                                    clientsocket.send(bytes(protocol["fromServer"]["wrongPassword"], "utf-8"))
                        if not user_exists:
                            clientsocket.send(bytes(protocol["fromServer"]["userNotFound"], "utf-8"))
                        users_db.close()
            elif msg.decode().startswith(protocol["fromClient"]["register"]):
                if id != -1:
                    clientsocket.send(bytes(protocol["fromServer"]["alreadyLoggedIn"], "utf-8"))
                else:
                    credentials = msg.decode().split()
                    if len(credentials) != 3:
                        clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
                    else:
                        users_db = open("./users_pseudo_db", "r")
                        user_exists = False
                        for line in users_db:
                            words = line.split()
                            if words[1] == credentials[1]:
                                user_exists = True
                        users_db.close()
                        if user_exists:
                            clientsocket.send(bytes(protocol["fromServer"]["usernameTaken"], "utf-8"))
                        else:
                            id = current_client_id
                            if id in clients:
                                clients[id]["socket"].append(clientsocket)
                            else:
                                clients[id] = ({"socket": [clientsocket], "requests": [], "connected": -1})
                            clientsocket.send(bytes(protocol["fromServer"]["registerSuccess"] + ' ' + str(id) + ' ' + credentials[1] + ' ' + str(list(clients.keys())), "utf-8"))
                            for client in clients:
                                if clients[client]["connected"] == -1 and client != id:
                                    for sock in clients[client]["socket"]:
                                        sock.send(bytes(protocol["fromServer"]["newUser"] + ' ' + str(id), "utf-8"))
                            #users_db = open("./users_pseudo_db", "a")
                            #users_db.write("\n" + str(current_client_id) + " " + credentials[1] + " " + credentials[2])
                            #users_db.close()
                            #current_client_id += 1
            elif id == -1:
                clientsocket.send(bytes(protocol["fromServer"]["notLoggedIn"], "utf-8"))
            elif msg.decode() == protocol["fromClient"]["disconnect"] and clients[id]["connected"] != -1:
                for sock in clients[clients[id]["connected"]]["socket"]:
                    sock.send(bytes(protocol["fromServer"]["userLeft"], "utf-8"))
                clients[clients[id]["connected"]]["connected"] = -1
                clients[id]["connected"] = -1
                clientsocket.send(bytes(protocol["fromServer"]["disconnected"], "utf-8"))
            elif msg.decode() == protocol["fromClient"]["getUsers"]:
                clientsocket.send(bytes(protocol["fromServer"]["usersList"] + ' ' + str(list(clients.keys())), "utf-8"))
            elif msg.decode().startswith(protocol["fromClient"]["connect"]):
                split = msg.decode("utf-8").split()
                if len(split) != 2:
                    clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
                else:
                    try:
                        requested_id = int(split[1])
                        clients[id]["requests"].append(requested_id)
                        clientsocket.send(bytes(protocol["fromServer"]["connectFeedback"], "utf-8"))
                        for sock in clients[requested_id]["socket"]:
                            sock.send(bytes(protocol["fromServer"]["req"] + ' ' + str(id), "utf-8"))
                    except Exception as e:
                        print(e)
                        clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
            elif msg.decode().startswith(protocol["fromClient"]["accept"]):
                split = msg.decode("utf-8").split()
                if len(split) != 2:
                    clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
                else:
                    try:
                        accepted_id = int(split[1])
                        if clients[accepted_id]["requests"].index(id) >= 0:
                            clients[accepted_id]["requests"] = []
                            clients[id]["requests"] = []
                            clients[id]["connected"] = accepted_id
                            clients[accepted_id]["connected"] = id
                            for sock in clients[accepted_id]["socket"]:
                                sock.send(bytes(protocol["fromServer"]["accepted"] + ' ' + str(id), "utf-8"))
                            for sock in clients[id]["socket"]:
                                sock.send(bytes(protocol["fromServer"]["accepted"] + ' ' + str(accepted_id), "utf-8"))
                    except Exception as e:
                        print(e)
                        clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
            elif clients[id]["connected"] == -1:
                clientsocket.send(bytes(protocol["fromServer"]["notConnected"], "utf-8"))
            else:
                for sock in clients[clients[id]["connected"]]["socket"]:
                    sock.send(bytes(protocol["fromServer"]["receivedMessage"] + ' ' + str(id) + " " + msg.decode("utf-8"), "utf-8"))
    #except ConnectionResetError:
    except Exception:
        print("uzytkownik", id, addr, "rozlaczyl sie")
        for client in clients:
            if clients[client]["connected"] == -1 and client != id:
                for sock in clients[client]["socket"]:
                    sock.send(bytes(protocol["fromServer"]["userLeft"] + ' ' + str(id), "utf-8"))
        if clients[id]["connected"] != -1:
            for sock in clients[clients[id]["connected"]]["socket"]:
                sock.send(bytes(protocol["fromServer"]["userDisconnected"], "utf-8"))
            clients[clients[id]["connected"]]["connected"] = -1
        if id != -1:
            clients[id]["socket"].remove(clientsocket)
            if len(clients[id]["socket"]) == 0:
                clients.pop(id)

        print("pozostali uzytkownicy online:", list(clients.keys()))
    clientsocket.close()


s = socket.socket()
host = socket.gethostname()
host = socket.gethostbyname(host)
port = 50005
print(host)

print('Serwer dziala!')

s.bind((host, port))
s.listen(5)

current_client_id = 0

users_db = open("./users_pseudo_db", "r")
last = ""
for line in users_db:
    last = line
if last != "":
    last = last.split(" ")
    current_client_id = int(last[0]) + 1
else:
    current_client_id = 0
users_db.close()

while True:
    c, addr = s.accept()
    print('Nowe polaczenie z', addr, 'przydzielam ID', -1)
    start_new_thread(on_new_client, (c, addr, -1))
    # clients[current_client_id] = ({"socket": c, "requests": [], "connected": -1})
    # current_client_id += 1

# TODO: dodac wszedzie nulle i supportowac nulle u klienta (jak kilka wiadomosci przyjdzie jednoczesnie to klient moze je zinterpretowac jako jedna, przydalby sie jakis symbol oznaczajacy koniec wiadomosci; wiadomosc moze byc potencjalnie dluzsza niz te 1024 co pobieramy, brak nulla oznacza ze trzeba czytac dalej zeby wiadomosc byla skompletowana, ewentualnie odgornie narzucic limit dlugosci)
# TODO: zadbac o to zeby slowa kluczowe w protokole nie byly prefiksami innych
# TODO: potencjalnie zrobic ze jak 1: CONNECT 0 i 0: CONNECT 1 to CONNECT 1 dziala jak ACCEPT 1 (w faktycznym projekcie raczej bez znaczenia)
# TODO: przemyslec co z wysylaniem komend podczas rozmowy (lub nie przemyslec bo w faktycznym projekcie nie ma to znaczenia)
# TODO: funkcja co imituje query?
# TODO: pewnie zrobic jakas maszyne stanow
