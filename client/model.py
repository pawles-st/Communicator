

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
    "emailTaken": "EMAIL_TAKEN",
    "emailValid": "EMAIL_VALID",
    "registerSuccess": "REGISTER_SUCCESS",
    "receivedSalt": "RECEIVED_SALT",
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
    "getSalt": "GET_SALT",
}


class Model():

    def __init__(self):
        self.app = None
        self.usersChatHistory = {}
        self.clientUserName = ''
        self.onlineUsersList = []

    def addOnlineUser(self, userName):
        self.onlineUsersList.append(userName)

    def removeOnlineUser(self, userName):
        idx = self.onlineUsersList.index(userName)
        del self.onlineUsersList[idx]
        return idx

    def setApp(self, app):
        self.app = app

    def setClientUserName(self, name):
        self.clientUserName = name

    def getClientUserName(self):
        return self.clientUserName

    def addUserChatHistory(self, userName, whoSent, message):      # whoSent: 0 - clientUser wysłał, 1 - User wysłał
        if not userName in self.usersChatHistory:
            self.usersChatHistory[userName] = []

        messageInfo = {"from": whoSent, "text": message}
                
        self.usersChatHistory[userName].append(messageInfo)
        self.app.displayMessage(str(messageInfo), userName)
    def getUserChatHistory(self, userName):
        if not userName in self.usersChatHistory:
            self.usersChatHistory[userName] = []
        return self.usersChatHistory[userName]

class ProtocolException(Exception):
    pass

class TerminateException(Exception):
    pass
