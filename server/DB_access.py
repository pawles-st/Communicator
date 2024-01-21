import mariadb.connector
import datetime
from utils import db_credentials

def get_all_users(connection):
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM user")
	result = cursor.fetchall()
	for row in result:
		print(row)
	cursor.close()

def get_user(connection, mail):
	cursor = connection.cursor()
	query = "SELECT * FROM user WHERE user_email = %s" # TODO: sql ignoruje case-sensitivity (np. email = h ale znajduje dla email = H)
	cursor.execute(query,(mail,))
	result = cursor.fetchone()
	return result

def get_user_password(connection,mail,password):
	cursor = connection.cursor()
	query = "SELECT * FROM user WHERE user_email = %s AND BINARY user_password = BINARY %s"
	cursor.execute(query,(mail,password,))
	result = cursor.fetchone()
	return result

def create_user(connection, id, name, password, date, mail, key, salt):
	cursor = connection.cursor()

	sql = "INSERT INTO user (user_name, user_password, date_of_join, user_email, user_pk, salt) VALUES (%s,%s,%s,%s,%s,%s)"

	user_data = (name,password,date,mail,key,salt)

	cursor.execute(sql, user_data)
	connection.commit()
	cursor.close()

def create_conversation(connection, id, name):
	cursor = connection.cursor()

	sql = "INSERT INTO conversation (conversation_id, conversation_name) VALUES (%s,%s)"

	conv_data = (id,name)

	cursor.execute(sql, conv_data)
	connection.commit()
	cursor.close()

def create_conversation_member(connection, userid, convid, date_of_join):
	cursor = connection.cursor()

	sql = "INSERT INTO conversation_member (user_id, conversation_id, joined_datetime) VALUES (%s,%s,%s)"
	conv_member_data = (userid,convid,date_of_join)

	cursor.execute(sql,conv_member_data)
	connection.commit()
	cursor.close()

def create_message(connection, message_id, sender_email, text, date_of_send, conv_id):
	cursor = connection.cursor()

	sql = "INSERT INTO message (message_id, sender_email, text, send_date, conv_id) VALUES (%s,%s,%s,%s,%s)"
	conv_member_data = (message_id,sender_email,text,date_of_send,conv_id)

	cursor.execute(sql, conv_member_data)
	connection.commit()
	cursor.close()

def get_salt(connection, mail):
	cursor = connection.cursor()
	query = "SELECT salt FROM user WHERE user_email = %s"
	cursor.execute(query,(mail,))
	result = cursor.fetchone()
	return result

def get_key(connection, mail):
	cursor = connection.cursor()
	query = "SELECT user_pk FROM user WHERE user_email = %s"
	cursor.execute(query, (mail,))
	result = cursor.fetchone()
	return result

def get_message_text_by_id(connection, mess_id):
	cursor = connection.cursor()
	query = "SELECT message_text FROM message WHERE message_id = %s"
	cursor.execute(query(mess_id,))
	result = cursor.fetchone()
	return result
def get_all_messages_from_convo(connection, convo_id):
	cursor = connection.cursor()
	query = "SELECT message_text FROM message WHERE conversation_id = %s"
	cursor.execute(query(convo_id,))
	result = cursor.fetchall()
	return result

def get_all_messages_with_senders_from_convo(connection, convo_id):
	cursor = connection.cursor()
	query = "SELECT sender_email, message_text FROM message WHERE conversation_id = %s"
	cursor.execute(query(convo_id, ))
	result = cursor.fetchall()
	return result
def get_user_conversations(connection, mail):
	cursor = connection.cursor()
	query = "SELECT conversation_id FROM conversation_member WHERE user_email = %s"
	cursor.execute(query(mail, ))
	result = cursor.fetchall()
	return result

#Można dorobić queries które zwracają też datę i godzine wysłania
def get_x_latest_messages_from_convo_by_date(connection, convo_id, x):
	cursor = connection.cursor()
	query = "SELECT message_text FROM message WHERE conversation_id = %s ORDER BY datetime_of_sending DESC LIMIT %s"
	cursor.execute(query(convo_id,x,))
	result = cursor.fetchall()
	return result

