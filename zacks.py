#!/usr/bin/python3

# zacks.com parsing module

from generics import Stock
from html.parser import HTMLParser
import urllib.request
import re
match_last_price = re.compile("([0-9\.]+)")

class zacksFetchStock(HTMLParser):
	unknown = 1
	div_found = 2
	span_found = 3
	end = 4
	p_last_price = 5
	p_net_change = 6
	state = unknown
	zstock = None

	def __init__(self, stock):
		assert type(stock) == Stock
		HTMLParser.__init__(self)
		self.stock = stock
	
	def update_stock(self):
		if self.stock.symbol == "":
			return
		response = urllib.request.urlopen('http://www.zacks.com/stock/quote/' + self.stock.symbol)
		html = str(response.read())
		# html = open("test_zacksito", "r").read()
		html = html.replace("\\n", "")
		self.feed(html)
		# print(html)

	def handle_starttag(self, tag, attrs):
		if self.state == self.end:
			return
		# Rank
		if self.state == self.unknown and tag == "div" \
			and len(attrs) > 0 and attrs[0][1] == "zr_rankbox":
			self.state = self.div_found
		elif self.state == self.div_found and tag == "span":
			self.state = self.span_found
		# Price
		elif self.state == self.unknown and tag == "p" and len(attrs) > 0 \
				and attrs[0][1] == "last_price":
			self.state = self.p_last_price
		# Change
		elif self.state == self.unknown and tag == "p" and len(attrs) == 2 \
			and attrs[1][1] == "net_change":
			self.state = self.p_net_change
		else:
			return
		# print(tag, attrs)

	def handle_endtag(self, tag):
		if self.state == self.end:
			return
		# Rank
		if self.state == self.span_found and tag == "span":
			self.state = self.div_found
		elif self.state == self.div_found and tag == "div":
			# Mark finding the rank as the end, no other parsing can happen
			self.state = self.end
		# Price
		elif self.state == self.p_last_price and tag == "p":
			self.state = self.unknown
		# Change
		elif self.state == self.p_net_change and tag == "p":
			self.state = self.unknown
		else:
			return
		# print("/" + tag)

	def handle_data(self, data):
		if self.state == self.end:
			return
		data = data.strip()
		if (len(data) == 0):
			return
		# Rank
		if self.state == self.span_found and data != "&nbsp;":
			z_rating = int(data)
			if z_rating == 1:
				self.stock.set_rating(self.stock.rating.R_BUY)
			elif z_rating <= 3:
				self.stock.set_rating(self.stock.rating.R_HOLD)
			elif z_rating > 3 and self.zrating <= 5:
				self.stock.set_rating(self.stock.rating.R_SELL)
			else:
				raise Exception("Invalid z_rating found during parsing stock")
			# We consider finding the Rank as the end of any processing
			self.state = self.end
		# Price
		elif self.state == self.p_last_price:
			m = match_last_price.search(data)
			if m:
				self.stock.price = float(m.group(1))
				self.state = self.unknown
		# Change
		elif self.state == self.p_net_change:
			self.stock.change = data.replace(" ", "")
			self.state = self.unknown
		else:
			return
		# print (data)

# Don't use directly, derive class and set topmover_cat
class zacksFetchTop(HTMLParser):
	topmover_cat = ""
	unknown = 0
	div_found = 1
	tbody_found = 2
	tr_found = 3
	td_name_found = 4
	td_symbol_found = 5
	td_price_found = 6
	td_chg_found = 7
	end_of_tr = 8
	end_of_rows = 9
	state = unknown

	def __init__(self):
		HTMLParser.__init__(self)
		self.cur_stock = None
		self.all_stocks = []

	def handle_starttag(self, tag, attrs):
		if self.state == self.end_of_rows:
			return
		prev_state = self.state
		if self.state == self.unknown and tag == "div" and len(attrs) > 0 and attrs[0][1] == ("topmovers_" + self.topmover_cat):
			self.state = self.div_found
		elif self.state == self.div_found and tag == "tbody":
			self.state = self.tbody_found
		elif (self.state == self.tbody_found or self.state == self.end_of_tr) and tag == "tr":
			self.state = self.tr_found
		elif self.state == self.tr_found and tag == "td":
			self.cur_stock = Stock("");
			self.all_stocks.append(self.cur_stock)
			self.state = self.td_name_found
		elif tag == "td":
			if self.state == self.td_name_found:
				self.state = self.td_symbol_found
			elif self.state == self.td_symbol_found:
				self.state = self.td_price_found
			elif self.state == self.td_price_found:
				self.state = self.td_chg_found
			else:
				return
		else:
			return
		# print(tag, str(attrs))
		# print("PREVIOUS state",  prev_state, "new state", self.state)

	def handle_endtag(self, tag):
		if self.state == self.end_of_rows or self.state == self.unknown:
			return
		# print("/" + tag)
		prev_state = self.state
		if tag == "tbody":
			self.state = self.end_of_rows
			# We're done getting all top stocks, now goto individual stocks
			# and update the change
			for s in self.all_stocks:
				tf = zacksFetchStock(s)
				tf.update_stock()
			# Only include strong buys
			self.all_stocks = list(filter(lambda x: x.z_rating == 1, self.all_stocks))
		elif tag == "tr":
			self.state = self.end_of_tr
		else:
			return
		# print("PREVIOUS state",  prev_state, "new state", self.state)
		# print("Encountered an end tag :", tag)

	def handle_data(self, data):
		data = data.strip()
		if (len(data) == 0):
			return
		# print("self.state ", self.state, " data", data)
		if self.state == self.td_name_found:
			self.cur_stock.name = str(data)
		elif self.state == self.td_symbol_found:
			self.cur_stock.symbol = str(data)
		elif self.state == self.td_price_found:
			self.cur_stock.price = float(str(data))
		# elif self.state == self.td_chg_found:
		#	self.cur_stock.change = str(data)
		else:
			return
		# print("Encountered some data, :", data, " len ", len(data))

	# Current this only updates the Name, symbol, price and ranking of
	# the top stocks on zack.com, change value is updated directly by Stock class
	def fetch_parse(self):
		response = urllib.request.urlopen('http://www.zacks.com/')
		html = str(response.read())
		html = html.replace("\\n", "")
		# html = open("test_zackcom", "r").read()
		html = html.replace(" class\"truncated_text_two\"", "")
		self.feed(html)
		# print(html)

class zacksFetchTopGrowth(zacksFetchTop):
	topmover_cat = "growth"

class zacksFetchTopIncome(zacksFetchTop):
	topmover_cat = "income"

def get_top_stocks():
	zf_growth = zacksFetchTopGrowth()
	zf_growth.fetch_parse()
	zf_income = zacksFetchTopIncome()
	zf_income.fetch_parse()
	return zf_growth.all_stocks + zf_income.all_stocks

def zacks_update_stock(s):
	assert type(s) == Stock
	tf = zacksFetchStock(s)
	tf.update_stock()
	
def get_rating(s):
	assert type(s) == str and s != ""
	st = Stock(s)
	zacks_update_stock(st)
	return st.rating

if __name__ == "__main__":
	# all = get_top_stocks()
	# for s in all:
	#	print(s)
	r = get_rating("AMZN")
	print(r)


