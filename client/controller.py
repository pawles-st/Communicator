import socket
import time
import _thread
import bcrypt
from model import *
from encryption import *

class Controller():
    __SOCKET_RECEIVE_SIZE = 1024
    __KEY_FILEPATH = "private_key.pem"

    def __init__(self):
        self.socket = None
        self.end = False
        self.interlocutorId = ""
        self.app = None
        self.model = Model()
        self.is_logged = False
        self.private_key = None
        self.current_command = None

    def endController(self):
        self.end = True

    def setApp(self, app):
        self.app = app
        self.app.model = self.model
        self.model.setApp(app)

    def listen(self):
        while not self.end:
            time.sleep(0.1)
            data = self.socket.recv(self.__SOCKET_RECEIVE_SIZE)

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


#    def sendMessage(self, msg):
#
#        if self.logged and self.interlocutorId != "":
#            self.model.addUserChatHistory(self.interlocutorId, 0, msg)
#            msg = protocolFromClient["send"] + " " + self.interlocutorId + " " + msg
#        self.socket.send(bytes(msg, "utf-8"))
            
    def authorise(self):

        # send requests to server until logged in or exits

        while not self.end:
            time.sleep(0.1)

            if self.current_command:

                # read the request and authorisation data and send it to server

                req = self.current_command.split()
                self.current_command = None
                action = req[0]
                data = req[1:]

                # match the request against the protocol

                if action == protocolFromClient["login"]:
                    if self.private_key is None: # can't login without the private key
                        self.app.displayMessage("Nie udało się odnaleźć pliku z kluczem prywatnym", 0)
                    else:
                        email = data[0]
                        salt_request = protocolFromClient["getSalt"] + data[0]
                elif action == protocolFromClient["register"]:
                    if len(data) == 4:
                        email = data[0]
                        login = data[1]
                        password = data[2]
                        password_confirm = data[3]

                        # confirm the password

                        if password == password_confirm:

                            # check email availability

                            self.socket.send(bytes(email, "utf-8"))
                            res = self.socket.recv(self.__SOCKET_RECEIVE_SIZE).decode("utf-8")
                            if res.startswith(protocolFromServer["emailValid"]):

                                # hash the password with the received salt

                                salt = res.split(" ", 1)[1]
                                pass_bytes = password.encode("utf-8")
                                pass_hash = bcrypt.hashpw(pass_bytes, salt)
                                self.socket.send(bytes((login, pass_hash), "utf-8"))

                                # create the private key and save it

                                self.private_key = create_keys()
                                save_key(self.private_key, Controller.__KEY_FILEPATH)

                                # send the public key to the server

                                public_key = get_public_key(self.private_key)
                                public_key_pem = public_key.public_bytes(
                                        encoding=serialization.Encoding.PEM,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                                )
                                self.socket.send(public_key_pem)

                                # TODO: public key verification?

                                # return userdata

                                userdata = (email, login)
                                return userdata

                            elif res.startswith(protocolFromServer["emailTaken"]):
                                self.app.displayMessage("Email jest już zajęty")

                        else:
                            self.app.displayMessage("Proszę wpisać to samo hasło w potwierdzeniu", 0)
                    else:
                        self.app.displayMessage("Proszę podać <email> <nazwę_użytkownika> <hasło> <potwierdzenie_hasła>", 0)
        else:
            raise TerminateException("Nieudany login")

    def controllerStart(self):

        # read the private key from file

        try:
            self.private_key = load_key(Controller.__KEY_FILEPATH)
        except FileNotFoundError:
            # there is no private key yet; the user won't be able to make any LOGIN requests
            self.app.displayMessage("Nie znaleziono klucza prywatnego. Jeśli nie posiadasz jeszcze konta, zignoruj tę wiadomość. W przeciwnym wypadku proszę umieścić klucz prywatny w folderze z aplikacją\n", 0)
        except ValueError:
            self.app.displayMessage("Nie udało się wczytać klucza prywatnego: plik mógł zostać uszkodzony.\n", 0)

        # connect to the server

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # host = '192.168.100.7'
            host = '127.0.1.1'
            port = 50005
            self.socket.connect((host, port))
        except ConnectionRefusedError as err:
            self.app.displayMessage("Nie udało się połączyć z serwerem: " + str(err), 0)
            return 1

        # display the welcoming message

        self.app.displayMessage("Proszę się zalogować wpisując '" + protocolFromClient["login"] + " <mail> <hasło>'\n"
              "lub zarejestrować wpisując '" + protocolFromClient["register"] + " <mail> <nazwa_użytkownika> <hasło> <potwierdzenie_hasła>'", -1)

        # log in/register

        try:
            userdata = self.authorise()
        except TerminateException:
            return 1

        # setup the app after successful login/registration
        
        res = self.socket.recv(self.__SOCKET_RECEIVE_SIZE).decode("utf-8")
        if res.startswith(protocolFromServer["welcome"]):
            self.is_logged = True
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
        else:
            raise self.ProtocolException("Nieprawidłowa odpowiedź")

        self.app.displayLoggedUserName(self.model.getClientUserName())

        _thread.start_new_thread(self.send, ())
        _thread.start_new_thread(self.listen, ())

        return 0
