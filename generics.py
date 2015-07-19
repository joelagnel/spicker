#!/usr/bin/python3

class Stock():
	R_BUY = 1
	R_HOLD = 2
	R_SELL = 3
	R_UNKNOWN = -1

	def get_rating(self):
		if self.rating == self.R_BUY:
			return "R_BUY"
		if self.rating == self.R_HOLD:
			return "R_HOLD"
		if self.rating == self.R_SELL:
			return "R_SELL"
		return "R_UNKNOWN"

	def __init__(self, symbol):
		self.symbol = symbol
		self.price = 0.0
		self.rating = self.R_UNKNOWN
		self.name = ""
		self.change = ""

	def update_latest(self):
		print("Updating " + self.symbol)
		zfs = zacksFetchStock()
		zfs.update_stock(self)

	def __repr__(self):
		return "STOCK " + self.name + " (" + self.symbol + ") "\
			+ "Price: " + str(self.price) + " Change: " + \
		self.change + " Rating: " + self.get_rating()
