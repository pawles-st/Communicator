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
        self.interlocutorKey = None
        self.app = None
        self.model = Model()
        self.is_logged = False
        self.private_key = None
        self.current_command = None
        self.current_message = None

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

            if message.startswith(protocolFromServer["receivedKey"]):

                # save public key of current interlocutor

                words = message.split()
                public_key_pem = words[1]
                self.interlocutorKey = load_pem_public_key(public_key_pem)

                self.current_command = protocolFromServer["send"] + " " + self.current_message

            if message.startswith(protocolFromServer["receivedMessage"]):

                # read the user and message cipher

                words = message.split(" ", 2)
                user_name = words[1]
                message_cipher = words[2]

                # decode the message with the private key

                message_text = decrypt(message_cipher, self.private_key)

                # add the message to the chat history

                self.model.addUserChatHistory(userName, 1, messageText)

            elif message.startswith(protocolFromServer["newUser"]):

                # add the new user to the list

                words = message.split(" ", 1)
                user = words[1]
                self.app.addOnlineUser(user)
            else:
                self.app.displayMessage(message, -1)

    def send(self):
         while not self.end:
            time.sleep(0.1)
            # message = protocol["send"] + ' ' + input()            # TODO: naprawić, żeby wysyłało SEND tylko gdy nie zaczyna się od słowa kluczowego protkołu

            if self.current_command:
                command = self.current_command
                if command == protocolFromClient["exit"]:
                    self.end = True
                elif command.startswith(protocolFromClient["send"]) and self.interlocutorId != "":

                    if self.interlocutorKey == None:

                        # ask for the interlocutor's public key

                        req = protocolFromClient["getKey"] + " " + self.interlocutorId
                        self.socket.send(bytes(req))

                    else:

                        # add the message to the chat history

                        self.model.addUserChatHistory(self.interlocutorId, 0, msg)
                        message = self.current_command.split(" ", 1)[1]

                        self.current_command = protocolFromClient["send"]

                        # send the message encrypted with the receiver's key

                        encrypted_message = encrypt(message, public_key)
                        req = protocolFromClient["send"] + " " + self.interlocutorId + " " + encrpyted_message
                        self.socket.send(bytes(req, "utf-8"))

                        # send the message encrypted with the sender's key

                        encrypted_message = encrypt(message, get_public_key(self.private_key))
                        req = protocolFromClient["send"] + " " + self.interlocutorId + " " + encrpyted_message
                        self.socket.send(bytes(req, "utf-8"))


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
                        if len(data) == 2:
                            email = data[0]
                            password = data[1]

                            # ask for the salt corresponding to the given mail

                            req = protocolFromClient["getSalt"] + " " + email
                            self.socket.send(bytes(req, "utf-8"))

                            # receive salt from server

                            res = self.socket.recv(self.__SOCKET_RECEIVE_SIZE).decode("utf-8")
                            if res.startswith(protocolFromServer["receivedSalt"]):

                                # hash the password with the salt and send to the server

                                salt = res.split(" ", 1)[1]
                                salt = bytes(salt, "utf-8")
                                pass_bytes = password.encode("utf-8")
                                pass_hash = bcrypt.hashpw(pass_bytes, salt)
                                login_data = protocolFromClient["loginData"] + " " + pass_hash.decode("utf-8")
                                self.socket.send(bytes(login_data, "utf-8"))

                                # verify the password

                                res = self.socket.recv(self.__SOCKET_RECEIVE_SIZE).decode("utf-8")
                                if res.startswith(protocolFromServer["welcome"]):

                                    # setup the app and finish login

                                    self.is_logged = True
                                    self.model.setClientUserName(res[1])
                                    self.app.addMultipleOnlineUsers(res[2])
                                    self.app.displayMessage("Zalogowano.", -1)
                                    return

                                elif res.startswith(protocolFromServer["userNotFound"]):
                                    self.app.displayMessage("Nieprawidłowy email lub hasło", 0)
                                else:
                                    print(res)
                                    raise ProtocolException("Nieprawidłowa odpowiedź")
                            elif res.startswith(protocolFromServer["userNotFound"]):
                                self.app.displayMessage("Nieprawidłowy email lub hasło", 0)
                            else:
                                raise ProtocolException("Nieprawidłowa odpowiedź")
                        else:
                            self.app.displayMessage("Proszę podać <email> <hasło>", 0)
                elif action == protocolFromClient["register"]:
                    if len(data) == 4:
                        email = data[0]
                        login = data[1]
                        password = data[2]
                        password_confirm = data[3]

                        # confirm the password

                        if password == password_confirm:

                            # check email availability

                            self.socket.send(bytes(protocolFromClient["checkAvailability"] + " " + email, "utf-8"))
                            res = self.socket.recv(self.__SOCKET_RECEIVE_SIZE).decode("utf-8")
                            if res.startswith(protocolFromServer["emailValid"]):

                                # hash the password with the received salt

                                salt = res.split(" ", 1)[1]
                                salt = bytes(salt, "utf-8")
                                pass_bytes = password.encode("utf-8")
                                pass_hash = bcrypt.hashpw(pass_bytes, salt)
                                # self.socket.send(bytes((login, pass_hash), "utf-8"))

                                # create the private key and save it

                                self.private_key = create_keys()
                                save_key(self.private_key, Controller.__KEY_FILEPATH)

                                # send the public key to the server

                                public_key = get_public_key(self.private_key)
                                public_key_pem = public_key.public_bytes(
                                        encoding=serialization.Encoding.PEM,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                                )

                                #self.socket.send(public_key_pem)
                                self.socket.send(bytes(protocolFromClient["registerData"] + " " + login + " " + pass_hash.decode("utf-8") + " " + public_key_pem.decode("utf-8"), "utf-8"))
                                # self.socket.send(bytes("REGISTER_DATA " + login + " " + pass_hash + " " + public_key_pem, "utf-8"))

                                # TODO: public key verification?

                                res = self.socket.recv(self.__SOCKET_RECEIVE_SIZE).decode("utf-8")
                                if res.startswith(protocolFromServer["registerSuccess"]):
                                    self.app.displayMessage("Zarejestrowano", -1)

                            elif res.startswith(protocolFromServer["emailTaken"]):
                                self.app.displayMessage("Email jest już zajęty", 0)

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
            host = '192.168.100.7'
            # host = '127.0.1.1'
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
        print(res)
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
