#!/usr/bin/python3

# zacks.com parsing module

from html.parser import HTMLParser
import urllib.request
import re
match_last_price = re.compile("([0-9\.]+)")

class Stock():
	def __init__(self, symbol):
		self.symbol = symbol
		self.name = ""
		self.price = ""
		self.change = ""
		self.rating = "-1"
	def update_latest(self):
		zfs = zacksFetchStock()
		zfs.update_stock(self)
	def __repr__(self):
		return "STOCK " + self.name + " (" + self.symbol + ") "\
			+ "Price: " + self.price + " Change: " + self.change + " Ranking: " + self.rating

class zacksFetchStock(HTMLParser):
	unknown = 1
	div_found = 2
	span_found = 3
	end = 4
	p_last_price = 5
	p_net_change = 6
	state = unknown
	
	stock = ""
	
	def update_stock(self, stock):
		self.stock = stock
		if self.stock.symbol == "":
			return
		#response = urllib.request.urlopen('http://www.zacks.com/stock/quote/' + self.stock.symbol)
		#html = str(response.read())
		html = open("test_zacksito", "r").read()
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
			self.stock.rating = data
			# We consider finding the Rank as the end of any processing
			self.state = self.end
		# Price
		elif self.state == self.p_last_price:
			m = match_last_price.search(data)
			if m:
				self.stock.price = m.group(1)
				self.state = self.unknown
		# Change
		elif self.state == self.p_net_change:
			self.stock.change = data.replace(" ", "")
			self.state = self.unknown
		else:
			return
		# print (data)

class zacksFetchTop(HTMLParser):
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
	cur_stock = None
	all_stocks = []

	def handle_starttag(self, tag, attrs):
		if self.state == self.end_of_rows:
			return
		# prev_state = self.state
		# print(tag, str(attrs))
		if self.state == self.unknown and tag == "div" and len(attrs) > 0 and attrs[0][1] == "topmovers_growth":
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
				raise Exception("Parser Error! unexpected td")
		else:
			return
		# print("PREVIOUS state",  prev_state, "new state", self.state)

	def handle_endtag(self, tag):
		if self.state == self.end_of_rows:
			return
		# print("/" + tag)
		# prev_state = self.state
		if tag == "tbody":
			self.state = self.end_of_rows
			# We're done getting all top stocks, now goto individual stocks and update
			for s in self.all_stocks:
				s.update_latest()
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
		if self.state == self.td_name_found:
			self.cur_stock.name = str(data)
		elif self.state == self.td_symbol_found:
			self.cur_stock.symbol = str(data)
		elif self.state == self.td_price_found:
			self.cur_stock.price = str(data)
		elif self.state == self.td_chg_found:
			self.cur_stock.change = str(data)
		else:
			return
		# print("Encountered some data, :", data, " len ", len(data))

	def fetch_parse(self):
		#response = urllib.request.urlopen('http://www.zacks.com/')
		#html = str(response.read())
		#html = html.replace("\\n", "")
		html = open("test_zackcom", "r").read()
		html = html.replace(" class\"truncated_text_two\"", "")
		self.feed(html)
		# print(html)

def get_top_stocks():
	zf = zacksFetchTop()
	zf.fetch_parse()
	return zf.all_stocks

if __name__ == "__main__":
	all = get_top_stocks()
	for s in all:
		print(s)


