import redis

class Db:
	def __init__(self):
		self.conn = redis.Redis(host='localhost', port=6379, db=10)
