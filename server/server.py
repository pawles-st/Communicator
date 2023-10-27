import socket
from _thread import *

clients = {}
protocol = {
    "req": "REQUEST",                               # serwer
    "accept": "ACCEPT",                             # klient
    "accepted": "ACCEPTED",                         # serwer
    "connect": "CONNECT",                           # klient
    "connectFeedback": "CONNECT_OK",                # serwer
    "disconnect": "DISCONNECT",                     # klient
    "welcome": "WELCOME",                           # serwer
    "newUser": "NEW_USER",                          # serwer
    "getUsers": "GET_ONLINE",                       # klient
    "usersList": "ONLINE_LIST",                     # serwer
    "userDisconnected": "INTERLOCUTOR_EXIT",        # serwer
    "disconnected": "DISCONNECT_SUCCESS",           # serwer
    "serverError": "SERVER_ERROR",                  # serwer
    "notConnected": "NO_FRIENDS?",                  # serwer
    "receivedMessage": "MESSAGE",                   # serwer
    "userLeft": "USER_LEFT"                         # serwer
}


def on_new_client(clientsocket, addr, id):
    try:
        # clientsocket.send(bytes("WELCOME " + str(id) + '\n', "utf-8"))
        # clientsocket.send(bytes("ONLINE_LIST" + str(list(clients.keys())), "utf-8"))
        clientsocket.send(bytes(protocol["welcome"] + ' ' + str(id) + ' ' + str(list(clients.keys())), "utf-8"))
        for client in clients:
            if clients[client]["connected"] == -1 and client != id:
                clients[client]["socket"].send(bytes(protocol["newUser"] + ' ' + str(id), "utf-8"))
        while True:
            msg = clientsocket.recv(1024)
            print(str(id) + ': ' + msg.decode("utf-8"))
            if msg.decode() == protocol["disconnect"] and clients[id]["connected"] != -1:
                clients[clients[id]["connected"]]["socket"].send(bytes(protocol["userLeft"], "utf-8"))
                clients[clients[id]["connected"]]["connected"] = -1
                clients[id]["connected"] = -1
                clientsocket.send(bytes(protocol["disconnected"], "utf-8"))
            elif msg.decode() == protocol["getUsers"]:
                clientsocket.send(bytes(protocol["usersList"] + ' ' + str(list(clients.keys())), "utf-8"))
            elif msg.decode().startswith(protocol["connect"]):
                split = msg.decode("utf-8").split()
                if len(split) != 2:
                    clientsocket.send(bytes(protocol["serverError"], "utf-8"))
                else:
                    try:
                        requested_id = int(split[1])
                        connected_socket = clients[requested_id]["socket"]
                        clients[id]["requests"].append(requested_id)
                        clientsocket.send(bytes(protocol["connectFeedback"], "utf-8"))
                        connected_socket.send(bytes(protocol["req"] + ' ' + str(id), "utf-8"))
                    except Exception as e:
                        print(e)
                        clientsocket.send(bytes(protocol["serverError"], "utf-8"))
            elif msg.decode().startswith(protocol["accept"]):
                split = msg.decode("utf-8").split()
                if len(split) != 2:
                    clientsocket.send(bytes(protocol["serverError"], "utf-8"))
                else:
                    try:
                        accepted_id = int(split[1])
                        if clients[accepted_id]["requests"].index(id) >= 0:
                            clients[accepted_id]["requests"] = []
                            clients[id]["requests"] = []
                            clients[id]["connected"] = accepted_id
                            clients[accepted_id]["connected"] = id
                            clients[accepted_id]["socket"].send(bytes(protocol["accepted"] + ' ' + str(id), "utf-8"))
                            clients[id]["socket"].send(bytes(protocol["accepted"] + ' ' + str(accepted_id), "utf-8"))
                    except Exception as e:
                        print(e)
                        clientsocket.send(bytes(protocol["serverError"], "utf-8"))
            elif clients[id]["connected"] == -1:
                clientsocket.send(bytes(protocol["notConnected"], "utf-8"))
            else:
                clients[clients[id]["connected"]]["socket"].send(bytes(protocol["receivedMessage"] + ' ' + str(id) + " " + msg.decode("utf-8"), "utf-8"))
    except ConnectionResetError:
        print("bro disconnected :skull: ", addr, " mial id: ", id)
        print("uzytkownik", id, addr, "rozlaczyl sie")
        for client in clients:
            print(client)
            if clients[client]["connected"] == -1 and client != id:
                clients[client]["socket"].send(bytes(protocol["userLeft"] + ' ' + str(id), "utf-8"))
        if clients[id]["connected"] != -1:
            clients[clients[id]["connected"]]["socket"].send(bytes(protocol["userDisconnected"], "utf-8"))
            clients[clients[id]["connected"]]["connected"] = -1
        clients.pop(id)

        print("pozostali uzytkownicy online:", list(clients.keys()))
    clientsocket.close()


s = socket.socket()
host = socket.gethostname()
port = 50000

print('Serwer dziala!')

s.bind((host, port))
s.listen(5)

current_client_id = 0

while True:
    c, addr = s.accept()
    print('Nowe polaczenie z', addr, 'przydzielam ID', current_client_id)
    start_new_thread(on_new_client, (c, addr, current_client_id))
    clients[current_client_id] = ({"socket": c, "requests": [], "connected": -1})
    current_client_id += 1

# TODO: dodac wszedzie nulle i supportowac nulle u klienta (jak kilka wiadomosci przyjdzie jednoczesnie to klient moze je zinterpretowac jako jedna, przydalby sie jakis symbol oznaczajacy koniec wiadomosci; wiadomosc moze byc potencjalnie dluzsza niz te 1024 co pobieramy, brak nulla oznacza ze trzeba czytac dalej zeby wiadomosc byla skompletowana, ewentualnie odgornie narzucic limit dlugosci)
# TODO: zadbac o to zeby slowa kluczowe w protokole nie byly prefiksami innych
# TODO: potencjalnie zrobic ze jak 1: CONNECT 0 i 0: CONNECT 1 to CONNECT 1 dziala jak ACCEPT 1 (w faktycznym projekcie raczej bez znaczenia)
# TODO: przemyslec co z wysylaniem komend podczas rozmowy (lub nie przemyslec bo w faktycznym projekcie nie ma to znaczenia)
