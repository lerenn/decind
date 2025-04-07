import math

class ArbitrageTraderImportError(Exception):
	"""
	Exception raised for errors related to arbitrage trader import
	"""

	def __init__(self, msg):
		super().__init__(msg)

class ArbitrageTrader(object):
	"""
	This class represents an arbitrage trader
	its funds are artificially unlimited
	"""

	def __init__(self, name, profit_token):
		self._name = name
		self._profit_token = profit_token
		self._provided_funds = 0

	def __repr__(self):
		return self._name

	def provide_funds(self, qty):
		self._provided_funds += qty
		self._profit_token.mint(self, qty)

	def provided_funds(self):
		return self._provided_funds

	def profits(self):
		return self._profit_token.funds(self) - self._provided_funds

	def _arbitrage_liquidity_pools(self, tokens, liquidity_pool1, liquidity_pool2):
		event = 0

		# Get common funds (except profit token)
		exch1_avail = set(liquidity_pool1.available(tokens))
		if self._profit_token in exch1_avail:
			exch1_avail.remove(self._profit_token)
		exch2_avail = set(liquidity_pool2.available(tokens))
		common = list(exch1_avail & exch2_avail)

		# Compare common pairs
		for bc in common:
				p1 = liquidity_pool1.price(bc, self._profit_token)
				p2 = liquidity_pool2.price(bc, self._profit_token)

				# Get variables
				bq_e1 = liquidity_pool1.funds(bc)
				bq_e2 = liquidity_pool2.funds(bc)
				pq_e1 = liquidity_pool1.funds(self._profit_token)
				pq_e2 = liquidity_pool2.funds(self._profit_token)
				a = pq_e2*bq_e1-pq_e1*bq_e2
				b = (bq_e2*pq_e1+pq_e2*bq_e1)*(bq_e1+bq_e2)
				c = (pq_e2*bq_e1-pq_e1*bq_e2)*(bq_e1*bq_e2)
				if a != 0:
					d = b**2-4*a*c
					qty = abs((-b+math.sqrt(d))/(2*a))
				else:
					qty = -c/b

				if p1 > p2:
					liquidity_pool2.swap(self, bc, -qty, self._profit_token)
					liquidity_pool1.swap(self, bc, qty, self._profit_token)
					event += 1
				else:
					liquidity_pool1.swap(self, bc, -qty, self._profit_token)
					liquidity_pool2.swap(self, bc, qty, self._profit_token)
					event += 1

		return event

	def arbitrage(self, tokens, liquidity_pools):
		event = 0

		for (i, e1) in enumerate(liquidity_pools):
			for e2 in liquidity_pools[i+1:]:
				if e1.funds(self._profit_token) == 0:
					continue
				elif e2.funds(self._profit_token) == 0:
					continue

				event += self._arbitrage_liquidity_pools(tokens, e1, e2)

		return event

	def json(self):
		"""
		Methods that convert the object to JSON
		"""
		json_struct = {
			"name": self._name,
			"profit_token": str(self._profit_token),
			"provided_funds": self._provided_funds
		}
		return json_struct

	def from_json(json_struct, tokens=[]):
		"""
		Class method that convert a JSON to the object
		"""

		profit_token = None
		for t in tokens:
			if str(t) == json_struct["profit_token"]:
				profit_token = t

		if profit_token is None:
			raise ArbitrageTraderImportError(
				" ".join([f"Profit token '{json_struct['profit_token']}'",
					f"for the arbitrage trade '{json_struct['name']}' was not provided"]))

		at = ArbitrageTrader(json_struct["name"], profit_token)
		at._provided_funds = json_struct["provided_funds"]

		return at

