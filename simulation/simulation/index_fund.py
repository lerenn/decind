from .token import Token
from .constants import ROUND_VALUE

class IndexFundImportError(Exception):
	"""
	Exception raised for errors related to importation
	"""

	def __init__(self, msg):
		super().__init__(msg)

class IndexFundNotEnoughFundsError(Exception):
	"""
	Exception raised for errors related to not enough funds
	"""

	def __init__(self, fund, token):
		msg = f"{fund} doesn't have enough {token}"
		super().__init__(msg)

class IndexFundNotEnoughMarketFundsError(Exception):
	"""
	Exception raised for errors related to not enough market funds
	"""

	def __init__(self, fund, token, buy=True):
		op = "buy" if buy else "sell"
		msg = f"There is not enough {token} on market for {fund} to {op}"
		super().__init__(msg)

class IndexFund(Token):
	"""
	This class will represent an Index Fund
	"""

	def __init__(self, name, reserve_token):
		self._reserve_token = reserve_token
		super().__init__(name)

	def targeted_repartition(self, tokens, liquidity_pools):
		percentages = {}
		total = 0

		# Get marketcap from each token
		for b in tokens:
			percentages[b] = b.marketcap(liquidity_pools, self._reserve_token)
			total += percentages[b]

		# Calculate the percentages
		for b in percentages.keys():
			percentages[b] /= total

		return percentages

	def mint(self, holder, qty):
		super().mint(holder, qty)
		self._reserve_token.transfer(holder, self, qty)

	def burn(self, holder, qty):
		super().burn(holder, qty)
		self._reserve_token.transfer(holder, self, -qty)
		# TODO Add assets selling if there is not enough reserve token coins

	def value(self, tokens, liquidity_pools):
		total = 0
		for b in tokens:
			price = b.global_price(liquidity_pools, self._reserve_token)
			actual_value = b.funds(self) * price
			total += actual_value
		return total + self._reserve_token.funds(self)

	def _sort_liquidity_pools(self, token, liquidity_pools, reverse=False):
		concerned_liquidity_pools = []
		for e in liquidity_pools:
			if len(e.pairs([token, self._reserve_token])) != 0:
				concerned_liquidity_pools.append(e)

		return sorted(concerned_liquidity_pools, key=lambda e: e.price(token, self._reserve_token), reverse=reverse)

	def _buy_asset(self, token, qty, liquidity_pools):
		# Check if there is enough reserve qty to sell
		reserve_qty_to_sell = round(qty*token.global_price(liquidity_pools, self._reserve_token), ROUND_VALUE)
		reserve_qty = self._reserve_token.funds(self)
		if reserve_qty_to_sell > reserve_qty:
			raise IndexFundNotEnoughFundsError(self, self._reserve_token)

		# Loop over liquidity_pools for asset buying
		for e in self._sort_liquidity_pools(token, liquidity_pools):
			if token.funds(e) < qty:	# If there is not enough on liquidity_pool for all
				if token.funds(e) < 1/ROUND_VALUE:	# If there is even not enough for 1/ROUND_VALUE
					continue
				q = token.funds(e)-1/ROUND_VALUE
				e.swap(self, token, -q, self._reserve_token)
				qty -= q
			else:																		# If there is enough on liquidity_pool
				e.swap(self, token, -qty, self._reserve_token)
				return

		# Should not get there
		raise IndexFundNotEnoughMarketFundsError(self, token, True)

	def _sell_asset(self, token, qty, liquidity_pools):
		# Loop over liquidity_pools for asset selling
		for e in self._sort_liquidity_pools(token, liquidity_pools, reverse=True):
			qty *= token.global_price(liquidity_pools, self._reserve_token)
			if self._reserve_token.funds(e) < qty:	# If there is not enough on liquidity_pool for all
				if self._reserve_token.funds(e) < 1/ROUND_VALUE:	# If there is even not enough for 1/ROUND_VALUE
					continue
				q = self._reserve_token.funds(e)-1/ROUND_VALUE
				e.swap(self, self._reserve_token, -q, token)
				qty -= q
			else: 																								# If there is enough on liquidity_pool
				e.swap(self, self._reserve_token, -qty, token)
				return

		# Should not get there
		raise IndexFundNotEnoughMarketFundsError(self, token, False)

	def balance(self, tokens, liquidity_pools):
		total_value = self.value(tokens, liquidity_pools)
		percentages = self.targeted_repartition(tokens, liquidity_pools)
		differences = {}

		# Get what needs to be sell/bought
		for (b, p) in percentages.items():
			price = b.global_price(liquidity_pools, self._reserve_token)
			actual_value = b.funds(self) * price
			target_value = p * total_value
			differences[b] = (target_value - actual_value) / price

		# Sell what needs to be sold
		for (b, d) in differences.items():
			if d < 0:
				self._sell_asset(b, -d, liquidity_pools)

		# Buy what needs to be bought
		if self._reserve_token.funds(self) > 10**(-ROUND_VALUE):
			for (b, d) in differences.items():
				if d > 0:
					self._buy_asset(b, d, liquidity_pools)

	def json(self):
		"""
		Methods that convert the object to JSON
		"""
		json_struct = super().json()
		json_struct["reserve_token"] = str(self._reserve_token)
		return json_struct

	def from_json(json_struct, tokens=[]):
		"""
		Class method that convert a JSON to the object
		"""

		reserve_token = None
		for t in tokens:
			if str(t) == json_struct["reserve_token"]:
				reserve_token = t

		if reserve_token is None:
			raise IndexFundImportError(
				" ".join([f"Reserve token '{json_struct['reserve_token']}'",
					f"for the index fund '{json_struct['name']}' was not provided"]))

		fund = IndexFund(
			json_struct["name"],
			reserve_token,
		)

		fund._holders = json_struct.get("holders", {})
		return fund