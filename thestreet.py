#!/usr/bin/python3

# tstreet.com parsing module

from generics import Stock
from html.parser import HTMLParser
import urllib.request

# Don't use directly, derive class and set topmover_cat
class tstFetchStock(HTMLParser):
	unknown = 0
	reco_found = 1
	state = unknown

	def __init__(self, stock):
		HTMLParser.__init__(self)
		assert type(stock) == Stock
		self.stock = stock
		self.stock.set_rating(self.stock.rating.R_UNKNOWN)
	
	def handle_starttag(self, tag, attrs):
		return

	def handle_endtag(self, tag):
		return

	def handle_data(self, data):
		data = data.strip()
		if (len(data) == 0):
			return
		if data == "Recommendation:":
			self.state = self.reco_found
		elif self.state == self.reco_found:
			if "Hold" in data:
				self.stock.set_rating(self.stock.rating.R_HOLD)
			elif "Buy" in data:
				self.stock.set_rating(self.stock.rating.R_BUY)
			elif "Sell" in data:
				self.stock.set_rating(self.stock.rating.R_SELL)
			self.state = self.unknown
		else:
			return
		# print("self.state ", self.state, " data", data)
		# print("Encountered some data, :", data, " len ", len(data))

	def update_rating(self):
		# html = open("test_tstcom", "r").read()
		response = urllib.request.urlopen('http://www.thestreet.com/r/ratings/reports/summary/' + self.stock.symbol + '.html')
		html = str(response.read())
		html = html.replace("\\n", "\n")
		html = html.replace("\\r", "")
		html = html.replace("\\'", "'")
		self.feed(html)
		# print(html)

def get_rating(s):
	assert type(s) == str and s != ""
	st = Stock(s)
	tf = tstFetchStock(st)
	tf.update_rating()
	return st.rating

if __name__ == "__main__":
	r = get_rating("AMZN")
	print(r)
