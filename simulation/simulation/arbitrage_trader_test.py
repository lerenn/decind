import unittest

from .arbitrage_trader import ArbitrageTrader
from .token import Token
from .liquidity_pool import LiquidityPool

# Import related errors
from .arbitrage_trader import ArbitrageTraderImportError

class TestArbitrageTrader(unittest.TestCase):
	def test_init(self):
		"""
		Test the class initizalization
		"""

		# Create a test arbitrage trader
		token = Token("stableCoin", stablecoin=True)
		at = ArbitrageTrader("ArbitrageTrader", token)

		# Check that the initialization works
		self.assertIsNotNone(at)

		# Check name
		self.assertEqual("ArbitrageTrader", str(at))

	def test_provide_funds(self):
		"""
		Test the class adding funds
		"""

		# Create a test arbitrage trader
		token = Token("stableCoin", stablecoin=True)
		at = ArbitrageTrader("ArbitrageTrader", token)

		# Add funds and check state
		at.provide_funds(1000)
		self.assertEqual(token.funds(at), 1000)
		self.assertEqual(at.profits(), 0)

	def test_arbitrage(self):
		"""
		Test the class balance for profits
		"""

		# Create tokens
		tokenS = Token("stableCoin", stablecoin=True)
		tokenB = Token("BB")
		tokenC = Token("BC")
		tokenD = Token("BD")
		tokens = [ tokenS, tokenB, tokenC, tokenD ]

		# Create liquidity pools
		lpA = LiquidityPool("TestLiquidityPoolA")
		lpA.change_funds(tokenS, 5000)
		lpA.change_funds(tokenB, 250)
		lpA.change_funds(tokenC, 125)
		lpA.change_funds(tokenD, 250)
		lpB = LiquidityPool("TestLiquidityPoolB")
		lpB.change_funds(tokenS, 5000)
		lpB.change_funds(tokenC, 250)
		lpB.change_funds(tokenD, 125)
		lps = [ lpA, lpB ]

		# Create an arbitrage trader
		at = ArbitrageTrader("ArbitrageTrader", tokenS)
		at.provide_funds(2500)

		# Arbitrage
		self.assertNotEqual(
			lpA.price(tokenC, tokenS),
			lpB.price(tokenC, tokenS))
		self.assertNotEqual(
			lpA.price(tokenD, tokenS),
			lpB.price(tokenD, tokenS))
		self.assertEqual(at.arbitrage(tokens, lps), 2)
		self.assertEqual(
			lpA.price(tokenC, tokenS),
			lpB.price(tokenC, tokenS))
		self.assertEqual(
			lpA.price(tokenD, tokenS),
			lpB.price(tokenD, tokenS))

		# Check that it is profitable
		self.assertTrue(at.profits() > 0)

	def test_json(self):
		"""
		This will test the transformation to json and import
		"""

		# Add needed objects
		tokenS = Token("stableCoin", stablecoin=True)
		at = ArbitrageTrader("ArbitrageTrader", tokenS)
		at.provide_funds(2500)

		# Simulate gains
		tokenS.mint(at, 500)

		# Save the arbitrage trader
		json_struct = at.json()
		at = None

		# From JSON but with no proposed tokens
		with self.assertRaises(ArbitrageTraderImportError):
			at = ArbitrageTrader.from_json(json_struct)

		# Real import
		at = ArbitrageTrader.from_json(json_struct, [ tokenS ])

		# Check that the initialization works
		self.assertIsNotNone(at)

		# Check that name is correct
		self.assertEqual(str(at), "ArbitrageTrader")

		# Check provided funds
		self.assertEqual(at.provided_funds(), 2500)
		self.assertEqual(at.profits(), 500)