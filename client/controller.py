import socket
import time
import _thread
import bcrypt
from model import *
from encryption import *

class Controller():
    class ProtocolException(Exception):
        pass


    SOCKET_RECEIVE_SIZE = 1024
    KEY_FILEPATH = "private_key.pem"

    def __init__(self):
        self.socket = None
        # self.userNick = ''
        self.end = False
        self.interlocutorId = ""
        self.app = None
        self.model = Model()
        self.logged = False

    # def getUserNick(self):
    #     return self.userNick

    def isLogged(self):
        return self.logged

    def setLogged(self, val):
        self.logged = val

    def setInterlocutorId(self, id):
        self.interlocutorId = id

    def endController(self):
        self.end = True

    def setApp(self, app):
        self.app = app
        self.app.model = self.model
        self.model.setApp(app)

    def listen(self):
        while True:
            time.sleep(0.1)
            data = self.socket.recv(self.SOCKET_RECEIVE_SIZE)

            message = str(data.decode('utf-8'))

            if message.startswith(protocolFromServer["req"]):
                self.interlocutorId = int(message[(len(protocolFromServer["req"]) + 1):])
                self.app.displayMessage("Użytkownik o ID " + str(self.interlocutorId) + " chce z Tobą rozmawiać. "
                        "Napisz '" +  str(protocolFromClient["accept"]) + ' ' + str(self.interlocutorId) + "' żeby zaakceptować połączenie.", -1)
            elif message.startswith(protocolFromServer["accepted"]):
                self.interlocutorId = int(message[(len(protocolFromServer["accepted"]) + 1):])
                # self.app.displayMessage("Użytkownik o ID", interlocutorId, "zaakceptował połączenie. "
                #         "Możecie teraz ze sobą rozmawiać.")
                self.app.displayMessage("Połączenie z użytkownikiem o ID " + str(self.interlocutorId) + " zostało nawiązane. "
                        "Możecie teraz ze sobą rozmawiać.", -1)
            # elif message.startswith(protocolFromServer["welcome"]):
            #     words = message.split(' ', 3)
            #     # self.app.displayMessage(words)
            #     self.app.displayMessage(
            #         "Witaj,", words[2], "wybierz któregoś użytkownika z listy wpisując '" + protocolFromClient["connect"] + " <id>' "
            #         "żeby poprosić o rozpoczęcie rozmowy.\n"
            #         "Aby rozłączyć się z tym użytkownikiem napisz '" +
            #         protocolFromClient["disconnect"] + "'.")
            #     self.app.displayMessage("Twoje id:", words[1], "\nLista obecnych użytkowników:", words[3])
            elif message.startswith(protocolFromServer["connectionEstablished"]):
                self.app.displayMessage("Proszę się zalgować wpisując '" + protocolFromClient["login"] + " <nick> <hasło>'\n"
                        "lub zarejestrować wpisując '" + protocolFromClient["register"] + " <nick> <hasło>'", -1)
            elif message.startswith(protocolFromServer["receivedMessage"]):
                words = message.split(" ", 2)
                userName = words[1]
                messageText = words[2]
                self.model.addUserChatHistory(userName, 1, messageText)
                # self.app.displayMessage(messageText, userName)
            elif message.startswith(protocolFromServer["newUser"]):
                user = message[(len(protocolFromServer["newUser"]) + 1):]
                self.app.addOnlineUser(user)
            elif message.startswith(protocolFromServer["userLeft"]):
                user = message[(len(protocolFromServer["userLeft"]) + 1):]
                self.app.removeOnlineUser(user)
            else:
                self.app.displayMessage(message, -1)

            if self.end:
                break



    # def send(self):
    #     # global self.userNick
    #     while True:
    #         time.sleep(0.1)
    #         # message = protocol["send"] + ' ' + input()            # TODO: naprawić, żeby wysyłało SEND tylko gdy nie zaczyna się od słowa kluczowego protkołu
    #         message = input()
    #
    #         if message == protocolFromClient["exit"]:
    #             self.end = True
    #             break
    #         # elif message.startswith(protocolFromClient["login"]):
    #         #     words = message.split()
    #         #     self.userNick = words[1]
    #         self.socket.send(bytes(message, "utf-8"))
    #     self.app.displayMessage("send wyszedł z while")


    def sendMessage(self, msg):

        if self.isLogged() and self.interlocutorId != "":
            self.model.addUserChatHistory(self.interlocutorId, 0, msg)
            msg = protocolFromClient["send"] + " " + self.interlocutorId + " " + msg
        self.socket.send(bytes(msg, "utf-8"))

    def authorise(self):

        # send requests to server until logged in or exits

        while True:

            # read the request and authorisation data and send it to server

            # message = input()
            #req = message.split(" ")
            #if req[0] == protocolFromClient["login"]:
            #    bcrypt

            # self.socket.send(bytes(message, "utf-8"))
            # self.app.displayMessage("message: ", message)
            # read server response

            response = self.socket.recv(self.SOCKET_RECEIVE_SIZE)
            response = response.decode("utf-8").split(" ", 2)
            status = response[0]
            data = response[1:]

            # print(response)

            # if registration is successful, create RSA keys and send them to server
            # if login is successful, return login data
            # otherwise, self.app.displayMessage the corresponding error message

            if status == protocolFromServer["registerSuccess"]:  # successful register
                # TODO: dodać tu coś (jakiś feedback w gui że się udało zarejestrować)
                private_key = create_keys()
                save_key(private_key, KEY_FILEPATH)
                public_key_pem = get_public_key_pem(private_key)
                

            elif status == protocolFromServer["welcome"]:  # successful login
                self.setLogged(True)
                self.model.setClientUserName(response[1])
                self.app.addMultipleOnlineUsers(response[2])
                # self.app.displayMessage(
                #     "Witaj, " + response[1] +
                #     " wybierz któregoś użytkownika z listy wpisując '" + protocolFromClient["connect"] + " <id>' "
                #                                                                                         "żeby poprosić o rozpoczęcie rozmowy.\n"
                #                                                                                         "Aby rozłączyć się z tym użytkownikiem napisz '" +
                #     protocolFromClient["disconnect"] + "'.", -1)
                # self.app.displayMessage("\nLista obecnych użytkowników: " + response[2], -1)
                self.app.displayMessage("Zalogowano.", -1)
                return data
            elif status == protocolFromServer["usernameTaken"]:
                self.app.displayMessage("Istnieje już użytkownik o podanej nazwie", -1)
            elif status == protocolFromServer["userNotFound"]:
                self.app.displayMessage("Nieprawidłowa nazwa użytkonika lub hasło", -1)
            else:
                raise self.ProtocolException("Nieprawidłowa odpowiedź")

    def controllerStart(self):
        # connect to the server

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            host = '192.168.100.7'
            # host = '127.0.1.1'
            port = 50005
            self.socket.connect((host, port))
        except ConnectionRefusedError as err:
            self.app.displayMessage("Nie udało się połączyć z serwerem: " + str(err), -1)
            return 1

        # self.app.displayMessage the welcoming message

        self.app.displayMessage("Proszę się zalogować wpisując '" + protocolFromClient["login"] + " <mail> <hasło>'\n"
              "lub zarejestrować wpisując '" + protocolFromClient["register"] + " <mail> <nazwa_uzytkownika> <haslo>'", -1)

        # log in/register

        try:
            userdata = self.authorise()
        except (EOFError, KeyboardInterrupt):
            self.socket.close()
            self.app.displayMessage("Żegnaj", -1)
            return 0

        # self.app.displayMessage(userdata)
        # self.userNick = userdata[0]
        # self.app.displayMessage("Twój nick: " + self.userNick, -1)
        self.app.displayLoggedUserName(self.model.getClientUserName())

        # _thread.start_new_thread(self.send, ())
        _thread.start_new_thread(self.listen, ())

        while True:
            time.sleep(0.1)
            if self.end:
                break

        self.socket.close()
        return 0

if __name__ == '__main__':
    controller = Controller()
    controller.controllerStart()
