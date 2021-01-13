


class Trade:
	def __init__(self, owner, offer, demand):
		self.owner = owner
		self.offer = offer
		self.request = demand
		self.fulfilled = False

	def fulfill_transaction(self):
		i = 0
		for resource in self.owner.resources.copy():
			pass

	def check_trade(self, inquiring_player):
		req = self.request
		res = self.owner.resources
		for i in req: