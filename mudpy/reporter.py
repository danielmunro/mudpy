class Reporter:

	def getMessages(self, messagePart, invoker, receiver = None):
		try:
			messages[invoker] = messages.pop('invoker')
			if messages[invoker].find('%s') > -1:
				messages[invoker] = messages[invoker] % str(receiver)
		except KeyError: pass
		try:
			messages[receiver] = messages.pop('receiver')
			if messages[receiver].find('%s') > -1:
				messages[receiver] = messages[receiver] % str(receiver)
		except KeyError: pass
		try:
			messages['*'] = messages.pop('*')
			if messages['*'].find('%s') > -1:
				messages['*'] = messages['*'] % str(invoker)
			if messages['*'].find('%s') > -1:
				messages['*'] = messages['*'] % str(receiver)
		except KeyError: pass
		return messages
