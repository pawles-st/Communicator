db_credentials = {
    "user": "test", # "root" u Wojtka
    "password": "test", # "root" u Wojtka
    "host": "localhost",
    "database": "chat",
    "port": "3306", # "3306" u Wojtka
}

protocol = {
    "fromServer": {
        "req": "REQUEST",                                       # REQUEST <id_goscia_co_requestuje> (obecnie useless)
        "accepted": "ACCEPTED",                                 # ACCEPTED (obecnie useless)
        "connectFeedback": "CONNECT_OK",                        # CONNECT_OK (obecnie useless)
        "connectionEstablished": "CONNECTION_ESTABLISHED",      # CONNECTION_ESTABISHED (obecnie useless)
        "welcome": "WELCOME",                                   # WELCOME <username? a moze mail idk> <lista uzytkownikow>
        "newUser": "NEW_USER",                                  # NEW_USER <id uzytkownika co dolaczyl>
        "usersList": "ONLINE_LIST",                             # ONLINE_LIST <lista uzytkownikow online>
        "userDisconnected": "INTERLOCUTOR_EXIT",                # INTERLOCUTOR_EXIT <??????????????????> (obecnie useless)
        "disconnected": "DISCONNECT_SUCCESS",                   # DISCONNECT_SUCCESS (obecnie useless)
        "serverError": "SERVER_ERROR",                          # SERVER_ERROR (obecnie useless)
        "notConnected": "NO_FRIENDS?",                          # NO_FRIENDS?
        "receivedMessage": "MESSAGE",                           # MESSAGE <id wysylajacego> <tresc wiadomosci>
        "userLeft": "USER_LEFT",                                # USER_LEFT <id uzytkownika co sie rozlaczyl>
        "alreadyLoggedIn": "ALREADY_LOGGED_IN",                 # ALREADY_LOGGED_IN (obecnie useless)
        "userNotFound": "USER_NOT_FOUND",                       # USER_NOT_FOUND
        "wrongPassword": "WRONG_PASSWORD",                      # WRONG_PASSWORD
        "usernameTaken": "USERNAME_TAKEN",                      # USERNAME_TAKEN
        "notLoggedIn": "NOT_LOGGED_IN",                         # NOT_LOGGED_IN
        "registerSuccess": "REGISTER_SUCCESS",                  # REGISTER_SUCCESS
    },
    "fromClient": {
        "send": "SEND",             # SEND <id_odbiorcy> <wiadomosc>
        "block": "BLOCK",           # BLOCK <id_blokowanego># nie wspierane
        "unblock": "UNBLOCK",       # UNBLOCK <id_odblokowywanego># nie wspierane
        "getUsers": "GET_ONLINE",   # GET_ONLINE [brak parametrow]# w przyszlosci moze byc bezuzyteczne i zostac usuniete
        "sendKey": "SEND_KEY",     # SEND_KEY ???
        "login": "LOGIN",           # LOGIN <mail> <haslo>
        "register": "REGISTER",     # REGISTER <mail> <nazwa_uzytkownika> <haslo>
    }
}
