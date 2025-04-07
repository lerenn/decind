import os
import unittest

from .arbitrage_trader import ArbitrageTrader
from .index_fund import IndexFund
from .liquidity_pool import LiquidityPool
from .simulation import Simulation
from .token import Token

class TestSimulation(unittest.TestCase):
	def test_init(self):
		"""
		Test the class initizalization
		"""

		# Check that the initialization works
		self.assertIsNotNone(Simulation())

	def test_tokens(self):
		"""
		Test the class tokens methods
		"""

		# Create a simulation
		sim = Simulation()

		# Set a token
		token = Token("TestToken")
		token2 = Token("TestToken2")
		sim.set_token(token)
		sim.set_token(token2)
		self.assertEqual(token, sim.token(token))
		self.assertEqual(token2, sim.token(token2))

		# Get a non existant token
		with self.assertRaises(KeyError):
			sim.token("InexistantToken")

		# Get list of tokens name
		self.assertEqual([ "TestToken", "TestToken2" ], sim.tokens())

	def test_liquidity_pools(self):
		"""
		Test the class liquidity_pools methods
		"""

		# Create a simulation
		sim = Simulation()

		# Set an liquidity pool
		lp = LiquidityPool("TestLiquidityPool")
		lp2 = LiquidityPool("TestLiquidityPool2")
		sim.set_liquidity_pool(lp)
		sim.set_liquidity_pool(lp2)
		self.assertEqual(lp, sim.liquidity_pool(lp))
		self.assertEqual(lp2, sim.liquidity_pool(lp2))

		# Get a non existant token
		with self.assertRaises(KeyError):
			sim.liquidity_pool("InexistantLiquidityPool")

		# Get list of tokens name
		self.assertEqual(
			[ "TestLiquidityPool", "TestLiquidityPool2" ],
			sim.liquidity_pools())

	def test_arbitrage_trader(self):
		"""
		Test the class arbitrage_trader methods
		"""

		# Create a simulation
		sim = Simulation()

		# Set an liquidity pool
		token = Token("TestToken")
		at = ArbitrageTrader("TestArbitrageTrader", token)
		token2 = Token("TestToken2")
		at2 = ArbitrageTrader("TestArbitrageTrader2", token2)
		sim.set_arbitrage_trader(at)
		sim.set_arbitrage_trader(at2)
		self.assertEqual(at, sim.arbitrage_trader(at))
		self.assertEqual(at2, sim.arbitrage_trader(at2))

		# Get a non existant token
		with self.assertRaises(KeyError):
			sim.arbitrage_trader("InexistantArbitrageTrader")

		# Get list of tokens name
		self.assertEqual(
			[ "TestArbitrageTrader", "TestArbitrageTrader2" ],
			sim.arbitrage_traders())

	def test_index_fund(self):
		"""
		Test the class index_fund methods
		"""

		# Create a simulation
		sim = Simulation()

		# Set an liquidity pool
		token = Token("TestToken", stablecoin=True)
		fund = IndexFund("TestIndexFund", token)
		token2 = Token("TestToken2", stablecoin=True)
		fund2 = IndexFund("TestIndexFund2", token2)
		sim.set_index_fund(fund)
		sim.set_index_fund(fund2)
		self.assertEqual(fund, sim.index_fund(fund))
		self.assertEqual(fund2, sim.index_fund(fund2))

		# Get a non existant token
		with self.assertRaises(KeyError):
			sim.index_fund("InexistantIndexFund")

		# Get list of tokens name
		self.assertEqual(
			[ "TestIndexFund", "TestIndexFund2" ],
			sim.index_funds())

	def test_load_save(self):
		"""
		Test the class load and save
		"""

		# Create a simulation
		sim = Simulation()

		# Set an token
		token = Token("TestToken")
		token.mint("Alice", 10)
		sim.set_token(token)

		# Set an liquidity pool
		lp = LiquidityPool("TestLiquidityPool")
		lp.change_funds(token, 500)
		token2 = Token("TestToken2")
		sim.set_token(token2)
		lp.change_funds(token2, 250)
		sim.set_liquidity_pool(lp)

		# Set an arbitrage trader
		at = ArbitrageTrader("ArbitrageTrader", token)
		at.provide_funds(2500)
		sim.set_arbitrage_trader(at)

		# Set an index fund
		fund = IndexFund("TestIndexFund", token)
		sim.set_index_fund(fund)

		# Save the simulation
		filename = "test-simulation.json"
		sim.save(filename)

		# Load new simulation
		new_sim = Simulation(filename)

		# Check new simulation
		self.assertIsNotNone(Simulation())

		# Check token new simulation
		token = sim.token("TestToken")
		self.assertIsNotNone(token)
		self.assertEqual("TestToken", str(token))
		self.assertEqual(3010, token.supply())
		self.assertEqual(token.funds("Alice"), 10)

		# Check liquidity pool
		token2 = sim.token("TestToken2")
		lp = sim.liquidity_pool("TestLiquidityPool")
		self.assertEqual(lp.price(token, token2), 0.5)
		self.assertEqual(lp.price(token2, token), 2)

		# Check arbitrage trader
		at = sim.arbitrage_trader("ArbitrageTrader")
		self.assertEqual(2500, at.provided_funds())

		# Check index fund
		ind = sim.index_fund("TestIndexFund")
		self.assertEqual("TestIndexFund", str(ind))

		# Remove the file
		# os.remove(filename)
