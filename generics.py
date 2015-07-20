#!/usr/bin/python3

class Rating():
	R_BUY = 1
	R_HOLD = 2
	R_SELL = 3
	R_UNKNOWN = -1

	def __init__(self, *args):
		if len(args) > 1:
			raise Exception("Only one extra arg allowed")
		if len(args) == 1:
			rating = args[0]
		else:
			rating = self.R_UNKNOWN
		assert type(rating) == int
		assert rating >= self.R_UNKNOWN and rating <= self.R_SELL
		self.rating = rating

	def __repr__(self):
		if self.rating == self.R_BUY:
			return "R_BUY"
		if self.rating == self.R_HOLD:
			return "R_HOLD"
		if self.rating == self.R_SELL:
			return "R_SELL"
		return "R_UNKNOWN"

class Stock():
	def __init__(self, symbol):
		assert type(symbol) == str
		self.symbol = symbol
		self.price = 0.0
		self.rating = Rating()
		self.name = ""
		self.change = ""

	def update_latest(self):
		print("Updating " + self.symbol)
		zfs = zacksFetchStock()
		zfs.update_stock(self)

	def set_rating(self, rating):
		self.rating = Rating(rating)

	def __repr__(self):
		return "STOCK " + self.name + " (" + self.symbol + ") "\
			+ "Price: " + str(self.price) + " Change: " + \
		self.change + " Rating: " + str(self.rating)
