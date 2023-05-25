import json


class Army:
	def __init__(self, name, player):
		self.name = name
		self.player = player
		self.units = []
		self.counts = {}
		self.getCounts()

class MercArmy(Army):
	def __init__(self, home):
		self.home = home

snee = MercArmy("sneeland", name="hehe")
print(snee.name)