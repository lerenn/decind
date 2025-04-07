from .constants import ROUND_VALUE

class TokenFundsError(Exception):
	"""
	Exception raised for errors related to funds
	"""

	def __init__(self, token_name, qty, holder):
		msg = f"{holder} do not have enough {token_name} be removed of {qty}"
		super().__init__(msg)

class TokenSupplyError(Exception):
	"""
	Exception raised for errors related to supply
	"""

	def __init__(self, token_name, qty, holder):
		msg = f"There is not enough supply to set {qty} {token_name} to {holder}"
		super().__init__(msg)

class TokenMintError(Exception):
	"""
	Exception raised for errors related to mint
	"""

	def __init__(self, msg):
		super().__init__(msg)

class TokenBurnError(Exception):
	"""
	Exception raised for errors related to burn
	"""

	def __init__(self, msg):
		super().__init__(msg)

class Token(object):
	"""
	This class represents a tokenized token
	If there is no supply, then it is a stablecoin
	"""

	def __init__(self, name, stablecoin=False):
		self._name = name
		self._holders = {}
		self._stablecoin = stablecoin

	def __repr__(self):
		return self._name

	def stablecoin(self):
		return self._stablecoin

	def global_price(self, liquidity_pools, quote_token):
		price = 0
		count = 0
		for e in liquidity_pools:
			if len(e.available([self])) != 0 and len(e.available([quote_token])) != 0:
				price += e.price(self, quote_token)*e.funds(self)
				count += e.funds(self)

		return price/count

	def marketcap(self, liquidity_pools, quote_token):
		return self.supply()*self.global_price(liquidity_pools, quote_token)

	def supply(self):
		total = 0
		for h in self._holders.values():
			total += h
		return total

	def holders(self):
		return self._holders.copy()

	def _mint_or_burn(self, holder, qty):
		"""
		Change holder detained quantity of the tokenized token
		Quantity can be positive or negative
		Holder should be a string or it will be changed to
		"""

		# Force holder as string
		holder = str(holder)

		# Round qty
		qty = round(qty, ROUND_VALUE)

		# Add holder to holders if it doesn't exists
		if self._holders.get(holder, None) == None:
			self._holders[holder] = 0

		# Check if it doesn't go below 0
		if (qty + self._holders[holder]) < 0:
			raise TokenFundsError(self._name, qty, holder)

		# Add quantity
		self._holders[holder] += qty

	def mint(self, holder, qty):
		if qty < 0:
			raise TokenMintError(f"Cannot mint a negative value: {qty}")
		self._mint_or_burn(holder, qty)

	def burn(self, holder, qty):
		if qty < 0:
			raise TokenBurnError(f"Cannot burn a negative value: {qty}")
		self._mint_or_burn(holder, -qty)

	def funds(self, holder):
		# Force holder as string
		holder = str(holder)

		# Get quantity and set to zero if it doesn't exists
		qty = self._holders.get(holder, None)
		if qty == None:
			self._holders[holder] = 0
			return 0

		return qty

	def transfer(self, src_holder, dst_holder, qty):
		# Force holders as string
		src_holder = str(src_holder)
		dst_holder = str(dst_holder)

		# Round qty
		qty = round(qty, ROUND_VALUE)

		# Test that src has enough funds
		if (self.funds(src_holder) - qty) < 0 and qty > 0:
			raise TokenFundsError(self, qty, src_holder)
		elif (self.funds(dst_holder) + qty) < 0 and qty < 0:
			raise TokenFundsError(self, qty, dst_holder)

		self._holders[src_holder] = round(self._holders[src_holder] - qty, ROUND_VALUE)
		self._holders[dst_holder] = round(self._holders[dst_holder] + qty, ROUND_VALUE)

	def json(self):
		"""
		Methods that convert the object to JSON
		"""
		json_struct = {
			"name": self._name,
			"holders": self._holders,
			"stablecoin": self._stablecoin
		}
		return json_struct

	def from_json(json_struct):
		"""
		Class method that convert a JSON to the object
		"""
		token = Token(
			json_struct.get("name", "???"),
			stablecoin=json_struct.get("stablecoin", False)
		)

		token._holders = json_struct.get("holders", {})
		return token