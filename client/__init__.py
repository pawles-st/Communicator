import socket
import time
import _thread
import bcrypt

from encryption import *

class ProtocolException(Exception):
    pass

SOCKET_RECEIVE_SIZE = 1024
KEY_FILEPATH = "private_key.pem"

# communication protocol
protocolFromServer = {
    "req": "REQUEST",                               # serwer
    "accepted": "ACCEPTED",                         # serwer
    "connectFeedback": "CONNECT_OK",                # serwer
    "connectionEstablished": "CONNECTION_ESTABLISHED",  # :(
    "welcome": "WELCOME",                           # serwer
    "newUser": "NEW_USER",                          # serwer
    "usersList": "ONLINE_LIST",                     # serwer
    "userDisconnected": "INTERLOCUTOR_EXIT",        # serwer
    "disconnected": "DISCONNECT_SUCCESS",           # serwer
    "serverError": "SERVER_ERROR",                  # serwer
    "notConnected": "NO_FRIENDS?",                  # serwer
    "receivedMessage": "MESSAGE",                   # serwer
    "userLeft": "USER_LEFT",                        # serwer
    "alreadyLoggedIn": "ALREADY_LOGGED_IN",
    "userNotFound": "USER_NOT_FOUND",
    "usernameTaken": "USERNAME_TAKEN",
    "registerSuccess": "REGISTER_SUCCESS",
}

protocolFromClient = {
    "send": "SEND",                                 # klient
    "exit": "EXIT",                                 # klient
    "accept": "ACCEPT",                             # klient
    "connect": "CONNECT",                           # klient
    "disconnect": "DISCONNECT",                     # klient
    "getUsers": "GET_ONLINE",                       # klient
    "login": "LOGIN",
    "register": "REGISTER",
    "sendKey:": "SEND_KEY",
}

end = False
interlocutorId = -1
userNick = ''

def listen(s):
    global end
    global interlocutorId
    while True:
        time.sleep(0.1)
        data = s.recv(SOCKET_RECEIVE_SIZE)

        message = str(data.decode('utf-8'))
        if message.startswith(protocolFromServer["req"]):
            interlocutorId = int(message[(len(protocolFromServer["req"]) + 1):])
            print("Użytkownik o ID", interlocutorId, "chce z Tobą rozmawiać. "
                    "Napisz '" +  str(protocolFromClient["accept"]) + ' ' + str(interlocutorId) + "' żeby zaakceptować połączenie.")
        elif message.startswith(protocolFromServer["accepted"]):
            interlocutorId = int(message[(len(protocolFromServer["accepted"]) + 1):])
            # print("Użytkownik o ID", interlocutorId, "zaakceptował połączenie. "
            #         "Możecie teraz ze sobą rozmawiać.")
            print("Połączenie z użytkownikiem o ID", interlocutorId, "zostało nawiązane. "
                    "Możecie teraz ze sobą rozmawiać.")
        elif message.startswith(protocolFromServer["welcome"]):
            words = message.split(' ', 3)
            # print(words)
            print(
                "Witaj,", words[2], "wybierz któregoś użytkownika z listy wpisując '" + protocolFromClient["connect"] + " <id>' "
                "żeby poprosić o rozpoczęcie rozmowy.\n"
                "Aby rozłączyć się z tym użytkownikiem napisz '" +
                protocolFromClient["disconnect"] + "'.")
            print("Twoje id:", words[1], "\nLista obecnych użytkowników:", words[3])
        elif message.startswith(protocolFromServer["connectionEstablished"]):
            print("Proszę się zalgować wpisując '" + protocolFromClient["login"] + " <nick> <hasło>'\n"
                    "lub zarejestrować wpisując '" + protocolFromClient["register"] + " <nick> <hasło>'")
        else:
            print(message)

        if end:
            break

    print("listen wyszedł z while")


def send(s):
    global end
    global userNick
    while True:
        time.sleep(0.1)
        # message = protocol["send"] + ' ' + input()            # TODO: naprawić, żeby wysyłało SEND tylko gdy nie zaczyna się od słowa kluczowego protkołu
        message = input()

        if message == protocolFromClient["exit"]:
            end = True
            break
        # elif message.startswith(protocolFromClient["login"]):
        #     words = message.split()
        #     userNick = words[1]
        s.send(bytes(message, "utf-8"))
    print("send wyszedł z while")


def authorise(s):
    
    # send requests to server until logged in or exits

    while True:

        # read the request and authorisation data and send it to server

        message = input()
        #req = message.split(" ")
        #if req[0] == protocolFromClient["login"]:
        #    bcrypt

        s.send(bytes(message, "utf-8"))

        # read server response

        response = s.recv(SOCKET_RECEIVE_SIZE)
        response = response.decode("utf-8").split(" ")
        status = response[0]
        data = response[1:]

        # if registration is successful, create RSA keys and send them to server
        # if login is successful, return login data
        # otherwise, print the corresponding error message

        if status == protocolFromServer["registerSuccess"]: # successful register
            
            private_key = create_keys()
            
        elif status == protocolFromServer["welcome"]: # successful login
            return data
        elif status == protocolFromServer["usernameTaken"]:
            print("Istnieje już użytkownik o podanej nazwie")
        elif status == protocolFromServer["userNotFound"]:
            print("Nieprawidłowa nazwa użytkonika lub hasło")
        else:
            raise ProtocolException("Nieprawidłowa odpowiedź")

def Main():
    
    # connect to the server
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #host = '192.168.100.7'
        host = '127.0.1.1'
        port = 50005
        s.connect((host, port))
    except ConnectionRefusedError as err:
        print("Nie udało się połączyć z serwerem: ", err)
        return 1

    # print the welcoming message

    print("Proszę się zalogować wpisując '" + protocolFromClient["login"] + " <nick> <hasło>'\n"
          "lub zarejestrować wpisując '" + protocolFromClient["register"] + " <nick> <hasło>'")

    # log in/register
    
    try:
        userdata = authorise(s)
    except (EOFError, KeyboardInterrupt):
        s.close()
        print("Żegnaj")
        return 0

    _thread.start_new_thread(send, (s,))
    _thread.start_new_thread(listen, (s,))

    while True:
        time.sleep(0.1)
        if end:
            break

    print("main wyszedł z while True :00")
    s.close()
    return 0

if __name__ == '__main__':
    Main()
