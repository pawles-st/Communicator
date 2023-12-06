from utils import protocol, db_credentials
from DB_access import get_user, get_user_password, create_user
import mysql.connector
import datetime

class Logger():
    def __init__(self):
        self.cnx = mysql.connector.connect(user=db_credentials["user"], password=db_credentials["password"], host=db_credentials["host"], database=db_credentials["database"], port=db_credentials["port"])
        self.cursor = self.cnx.cursor()
    def handle(self, message):
        if message.startswith(protocol["fromClient"]["login"]):
            return self.on_login(message)
        elif message.startswith(protocol["fromClient"]["register"]):
            return self.on_register(message)
        else:
            return "SEND", -1, "NOT_LOGGED_IN"
    def on_login(self, msg):
        credentials = msg.split()
        if len(credentials) != 3:
            return "SEND", -1, "ERROR"
        else:
            existing_user = get_user(self.cnx, credentials[1])
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
    def on_register(self, msg):
        credentials = msg.split()
        if len(credentials) != 4:
            return "SEND", -1, "ERROR"
        else:
            existing_user = get_user(self.cnx, credentials[1])
            if existing_user:
                self.cursor.close()
                return "SEND", -1, "EMAIL_TAKEN"
            else:
                create_user(self.cnx, 5, credentials[2], credentials[3], datetime.datetime.now(), credentials[1], 1)
                self.cursor.close()
                return "SEND", -1, "REGISTER_SUCCESS"
