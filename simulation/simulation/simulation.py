import json

from .arbitrage_trader import ArbitrageTrader
from .index_fund import IndexFund
from .liquidity_pool import LiquidityPool
from .token import Token

class Simulation(object):
	""" This class represents the simulation process """

	def __init__(self, filename=None):
		self._tokens = {}
		self._liquidity_pools = {}
		self._arbitrage_traders = {}
		self._index_funds = {}

		if filename != None:
			self._load(filename)

	def _load(self, filename):
		"""
		This method will load a simulation from file
		"""
		with open(filename, "r") as f:
			# Read the file to JSON representation of the simulation
			jsonText = f.read()
			json_struct = json.loads(jsonText)

			# Set the simulation from the JSON
			tokens = {}
			for a in json_struct.get("tokens", {}):
				tokens[str(a)] = Token.from_json(a)
			self._tokens = tokens

			# Set the liquidity_pools from the JSON
			liquidity_pools = {}
			for a in json_struct.get("liquidity_pools", {}):
				liquidity_pools[str(a)] = LiquidityPool.from_json(a)
			self._liquidity_pools = liquidity_pools

			# Set the arbitrage traders from JSON
			arbitrage_traders = {}
			for a in json_struct.get("arbitrage_traders", {}):
				arbitrage_traders[str(a)] = ArbitrageTrader.from_json(a, list(tokens.values()))
			self._arbitrage_traders = arbitrage_traders

			# Set the index funds from JSON
			index_funds = {}
			for a in json_struct.get("index_funds", {}):
				index_funds[str(a)] = IndexFund.from_json(a, list(tokens.values()))
			self._index_funds = index_funds

	def _dict_to_json_list(self, d):
		json_list = []
		for e in d.values():
			json_list.append(e.json())
		return json_list

	def save(self, filename):
		"""
		This method will save a simulation to a file
		"""
		with open(filename, "w") as f:
			# Get everything to JSON
			tokens = self._dict_to_json_list(self._tokens)
			lps = self._dict_to_json_list(self._liquidity_pools)
			ats = self._dict_to_json_list(self._arbitrage_traders)
			ind = self._dict_to_json_list(self._index_funds)

			# Build JSON representation of the simulation
			json_struct = {
				"tokens": tokens,
				"liquidity_pools": lps,
				"arbitrage_traders": ats,
				"index_funds": ind,
			}

			# Save to file
			jsonText = json.dumps(json_struct)
			f.write(jsonText)

	def set_token(self, token):
		"""
		This method set an token in the simulation
		Note that tokens should have different names
		"""
		self._tokens[str(token)] = token

	def token(self, name):
		return self._tokens[str(name)]

	def tokens(self):
		return list(self._tokens.keys())

	def set_liquidity_pool(self, liquidity_pool):
		self._liquidity_pools[str(liquidity_pool)] = liquidity_pool

	def liquidity_pool(self, name):
		return self._liquidity_pools[str(name)]

	def liquidity_pools(self):
		return list(self._liquidity_pools.keys())

	def set_arbitrage_trader(self, arbitrage_trader):
		self._arbitrage_traders[str(arbitrage_trader)] = arbitrage_trader

	def arbitrage_trader(self, name):
		return self._arbitrage_traders[str(name)]

	def arbitrage_traders(self):
		return list(self._arbitrage_traders.keys())

	def set_index_fund(self, index_fund):
		self._index_funds[str(index_fund)] = index_fund

	def index_fund(self, name):
		return self._index_funds[str(name)]

	def index_funds(self):
		return list(self._index_funds.keys())