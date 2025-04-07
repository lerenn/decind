import os
import unittest

from .constants import ROUND_VALUE

from .arbitrage_trader import ArbitrageTrader
from .index_fund import IndexFund
from .liquidity_pool import LiquidityPool
from .token import Token

# Import related errors
from .index_fund import IndexFundImportError
from .token import TokenFundsError

class TestIndexFund(unittest.TestCase):
	def test_init(self):
		"""
		Test the class initizalization
		"""

		# Create a test liquidity_pool
		stablecoin = Token("TestStableCoin", stablecoin=True)
		fund = IndexFund("TestIndexFund", stablecoin)

		# Check that the initialization works
		self.assertIsNotNone(fund)

		# Check correct name
		self.assertEqual(str(fund), "TestIndexFund")

	def test_targeted_repartition(self):
		"""
		Test the class targeted_repartition
		"""

		# Create liquidity pools
		lpA = LiquidityPool("TestLiquidityPoolA")
		lpB = LiquidityPool("TestLiquidityPoolB")
		lpC = LiquidityPool("TestLiquidityPoolC")
		lps = [ lpA, lpB, lpC ]

		# Create tokens
		tokenA = Token("TestTokenA")
		lpA.change_funds(tokenA, 500)
		lpB.change_funds(tokenA, 250)
		lpC.change_funds(tokenA, 1000)

		tokenB = Token("TestTokenB")
		lpA.change_funds(tokenB, 100)
		lpB.change_funds(tokenB, 150)
		lpC.change_funds(tokenB, 20)

		tokenC = Token("TestTokenC")
		lpA.change_funds(tokenC, 500)
		lpB.change_funds(tokenC, 600)
		lpC.change_funds(tokenC, 400)

		tokens = [ tokenA, tokenB, tokenC]

		# Create a stable coin
		stablecoin = Token("TestStableCoin", stablecoin=True)
		lpA.change_funds(stablecoin, 500)
		lpB.change_funds(stablecoin, 300)
		lpC.change_funds(stablecoin, 400)

		# Add users
		tokenA.mint("Alice", 500)
		tokenB.mint("Bob", 1000)
		tokenC.mint("Claire", 2000)

		# Create a test liquidity_pool
		fund = IndexFund("TestIndexFund", stablecoin)

		# Check targeted repartition
		repartition = fund.targeted_repartition(tokens, lps)
		self.assertEqual(repartition[tokenA], 0.15448188175460903)
		self.assertEqual(repartition[tokenB], 0.5651621106166561)
		self.assertEqual(repartition[tokenC], 0.2803560076287349)

	def test_reserve(self):
		"""
		Test the reserve of the fund
		"""

		# Create a test liquidity_pool
		stablecoin = Token("TestStableCoin", stablecoin=True)
		fund = IndexFund("TestIndexFund", stablecoin)

		# Add funds
		stablecoin.mint("Alice", 500)
		stablecoin.mint("Bob", 1000)
		stablecoin.mint("Claire", 2000)
		fund.mint("Alice", 500)
		fund.mint("Bob", 1000)
		fund.mint("Claire", 2000)

		# Check tokens
		self.assertEqual(fund.funds("Alice"), 500)
		self.assertEqual(fund.funds("Bob"), 1000)
		self.assertEqual(fund.funds("Claire"), 2000)

		# Check reserve
		self.assertEqual(stablecoin.funds(fund), 3500)

		# Cash out from Alice
		fund.burn("Alice", 500)
		with self.assertRaises(TokenFundsError):
			fund.burn("Bob", 1500)
		self.assertEqual(stablecoin.funds("Alice"), 500)
		self.assertEqual(fund.funds("Alice"), 0)
		self.assertEqual(fund.funds("Bob"), 1000)
		self.assertEqual(fund.funds("Claire"), 2000)
		self.assertEqual(stablecoin.funds(fund), 3000)

	def test_value(self):
		"""
		Test the value of the fund
		"""
		# Create a test liquidity_pool
		stablecoin = Token("TestStableCoin", stablecoin=True)
		fund = IndexFund("TestIndexFund", stablecoin)

		# Add funds
		stablecoin.mint("Alice", 500)
		stablecoin.mint("Bob", 1000)
		stablecoin.mint("Claire", 2000)
		fund.mint("Alice", 500)
		fund.mint("Bob", 1000)
		fund.mint("Claire", 2000)

		# Check value
		self.assertEqual(fund.value([], []), stablecoin.funds(fund))

		# Add funds to the index
		liquidity_pool = LiquidityPool("TestLiquidityPoolA")
		liquidity_pool.change_funds(stablecoin, 500)
		tokenA = Token("TestTokenA")
		tokenA.mint(fund, 700)
		liquidity_pool.change_funds(tokenA, 500)
		tokenB = Token("TestTokenA")
		tokenB.mint(fund, 700)
		liquidity_pool.change_funds(tokenB, 500)

		self.assertEqual(fund.value([tokenA, tokenB], [liquidity_pool]), 3500 + 700 + 700)


	def test_balance(self):
		"""
		Test the class balance
		"""

		# Create liquidity pools
		lpA = LiquidityPool("TestLiquidityPoolA")
		lpB = LiquidityPool("TestLiquidityPoolB")
		lpC = LiquidityPool("TestLiquidityPoolC")
		lpD = LiquidityPool("TestLiquidityPoolD")
		lps = [ lpA, lpB, lpC, lpD ]

		# Create tokens
		tokenA = Token("TestTokenA")
		lpA.change_funds(tokenA, 10000)
		lpB.change_funds(tokenA, 5000)
		lpC.change_funds(tokenA, 10000)

		tokenB = Token("TestTokenB")
		lpA.change_funds(tokenB, 2000)
		lpB.change_funds(tokenB, 5000)
		lpC.change_funds(tokenB, 2000)

		tokenC = Token("TestTokenC")
		lpA.change_funds(tokenC, 3000)
		lpB.change_funds(tokenC, 3000)
		lpC.change_funds(tokenC, 3000)

		tokens = [ tokenA, tokenB, tokenC]

		# Create a stable coin
		stablecoin = Token("TestStableCoin", stablecoin=True)
		lpA.change_funds(stablecoin, 1000)
		lpB.change_funds(stablecoin, 500)
		lpC.change_funds(stablecoin, 1000)

		# Add users
		stablecoin.mint("Alice", 500)
		stablecoin.mint("Bob", 1000)
		stablecoin.mint("Claire", 2000)

		tokenA.mint("Unknown", 5000000)
		tokenB.mint("Unknown", 2000000)
		tokenC.mint("Unknown", 1000000)

		# Create a test liquidity_pool
		fund = IndexFund("TestIndexFund", stablecoin)

		# Add funds
		fund.mint("Alice", 500)
		fund.mint("Bob", 1000)
		fund.mint("Claire", 2000)

		# Create an arbitrage trader
		at = ArbitrageTrader("ArbitrageTrader", stablecoin)
		at.provide_funds(2500)

		repartition = {}
		max_loop = 10000
		for i in range(0, max_loop+1):
			# Arbitrage the markets
			at.arbitrage(tokens, lps)

			# Get informations before balance to check result
			priceABeforeBalance = tokenA.global_price(lps, stablecoin)
			priceBBeforeBalance = tokenB.global_price(lps, stablecoin)
			priceCBeforeBalance = tokenC.global_price(lps, stablecoin)
			targeted_repartition = fund.targeted_repartition(tokens, lps)

			# Check if we need to go out
			if repartition == targeted_repartition:
				break

			# Do the balance
			fund.balance(tokens, lps)

			# Check result with ROUND_VALUE error
			qtyA = tokenA.funds(fund)*priceABeforeBalance
			qtyB = tokenB.funds(fund)*priceBBeforeBalance
			qtyC = tokenC.funds(fund)*priceCBeforeBalance
			total = qtyA+qtyB+qtyC
			partA = round(qtyA/total, ROUND_VALUE)
			partB = round(qtyB/total, ROUND_VALUE)
			partC = round(qtyC/total, ROUND_VALUE)
			self.assertTrue(
				round(targeted_repartition[tokenA], ROUND_VALUE) <= partA + 10**(-ROUND_VALUE) and
				round(targeted_repartition[tokenA], ROUND_VALUE) >= partA - 10**(-ROUND_VALUE))
			self.assertTrue(
				round(targeted_repartition[tokenB], ROUND_VALUE) <= partB + 10**(-ROUND_VALUE) and
				round(targeted_repartition[tokenB], ROUND_VALUE) >= partB - 10**(-ROUND_VALUE))
			self.assertTrue(
				round(targeted_repartition[tokenC], ROUND_VALUE) <= partC + 10**(-ROUND_VALUE) and
				round(targeted_repartition[tokenC], ROUND_VALUE) >= partC - 10**(-ROUND_VALUE))

			# Save the repartition
			repartition = targeted_repartition

			# Check if have done too much loops
			self.assertTrue(i < max_loop)

	def test_json(self):
		"""
		This will test the transformation to json and import
		"""

		# Add needed objects
		stablecoin = Token("TestStableCoin", stablecoin=True)
		fund = IndexFund("TestIndexFund", stablecoin)

		# Add funds to Alice
		stablecoin.mint("Alice", 500)
		fund.mint("Alice", 500)
		self.assertEqual(stablecoin.funds("Alice"), 0)
		self.assertEqual(fund.funds("Alice"), 500)

		# Save the fund
		json_struct = fund.json()
		fund = None

		# From JSON but with no proposed tokens
		with self.assertRaises(IndexFundImportError):
			fund = IndexFund.from_json(json_struct)

		# Real import
		fund = IndexFund.from_json(json_struct, [ stablecoin ])

		# Check that the initialization works
		self.assertIsNotNone(fund)

		# Check that name is correct
		self.assertEqual(str(fund), "TestIndexFund")

		# Check Alice funds
		self.assertEqual(stablecoin.funds("Alice"), 0)
		self.assertEqual(fund.funds("Alice"), 500)
