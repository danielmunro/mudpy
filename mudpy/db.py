import redis

class Db:
	def __init__(self):
		self.r = redis.Redis(host='localhost', port=6379, db=10)

	def getConnection(self):
		return self.r
