from .constants import ROUND_VALUE

class LiquidityPoolInexistantPairError(Exception):
	"""
	Exception raised for errors related to inexistant pair
	"""

	def __init__(self, base_token, quote_token):
		msg = f"Pair {base_token}-{quote_token} doesn't exist"
		super().__init__(msg)

class LiquidityPool(object):
	"""
	This class represents an liquidity_pool
	"""

	def __init__(self, name):
		self._name = name

	def __repr__(self):
		return self._name

	def change_funds(self, token, qty):
		if qty > 0:
			token.mint(self, qty)
		elif qty < 0:
			token.burn(self, -qty)

	def funds(self, token):
		return token.funds(self)

	def price(self, base_token, quote_token):
		quote_qty = quote_token.funds(self)
		base_qty = base_token.funds(self)

		# Check that the pair exists
		if base_qty == 0 or quote_qty == 0:
			raise LiquidityPoolInexistantPairError(base_token, quote_token)

		price = round(quote_qty/base_qty, ROUND_VALUE)
		if price == 0:
			return 10**(-ROUND_VALUE)

		return price

	def pairs(self, tokens):
		pairs = []

		for (i, b1) in enumerate(tokens):
			for b2 in tokens[i+1:]:
				if b1 != b2 and self.funds(b1) != 0 and self.funds(b2) != 0:
					pairs.append((b1, b2))
					pairs.append((b2, b1))

		return pairs

	def available(self, tokens):
		bc = []
		for b in tokens:
			if self.funds(b) != 0:
				bc.append(b)
		return bc

	def swap(self, holder, base_token, base_qty, quote_token):
		quote_qty = self.price(base_token, quote_token)*base_qty
		base_token.transfer(holder, self, base_qty)
		quote_token.transfer(self, holder, quote_qty)

		# Take care of stablecoins
		if base_token.stablecoin() and quote_token.stablecoin():
			self.change_funds(base_token, -base_qty)
			self.change_funds(quote_token, quote_qty)
		elif base_token.stablecoin():
			quote_qty = base_qty*self.price(base_token, quote_token)
			self.change_funds(base_token, -base_qty)
			self.change_funds(quote_token, -quote_qty)
		elif quote_token.stablecoin():
			base_qty = quote_qty/self.price(base_token, quote_token)
			self.change_funds(base_token, base_qty)
			self.change_funds(quote_token, quote_qty)

	def json(self):
		"""
		Methods that convert the object to JSON
		"""
		json_struct = {
			"name": self._name,
		}
		return json_struct

	def from_json(json_struct):
		"""
		Class method that convert a JSON to the object
		"""

		return LiquidityPool(json_struct["name"])
