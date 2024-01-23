import base64
import string
import random
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import mariadb
from utils import protocol, db_credentials
from DB_access import get_user, get_user_password, create_user, get_salt
# import mysql.connector
import datetime
import bcrypt
# TODO: gdy dwoch uzytkownikow wysle CHECK_AVAILABILTY <mail> i to jest ten sam mail i pozniej obaj wysla reszte credentials to jednemu sie uda zrobic konto a drugiemu nwm
class Logger():
    def __init__(self):
        # self.cnx = mysql.connector.connect(user=db_credentials["user"], password=db_credentials["password"], host=db_credentials["host"], database=db_credentials["database"], port=db_credentials["port"])
        self.cnx = mariadb.connect(user=db_credentials["user"], password=db_credentials["password"], host=db_credentials["host"], database=db_credentials["database"], port=db_credentials["port"])
        self.cursor = self.cnx.cursor()
        self.state = 0  # 0 - nic sie nie dzieje specjalnego,
                        # 1 - dostalem check_avalaialabelity i jest wolny email wiec czekam na send_key,
                        # 3 - dostalem send_key, czekam na weryfikacje.
                        # 4 - dostalem weryfikacje, czekam na reszte danych do rejestracji
                        # 2 - dostalem get_salt i czekam na login_data
        self.email = None # chcialem napisac komentarz ale nie pamietam jaki
        self.salt = None
        self.public_key = None
        self.verification_string = None
    def handle(self, message):
        print(message)
        # if message.startswith(protocol["fromClient"]["login"]) and self.state == 0:
        #     return self.on_login(message)
        # elif message.startswith(protocol["fromClient"]["register"]):
        #     return self.on_register(message)
        if message.startswith("CHECK_AVAILABILITY") and self.state == 0: # CHECK_AVAILABILITY <mail>
            return self.on_check_availability(message)
        elif message.startswith("REGISTER_DATA") and self.state == 4: # REGISTER_DATA <login> <haslo> <klucz>
            return self.on_register_data(message)
        elif message.startswith("GET_SALT") and self.state == 0:
            return self.on_get_salt(message)
        elif message.startswith("LOGIN_DATA") and self.state == 2:
            return self.on_login_data(message)
        elif message.startswith("SEND_KEY") and self.state == 1:
            return self.on_send_key(message)
        elif message.startswith("VERIFICATION") and self.state == 3:
            return self.on_verification(message)
        else:
            return "SEND", -1, "NOT_LOGGED_IN"
    def on_check_availability(self, msg):
        credentials = msg.split()

        if len(credentials) != 2:
            self.state = 0
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
        credentials = msg.split(' ', 2) #REGISTER_DATA <login> <haslo>
        if len(credentials) < 3:
            self.state = 0
            return "SEND", -1, "ERROR"
        else:
            create_user(self.cnx, 5, credentials[1], credentials[2], datetime.datetime.now(), self.email, self.public_key, self.salt.decode("utf-8"))
            self.state = 0
            print("user created")
            self.cursor.close()
            return "SEND", -1, "REGISTER_SUCCESS"
    def on_get_salt(self, msg): #GET_SALT <emali>
        credentials = msg.split(' ')
        if len(credentials) != 2:
            self.state = 0
            return "SEND", -1, "ERROR"
        else:
            self.state = 2
            self.email = credentials[1]
            existing_user = get_user(self.cnx, credentials[1])
            if existing_user:
                salt = get_salt(self.cnx, credentials[1])
                self.cursor.close()
                return "SEND", -1, "SALT " + salt[0]
            else:
                self.cursor.close()
                return "SEND", -1, "USER_NOT_FOUND"
    def on_login_data(self, msg):
        credentials = msg.split(' ')
        if len(credentials) != 2:
            self.state = 0
            return "SEND", -1, "ERROR"
        else:
            existing_user = get_user(self.cnx, self.email)
            if existing_user:
                check = get_user_password(self.cnx, self.email, credentials[1])
                if check:
                    self.cursor.close()
                    return "WELCOME", -1, str(self.email)
                else:
                    self.cursor.close()
                    self.state = 0
                    return "SEND", -1, "USER_NOT_FOUND"
            else:
                self.cursor.close()
                self.state = 0
                return "SEND", -1, "USER_NOT_FOUND"
    def on_send_key(self, msg):
        data = msg.split(' ', 1)
        if len(data) != 2:
            self.state = 0
            return "SEND", -1, "ERROR"
        else:
            self.public_key = data[1]
            public_key_pem = load_pem_public_key(bytes(data[1], "utf-8"))
            self.verification_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            ciphertext = public_key_pem.encrypt(
                bytes(self.verification_string, "utf-8"),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                )
            )
            req = "VERIFY_KEY " + base64.b64encode(ciphertext).decode("utf-8")
            self.state = 3
            return "SEND", -1, req

    def on_verification(self, msg):
        data = msg.split(' ', 1)
        if len(data) != 2:
            self.state = 0
            return "SEND", -1, "ERROR"
        else:
            print("expected: " + self.verification_string + ", got " + data[1])
            if data[1] == self.verification_string:
                self.state = 4
                return "SEND", -1, "VERIFIED"
            else:
                self.state = 0
                return "SEND", -1, "NOT_VERIFIED"