import socket
import time
import _thread

# TODO: podzielić protocol na od serwera i od klienta

protocol = {
    "req": "REQUEST",                               # serwer
    "exit": "EXIT",                                 # klient
    "accept": "ACCEPT",                             # klient
    "accepted": "ACCEPTED",                         # serwer
    "connect": "CONNECT",                           # klient
    "connectFeedback": "CONNECT_OK",                # serwer
    "disconnect": "DISCONNECT",                     # klient
    "welcome": "WELCOME",                           # serwer
    # "newUser": "NEW_USER",                        # serwer
    "getUsers": "GET_ONLINE",                       # klient
    "usersList": "ONLINE_LIST",                     # serwer
    "userDisconnected": "INTERLOCUTOR_EXIT",        # serwer
    "disconnected": "DISCONNECT_SUCCESS",           # serwer
    "serverError": "SERVER_ERROR",                  # serwer
    "notConnected": "NO_FRIENDS?",                  # serwer
    "receivedMessage": "MESSAGE",                   # serwer
    "send": "SEND",                                 # klient
    "userLeft": "USER_LEFT"                         # serwer
}

end = False
interlocutorId = -1

def listen(s):
    global end
    global interlocutorId
    while True:
        time.sleep(0.1)
        data = s.recv(1024)

        message = str(data.decode('utf-8'))

        # print(message)

        if message.startswith(protocol["req"]):
            interlocutorId = int(message[(len(protocol["req"]) + 1):])
            print("Użytkownik o ID", interlocutorId, "chce z Tobą rozmawiać. "
                    "Napisz '" +  str(protocol["accept"]) + ' ' + str(interlocutorId) + "' żeby zaakceptować połączenie.")
        elif message.startswith(protocol["accepted"]):
            interlocutorId = int(message[(len(protocol["accepted"]) + 1):])
            # print("Użytkownik o ID", interlocutorId, "zaakceptował połączenie. "
            #         "Możecie teraz ze sobą rozmawiać.")
            print("Połączenie z użytkownikiem o ID", interlocutorId, "zostało nawiązane. "
                    "Możecie teraz ze sobą rozmawiać.")
        elif message.startswith(protocol["welcome"]):
            words = message.split(' ', 2)
            print(words)
            print("Twoje id:", words[1], "\nLista obecnych użytkowników:", words[2])
        else:
            print(message)
        if end:
            break
    print("listen wyszedł z while")

def send(s):
    global end
    while True:
        time.sleep(0.1)
        # message = protocol["send"] + ' ' + input()            # TODO: naprawić, żeby wysyłało SEND tylko gdy nie zaczyna się od słowa kluczowego protkołu
        message = input()

        if message == protocol["exit"]:
            end = True
            break

        s.send(bytes(message, "utf-8"))
    print("send wyszedł z while")

def Main():
    host = '192.168.100.7'
    port = 50000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    _thread.start_new_thread(send, (s,))
    _thread.start_new_thread(listen, (s,))

    print("Witaj, wybierz któregoś użytkownika z listy wpisując '" + protocol["connect"] + " <id>' "
            "żeby poprosić o rozpoczęcie rozmowy.\n"
            "Aby rozłączyć się z tym użytkownikiem napisz '" + protocol["disconnect"] + "'.")

    while True:
        time.sleep(2)
        if  end:
            break

    print("main wyszedł z while True :00")
    s.close()


if __name__ == '__main__':
    Main()