from stream_key import StreamKey
from user import User
from mongoengine import connect as mongo_connect
from mongoengine import disconnect as mongo_disconnect 

class Db:


	def __init__(self, conn_string:str):
		self.conn_string = conn_string
		self.connect()

	def connect(self):
		mongo_connect(host=self.conn_string)

	def close(self):
		mongo_disconnect()

	def get_user(self, user_email:str) -> User:
		return User.objects(email=user_email).first()
	
	# Looks stupid but ensures that connection is established before calling 
	# user.save at some random point.
	def save_user(self, user: User) -> User:
		return user.save()
	# Even more stupid is that connection failure is never handled ... :)

	def save_key(self, key: StreamKey) -> StreamKey:
		return key.save()

	def get_key_with_val(self, key_val:str) -> StreamKey:
		return StreamKey.objects(value=key_val).first()

	def get_key_with_owner(self, user: User) -> StreamKey:
		return StreamKey.objects(owner=user).first()

	# def get_by_key(self, wanted_key: str):
	# 	return User.objects(stream_key__value=wanted_key).first()
		
		