def get_x_latest_messages_with_senders_from_convo_by_date(connection, convo_id, x):
	cursor = connection.cursor()
	query = "SELECT sender_email, message_text FROM message WHERE conversation_id = %s ORDER BY datetime_of_sending DESC LIMIT %s"
	cursor.execute(query(convo_id,x,))
	result = cursor.fetchall()
	return result

def get_x_latest_messages_from_convo_by_id(connection, convo_id, x):
	cursor = connection.cursor()
	query = "SELECT message_text FROM message WHERE conversation_id = %s ORDER BY message_id DESC LIMIT %s"
	cursor.execute(query(convo_id,x))
	result = cursor.fetchall()
	return result

def get_x_latest_messages_with_senders_from_convo_by_id(connection, convo_id, x):
	cursor = connection.cursor()
	query = "SELECT sender_email, message_text FROM message WHERE conversation_id = %s ORDER BY message_id DESC LIMIT %s"
	cursor.execute(query(convo_id,x))
	result = cursor.fetchall()
	return result

def get_x_messages_with_senders_with_id_less_than(connection, convo_id, earlier_than_id, no_of_messages):
	cursor = connection.cursor()
	query = "SELECT sender_email,message_text FROM message WHERE conversation_id = %s AND message_id < %s ORDER BY message_id DESC LIMIT %s"
	cursor.execute(query(convo_id,earlier_than_id,no_of_messages))
	result = cursor.fetchall()
	return result
def get_messages_sent_after_x(connection, convo_id, date):
	cursor = connection.cursor()
	query = "SELECT sender_email,message_text FROM message WHERE conversation_id = %s AND datetime_of_sending > %s ORDER BY datetime_of_sending DESC"
	cursor.execute(query(convo_id,date,))
	result = cursor.fetchall()
	return result

def edit_message(connection, text, message_id):
	cursor = connection.cursor()
	query = "UPDATE message SET message_text = %s WHERE message_id = %s"
	cursor.execute(query(text,message_id,))
	connection.commit()
	cursor.close()

def delete_message(connection, message_id):
	cursor = connection.cursor()
	query = "DELETE FROM message WHERE message_id = %s"
	cursor.execute(query(message_id,))
	connection.commit()
	cursor.close()

cnx = mysql.connector.connect(user=db_credentials["user"], password=db_credentials["password"],
								   host=db_credentials["host"], database=db_credentials["database"],
								   port=db_credentials["port"])

cursor = cnx.cursor()
#create_user(cnx,2,"siema","okoń",datetime.datetime.now(),"haha@wp.pl","123k5432wibblywobbly")
# get_all_users(cnx)

#cursor.execute("CREATE DATABASE chat")
#cursor.execute("CREATE TABLE message (message_id INT PRIMARY KEY, sender_id INT, message_text VARCHAR(1000), datetime_of_sending DATETIME, conversation_id INT, FOREIGN KEY(conversation_id) REFERENCES conversation(conversation_id) ON DELETE SET NULL)")
#cursor.execute("CREATE TABLE conversation (conversation_id INT PRIMARY KEY, conversation_name VARCHAR(100))")
#cursor.execute("CREATE TABLE conversation_member (user_id INT NOT NULL, conversation_id INT, joined_datetime DATETIME, left_datetime DATETIME, FOREIGN KEY(user_id) REFERENCES user(user_id), FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id), CONSTRAINT Pk_conv_member PRIMARY KEY(user_id, conversation_id))")
#cursor.execute("CREATE TABLE user (user_id INT NOT NULL PRIMARY KEY, user_name VARCHAR(100), user_password VARCHAR(60), date_of_join DATETIME)")
#cursor.execute("ALTER TABLE user ADD user_email VARCHAR(150)")
#cursor.execute("ALTER TABLE user ADD user_pk VARCHAR(100)")




