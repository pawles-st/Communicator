import socket
from _thread import *
from utils import protocol
from logger import Logger
from message_handler import MessageHandler
clients = {}

def on_new_client(clientsocket, addr, id):
    global current_client_id
    try:
        # not logged in yet
        logger = Logger()
        while id == -1:
            msg = clientsocket.recv(1024)
            if len(msg.decode("utf-8")) != 0:
                print(str(id) + ': ' + msg.decode("utf-8"))
                result = logger.handle(msg.decode("utf-8"))
                if result[0] == "SEND" and result[1] == -1:
                    clientsocket.send(bytes(result[2], "utf-8"))
                elif result[0] == "WELCOME":
                    id = result[2]
                    if id in clients:
                        clients[id]["socket"].append(clientsocket)
                    else:
                        clients[id] = ({"socket": [clientsocket], "requests": [], "connected": -1})
                    for client in clients:
                        if clients[client]["connected"] == -1 and client != id:
                            for sock in clients[client]["socket"]:
                                sock.send(bytes(protocol["fromServer"]["newUser"] + ' ' + str(id), "utf-8"))
                    clientsocket.send(bytes(protocol["fromServer"]["welcome"] + ' ' + result[2] + ' ' + str(list(clients.keys())), "utf-8"))
                else:
                    clientsocket.send(bytes(protocol["fromServer"]["serverError"], "utf-8"))
        msghandler = MessageHandler()
        # id != -1 - logged in
        while True:
            msg = clientsocket.recv(1024)
            if len(msg.decode("utf-8")) != 0:
                print(str(id) + ': ' + msg.decode("utf-8"))
                result = msghandler.handle(msg.decode("utf-8"), id)
                if result[0] == "SEND":
                    if result[1] == -1:
                        clientsocket.send(bytes(result[2], "utf-8"))
                    else:
                        if result[1] in clients:
                            for sock in clients[result[1]]["socket"]:
                                sock.send(bytes(protocol["fromServer"]["receivedMessage"] + " " + id + " " + result[2], "utf-8"))
                elif result[0] == "GET_ONLINE":
                    clientsocket.send(bytes(protocol["fromServer"]["usersList"] + ' ' + str(list(clients.keys())), "utf-8"))

    except Exception as e:
        print(e)
        print("uzytkownik", id, addr, "rozlaczyl sie")
        for client in clients:
            if id != -1 and clients[client]["connected"] == -1 and client != id:
                for sock in clients[client]["socket"]:
                    sock.send(bytes(protocol["fromServer"]["userLeft"] + ' ' + str(id), "utf-8"))
        if id != -1 and clients[id]["connected"] != -1:
            for sock in clients[clients[id]["connected"]]["socket"]:
                sock.send(bytes(protocol["fromServer"]["userDisconnected"], "utf-8"))
            clients[clients[id]["connected"]]["connected"] = -1
        if id != -1:
            clients[id]["socket"].remove(clientsocket)
            if len(clients[id]["socket"]) == 0:
                clients.pop(id)

        print("pozostali uzytkownicy online:", list(clients.keys()))
    clientsocket.close()


if __name__ == '__main__':
    s = socket.socket()
    host = socket.gethostname()
    host = socket.gethostbyname(host)
    port = 50005
    print(host)

    print('Serwer dziala!')

    s.bind((host, port))
    s.listen(5)

    current_client_id = 0

    while True:
        c, addr = s.accept()
        print('Nowe polaczenie z', addr, 'przydzielam ID', -1)
        start_new_thread(on_new_client, (c, addr, -1))

    # TODO: dodac wszedzie nulle i supportowac nulle u klienta (jak kilka wiadomosci przyjdzie jednoczesnie to klient
    #  moze je zinterpretowac jako jedna, przydalby sie jakis symbol oznaczajacy koniec wiadomosci; wiadomosc moze byc potencjalnie dluzsza niz
    #  te 1024 co pobieramy, brak nulla oznacza ze trzeba czytac dalej zeby wiadomosc byla skompletowana, ewentualnie odgornie narzucic limit dlugosci)
    # TODO: zadbac o to zeby slowa kluczowe w protokole nie byly prefiksami innych
    # TODO: pewnie zrobic jakas maszyne stanow
    # TODO: w paru miejscach zrobilem string z palca wpisany a nie z protokołu, pewnie wartoby to zmienić