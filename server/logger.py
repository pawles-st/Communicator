from utils import protocol, db_credentials
from DB_access import get_user, get_user_password, create_user
import mysql.connector
import datetime
import bcrypt
# TODO: gdy dwoch uzytkownikow wysle CHECK_AVAILABILTY <mail> i to jest ten sam mail i pozniej obaj wysla reszte credentials to jednemu sie uda zrobic konto a drugiemu nwm
class Logger():
    def __init__(self):
        self.cnx = mysql.connector.connect(user=db_credentials["user"], password=db_credentials["password"], host=db_credentials["host"], database=db_credentials["database"], port=db_credentials["port"])
        self.cursor = self.cnx.cursor()
        self.state = 0 # 0 - nic sie nie dzieje specjalnego, 1 - dostalem check_avalaialabelity i jest wolny email wiec czekam na reszte credentials
        self.email = None # chcialem napisac komentarz ale nie pamietam jaki
        self.salt = None
    def handle(self, message):
        if message.startswith(protocol["fromClient"]["login"]) and self.state == 0:
            return self.on_login(message)
        # elif message.startswith(protocol["fromClient"]["register"]):
        #     return self.on_register(message)
        elif message.startswith("CHECK_AVAILABILITY") and self.state == 0: # CHECK_AVAILABILITY <mail>
            return self.on_check_availability(message)
        elif message.startswith("REGISTER_DATA") and self.state == 1: # REGISTER_DATA <login> <haslo> <klucz>
            return self.on_register_data(message)
        else:
            return "SEND", -1, "NOT_LOGGED_IN"
    def on_login(self, msg):
        credentials = msg.split()
        if len(credentials) != 3:
            return "SEND", -1, "ERROR"
        else:
            existing_user = get_user(self.cnx, credentials[1])
            print(existing_user)
            if existing_user:
                check = get_user_password(self.cnx, credentials[1], credentials[2])
                if check:
                    self.cursor.close()
                    return "WELCOME", -1, str(credentials[1])
                else:
                    self.cursor.close()
                    return "SEND", -1, "USER_NOT_FOUND"
            else:
                self.cursor.close()
                return "SEND", -1, "USER_NOT_FOUND"
    # def on_register(self, msg):
    #     credentials = msg.split()
    #     if len(credentials) != 4:
    #         return "SEND", -1, "ERROR"
    #     else:
    #         existing_user = get_user(self.cnx, credentials[1])
    #         if existing_user:
    #             self.cursor.close()
    #             return "SEND", -1, "USERNAME_TAKEN"
    #         else:
    #             create_user(self.cnx, 5, credentials[2], credentials[3], datetime.datetime.now(), credentials[1], 1)
    #             self.cursor.close()
    #             return "SEND", -1, "REGISTER_SUCCESS"
    def on_check_availability(self, msg):
        credentials = msg.split()

        if len(credentials) != 2:
            return "SEND", -1, "ERROR"
        else:
            existing_user = get_user(self.cnx, credentials[1])
            if existing_user:
                self.cursor.close()
                return "SEND", -1, "EMAIL_TAKEN"
            else:
                self.state = 1
                self.email = credentials[1]
                self.salt = bcrypt.gensalt()
                self.cursor.close()
                return "SEND", -1, "EMAIL_VALID " + self.salt.decode("utf-8")
    def on_register_data(self, msg):
        credentials = msg.split(' ', 3) #REGISTER_DATA <login> <haslo> <klucz>
        if len(credentials) < 4:
            return "SEND", -1, "ERROR"
        else:
            create_user(self.cnx, 5, credentials[1], credentials[2], datetime.datetime.now(), self.email, credentials[3], self.salt.decode("utf-8"))
            print("user created")
            self.cursor.close()
            return "SEND", -1, "REGISTER_SUCCESS"
