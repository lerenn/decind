import unittest

# Import tested class
from .token import Token
from .liquidity_pool import LiquidityPool
from .constants import ROUND_VALUE

# Import related errors
from .token import TokenFundsError
from .token import TokenBurnError
from .token import TokenMintError

class TestToken(unittest.TestCase):
	def test_init(self):
		"""
		Test the class initizalization
		"""

		# Check that the initialization works
		self.assertIsNotNone(Token("TestToken"))

	def test_mint_burn(self):
		"""
		Test the change holder quantity method
		"""

		# Create a test token
		token = Token("TestToken")

		# Add holder and gets its quantity back
		token.mint("Alice", 10)
		self.assertEqual(token.funds("Alice"), 10)
		self.assertEqual(token.supply(), 10)

		# Check if holder doesn't exists
		self.assertEqual(token.funds("InexistantHolder"), 0)

		# Add 10 to Alice
		token.mint("Alice", 10)
		self.assertEqual(token.funds("Alice"), 20)
		self.assertEqual(token.supply(), 20)

		# Remove 5 to Alice
		token.burn("Alice", 5)
		self.assertEqual(token.funds("Alice"), 15)
		self.assertEqual(token.supply(), 15)

		# Remove more that what Alice have and check that Alice quantity did not change
		with self.assertRaises(TokenFundsError):
			token.burn("Alice", 1500)
		self.assertEqual(token.funds("Alice"), 15)

		# Add negative value and check no change
		with self.assertRaises(TokenMintError):
			token.mint("Alice", -1)
		self.assertEqual(token.funds("Alice"), 15)

		# Remove negative value and check no change
		with self.assertRaises(TokenBurnError):
			token.burn("Alice", -1)
		self.assertEqual(token.funds("Alice"), 15)

		# Check round
		token.mint("Alice", 1/3)
		self.assertEqual(token.funds("Alice"), 15 + round(1/3, ROUND_VALUE))

	def test_holders(self):
		# Create a test token with 2 holders
		token = Token("TestToken")
		token.mint("Alice", 10)
		token.mint("Bob", 15)

		# Check holders
		holders = token.holders()
		self.assertEqual(holders, {"Alice": 10, "Bob": 15})

		# Check that it doesn't modify the holders
		holders["Alice"] = 50
		self.assertEqual(token.funds("Alice"), 10)

	def test_supply(self):
		"""
		Test the supply fonctionnality
		"""
		# Create a test token with 2 holders
		token = Token("TestToken")
		token.mint("Alice", 250)
		token.mint("Bob", 100)
		token.mint("BrokeHolder", 0)

		# Check supply
		self.assertEqual(token.supply(), 350)

	def test_transfer(self):
		"""
		Test the transfer fonctionnality
		"""
		# Create a test token with 2 holders
		token = Token("TestToken")
		token.mint("Alice", 10)
		token.mint("Bob", 10)
		token.mint("BrokeHolder", 0)

		# Transfer from Alice to Bob and check both quantity
		token.transfer("Alice", "Bob", 10)
		self.assertEqual(token.funds("Alice"), 0)
		self.assertEqual(token.funds("Bob"), 20)

		# Reverse transfer from Alice to Bob and check both quantity
		token.transfer("Alice", "Bob", -5)
		self.assertEqual(token.funds("Alice"), 5)
		self.assertEqual(token.funds("Bob"), 15)

		# Transfer from InexistantUser to Bob and check that Bob quantity did not changed
		with self.assertRaises(TokenFundsError):
			token.transfer("InexistantHolder", "Bob", 5)
		self.assertEqual(token.funds("Bob"), 15)

		# Transfer from BrokeHolder to Bob and check that Bob quantity did not changed
		with self.assertRaises(TokenFundsError):
			token.transfer("BrokeHolder", "Bob", 5)
		self.assertEqual(token.funds("Bob"), 15)

		# Transfer from Bob to NewHolder and check that hodlers have correct quantities
		token.transfer("Bob", "NewHolder", 5)
		self.assertEqual(token.funds("NewHolder"), 5)
		self.assertEqual(token.funds("Bob"), 10)

		# Transfer more that what Alice have to Bob and check that hodlers have correct quantities
		with self.assertRaises(TokenFundsError):
			token.transfer("Alice", "Bob", 50)
		self.assertEqual(token.funds("Alice"), 5)
		self.assertEqual(token.funds("Bob"), 10)

		# Reverse transfer more that what Bob have to Alice and check that hodlers have correct quantities
		with self.assertRaises(TokenFundsError):
			token.transfer("Alice", "Bob", -50)
		self.assertEqual(token.funds("Alice"), 5)
		self.assertEqual(token.funds("Bob"), 10)

		# Transfer round check
		token.transfer("Bob", "Alice", 1/3)
		self.assertEqual(token.funds("Alice"), 5 + round(1/3, ROUND_VALUE))
		self.assertEqual(token.funds("Bob"), 10 - round(1/3, ROUND_VALUE))

	def test_tostr(self):
		"""
		This will test the string representation of the class
		"""

		# Create a test token
		token = Token("TestToken")
		self.assertEqual("TestToken", str(token))

	def test_global_price(self):
		"""
		This will test the global price from the class
		"""

		# Create liquidity pools
		lpA = LiquidityPool("TestLiquidityPoolA")
		lpB = LiquidityPool("TestLiquidityPoolB")
		lpC = LiquidityPool("TestLiquidityPoolC")
		lpD = LiquidityPool("TestLiquidityPoolD")
		lpE = LiquidityPool("TestLiquidityPoolE")
		lps = [ lpA, lpB, lpC, lpD, lpE ]

		# Create token
		token = Token("TestToken")
		lpA.change_funds(token, 500)
		lpB.change_funds(token, 100)
		lpC.change_funds(token, 200)

		# Create a stable coin
		stablecoin = Token("TestStableCoin")
		lpA.change_funds(stablecoin, 500)
		lpB.change_funds(stablecoin, 300)
		lpC.change_funds(stablecoin, 400)
		lpD.change_funds(stablecoin, 100)

		# Check individual prices
		self.assertEqual(lpA.price(token, stablecoin), 1)
		self.assertEqual(lpB.price(token, stablecoin), 3)
		self.assertEqual(lpC.price(token, stablecoin), 2)

		# Check global price
		self.assertEqual(token.global_price(lps, stablecoin), 1.5)

	def test_marketcap(self):
		"""
		This will test the marketcap price from the class
		"""

		# Create liquidity pools
		lpA = LiquidityPool("TestLiquidityPoolA")
		lpB = LiquidityPool("TestLiquidityPoolB")
		lpC = LiquidityPool("TestLiquidityPoolC")
		lpD = LiquidityPool("TestLiquidityPoolD")
		lpE = LiquidityPool("TestLiquidityPoolE")
		lps = [ lpA, lpB, lpC, lpD, lpE ]

		# Create token
		token = Token("TestToken")
		lpA.change_funds(token, 500)
		lpB.change_funds(token, 100)
		lpC.change_funds(token, 200)

		# Create a stable coin
		stablecoin = Token("TestStableCoin")
		lpA.change_funds(stablecoin, 500)
		lpB.change_funds(stablecoin, 300)
		lpC.change_funds(stablecoin, 400)
		lpD.change_funds(stablecoin, 100)

		# Add users
		token.mint("Alice", 1000)
		token.mint("Bob", 1500)

		# Check marketcap
		global_price = token.global_price(lps, stablecoin)
		self.assertEqual(token.marketcap(lps, stablecoin), 3300*global_price)

	def test_json(self):
		"""
		This will test the transformation to json and import
		"""

		# Create a test token
		token = Token("TestToken", stablecoin=True)
		token.mint("Alice", 10)

		# Change to JSON
		json_struct = token.json()

		# Create new token from json
		token_from_json = Token.from_json(json_struct)

		# Check new token
		self.assertEqual("TestToken", str(token))
		self.assertEqual(10, token.supply())
		self.assertEqual(token.funds("Alice"), 10)
		self.assertTrue(token.stablecoin())

	def test_stablecoin(self):
		"""
		This will test the stablecoin functionnality
		"""
		# Create a test token
		token = Token("TestToken", stablecoin=True)

		# There is unlimited funds
		token.mint("Alice", 1000)

		# But you can have holders stripped from inexistant
		with self.assertRaises(TokenFundsError):
			token.burn("Alice", 11000)