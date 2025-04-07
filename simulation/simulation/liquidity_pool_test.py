import os
import unittest

from .token import Token
from .liquidity_pool import LiquidityPool

# Import related errors
from .token import TokenFundsError

from .liquidity_pool import LiquidityPoolInexistantPairError

class TestLiquidityPool(unittest.TestCase):
	def test_init(self):
		"""
		Test the class initizalization
		"""

		# Create a test liquidity_pool
		liquidity_pool = LiquidityPool("TestLiquidityPool")

		# Check that the initialization works
		self.assertIsNotNone(liquidity_pool)

		# Check correct name
		self.assertEqual(str(liquidity_pool), "TestLiquidityPool")

	def test_change_funds(self):
		"""
		Test the class change_funds
		"""

		# Create a test liquidity_pool
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		token = Token("TestToken")

		# Add funds to liquidity_pool and check them
		liquidity_pool.change_funds(token, 500)
		self.assertEqual(liquidity_pool.funds(token), 500)
		self.assertEqual(token.funds(liquidity_pool), 500)

		# Remove funds to liquidity_pool and check them
		liquidity_pool.change_funds(token, -200)
		self.assertEqual(liquidity_pool.funds(token), 300)
		self.assertEqual(token.funds(liquidity_pool), 300)

		# Remove too much funds to liquidity_pool and check them
		with self.assertRaises(TokenFundsError):
			liquidity_pool.change_funds(token, -2000)
		self.assertEqual(liquidity_pool.funds(token), 300)
		self.assertEqual(token.funds(liquidity_pool), 300)

	def test_price(self):
		"""
		Test the class price
		"""

		# Create a test liquidity_pool
		tokenA = Token("TestTokenA")
		tokenB = Token("TestTokenB")
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		liquidity_pool.change_funds(tokenA, 500)
		liquidity_pool.change_funds(tokenB, 250)

		# Check price
		self.assertEqual(liquidity_pool.price(tokenA, tokenA), 1)
		self.assertEqual(liquidity_pool.price(tokenB, tokenB), 1)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.5)
		self.assertEqual(liquidity_pool.price(tokenB, tokenA), 2)

		# Check with no funds
		tokenC = Token("TestTokenC")
		with self.assertRaises(LiquidityPoolInexistantPairError):
			liquidity_pool.price(tokenC, tokenA)
		with self.assertRaises(LiquidityPoolInexistantPairError):
			liquidity_pool.price(tokenA, tokenC)

	def test_swap(self):
		# Create two tokens and associated pair
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		tokenA = Token("TestTokenA")
		tokenB = Token("TestTokenB")
		liquidity_pool.change_funds(tokenA, 500)
		liquidity_pool.change_funds(tokenB, 250)

		# Check initial state
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.5)
		self.assertEqual(liquidity_pool.price(tokenB, tokenA), 2)

		# Add holder in tokens
		tokenA.mint("Alice", 150)

		# Swap base and check liquidity_pool state
		liquidity_pool.swap("Alice", tokenA, 100, tokenB)
		self.assertEqual(tokenA.funds("Alice"), 50)
		self.assertEqual(tokenB.funds("Alice"), 50)
		self.assertEqual(tokenA.funds(liquidity_pool), 600)
		self.assertEqual(tokenB.funds(liquidity_pool), 200)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.333)
		self.assertEqual(liquidity_pool.price(tokenB, tokenA), 3)

		# Reverse swap base and check liquidity_pool state (we see IL!!)
		liquidity_pool.swap("Alice", tokenA, -100, tokenB)
		self.assertEqual(tokenA.funds("Alice"), 150)
		self.assertEqual(tokenB.funds("Alice"), 16.7)
		self.assertEqual(tokenA.funds(liquidity_pool), 500)
		self.assertEqual(tokenB.funds(liquidity_pool), 233.3)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.467)
		self.assertEqual(liquidity_pool.price(tokenB, tokenA), 2.143)

		# Swap quote and check liquidity_pool state
		liquidity_pool.swap("Alice", tokenB, 10, tokenA)
		self.assertEqual(tokenB.funds("Alice"), 6.7)
		self.assertEqual(tokenA.funds("Alice"), 171.43)
		self.assertEqual(tokenB.funds(liquidity_pool), 243.3)
		self.assertEqual(tokenA.funds(liquidity_pool), 478.57)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.508)
		self.assertEqual(liquidity_pool.price(tokenB, tokenA), 1.967)

		# Reverse wap quote and check liquidity_pool state
		liquidity_pool.swap("Alice", tokenB, -10, tokenA)
		self.assertEqual(tokenB.funds("Alice"), 16.7)
		self.assertEqual(tokenA.funds("Alice"), 151.76)
		self.assertEqual(tokenB.funds(liquidity_pool), 233.3)
		self.assertEqual(tokenA.funds(liquidity_pool), 498.24)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.468)
		self.assertEqual(liquidity_pool.price(tokenB, tokenA), 2.136)

		# Check too much swipe
		with self.assertRaises(TokenFundsError):
			liquidity_pool.swap("Alice", tokenA, 2000, tokenB)
		with self.assertRaises(TokenFundsError):
			liquidity_pool.swap("Alice", tokenA, -2000, tokenB)

	def test_swap_stablecoins(self):
		"""
		This will test stablecoins swap
		"""

		# Create two stablecoins, two chains and an liquidity_pool
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		tokenA = Token("stableCoinA", stablecoin=True)
		tokenB = Token("stableCoinB", stablecoin=True)
		tokenC = Token("TestTokenC")
		tokenD = Token("TestTokenD")
		liquidity_pool.change_funds(tokenA, 500)
		liquidity_pool.change_funds(tokenB, 250)
		liquidity_pool.change_funds(tokenC, 100)
		liquidity_pool.change_funds(tokenD, 200)


		tokenA.mint("Alice", 150)

		# Check price
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.5)
		self.assertEqual(liquidity_pool.price(tokenC, tokenA), 5)
		self.assertEqual(liquidity_pool.price(tokenD, tokenA), 2.5)

		# Swap two stablecoins, it should change nothing except Alice funds
		liquidity_pool.swap("Alice", tokenA, 10, tokenB)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.5)
		self.assertEqual(liquidity_pool.price(tokenC, tokenA), 5)
		self.assertEqual(liquidity_pool.price(tokenD, tokenA), 2.5)
		self.assertEqual(tokenB.funds("Alice"), 5)
		self.assertEqual(tokenA.funds("Alice"), 140)

		# Swap stablecoin and normal coin, it should change only the pair on normalcoin/stablecoin
		liquidity_pool.swap("Alice", tokenB, 5, tokenC)
		self.assertEqual(liquidity_pool.price(tokenA, tokenB), 0.5)
		self.assertEqual(liquidity_pool.price(tokenD, tokenA), 2.5)
		self.assertEqual(liquidity_pool.price(tokenC, tokenA), 5.204)
		self.assertEqual(tokenC.funds("Alice"), 2)
		self.assertEqual(tokenB.funds("Alice"), 0)
		self.assertEqual(tokenA.funds("Alice"), 140)

	def test_json(self):
		"""
		This will test the transformation to json and import
		"""

		# Create two tokens and associated pair
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		tokenA = Token("TestTokenA")
		tokenB = Token("TestTokenB")
		liquidity_pool.change_funds(tokenA, 500)
		liquidity_pool.change_funds(tokenB, 250)

		# To JSON
		json_struct = liquidity_pool.json()
		liquidity_pool = None

		# From JSON
		liquidity_pool = LiquidityPool.from_json(json_struct)

		# Check that the initialization works
		self.assertIsNotNone(liquidity_pool)

		# Check that name is correct
		self.assertEqual(str(liquidity_pool), "TestLiquidityPool")

		# Check funds
		self.assertEqual(tokenA.funds(liquidity_pool), 500)
		self.assertEqual(tokenB.funds(liquidity_pool), 250)

	def test_pairs(self):
		"""
		This will test that the pairs are correct
		"""

		# Create few tokens and associated pair
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		tokenA = Token("BA")
		tokenB = Token("BB")
		tokenC = Token("BC")
		tokenD = Token("BD")
		tokens = [ tokenA, tokenB, tokenC, tokenD ]
		liquidity_pool.change_funds(tokenA, 500)
		liquidity_pool.change_funds(tokenB, 250)
		liquidity_pool.change_funds(tokenC, 125)

		expected_result = [
			(tokenA, tokenB),
			(tokenB, tokenA),
			(tokenA, tokenC),
			(tokenC, tokenA),
			(tokenB, tokenC),
			(tokenC, tokenB)
		]
		self.assertEqual(liquidity_pool.pairs(tokens), expected_result)

	def test_available(self):
		"""
		This will test which tokens are marked as available on the liquidity_pool
		"""

		# Create few tokens and associated pair
		liquidity_pool = LiquidityPool("TestLiquidityPool")
		tokenA = Token("BA")
		tokenB = Token("BB")
		tokenC = Token("BC")
		tokenD = Token("BD")
		tokens = [ tokenA, tokenB, tokenC, tokenD ]
		liquidity_pool.change_funds(tokenA, 500)
		liquidity_pool.change_funds(tokenB, 250)
		liquidity_pool.change_funds(tokenC, 125)

		# Check available tokens on this liquidity_pool
		expected_result = [ tokenA, tokenB, tokenC ]
		self.assertEqual(liquidity_pool.available(tokens), expected_result)