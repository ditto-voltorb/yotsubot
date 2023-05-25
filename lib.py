import discord
from discord.ext import commands
import json


unit_dice = {
	"irregular": 0.1,
	"regular": 0.2,
	"tank": 1,
	"heli": 0,
}
unit_styles = list(unit_dice.keys())
unit_casualities = {
	"irregular": 0,
	"regular": 0,
	"tank": 0,
	"heli": 0.25,
}

class Country:
	def __init__(self, name, player, image, flag, info="", reserves=[]):
		self.name = name
		self.player = player
		self.info = info
		self.armies = {}
		self.image = image
		self.flag = flag
		self.reserves = reserves
		self.reserve_count = {}
		self.getReserveCount()

	def getReserveCount(self):
		reserves_dict = {k: (sum(u.style == k for u in self.reserves),
			sum((u.style == k) and (u.injured == True) for u in self.reserves),
			sum((u.style == k) and (u.injured == False) for u in self.reserves)) for k in unit_styles}
		self.reserve_count = reserves_dict

	def reconstructReserves(self, irg, inj_irg, reg, inj_reg, tnk, inj_tnk, hel, inj_hel):
		self.reserves = []
		self.reserves += [Unit("irregular") for _ in range(irg)]
		self.reserves += [Unit("irregular", True) for _ in range(inj_irg)]
		self.reserves += [Unit("regular") for _ in range(reg)]
		self.reserves += [Unit("regular", True) for _ in range(inj_reg)]
		self.reserves += [Unit("tank") for _ in range(tnk)]
		self.reserves += [Unit("tank", True) for _ in range(inj_tnk)]
		self.reserves += [Unit("heli") for _ in range(hel)]
		self.reserves += [Unit("heli", True) for _ in range(inj_hel)]
		self.getReserveCount()

class Army:
	def __init__(self, name, player):
		self.name = name
		self.player = player
		self.units = []
		self.counts = {}
		self.getCounts()

	def getCounts(self):
		counts_dict = {k: (sum(u.style == k for u in self.units),
			sum((u.style == k) and (u.injured == True) for u in self.units)) for k in unit_styles}
		self.counts = counts_dict

	def reconstructUnits(self, irg, inj_irg, reg, inj_reg, tnk, inj_tnk, hel, inj_hel):
		self.units = []
		self.units += [Unit("irregular") for _ in range(irg)]
		self.units += [Unit("irregular", True) for _ in range(inj_irg)]
		self.units += [Unit("regular") for _ in range(reg)]
		self.units += [Unit("regular", True) for _ in range(inj_reg)]
		self.units += [Unit("tank") for _ in range(tnk)]
		self.units += [Unit("tank", True) for _ in range(inj_tnk)]
		self.units += [Unit("heli") for _ in range(hel)]
		self.units += [Unit("heli", True) for _ in range(inj_hel)]
		self.getCounts()

class MercArmy(Army):
	def __init__(self, name, owner=None, home=None, wandering=False):
		self.name = name
		self.owner = owner
		self.home = home
		self.wandering = wandering
		self.old_owner = None
		self.units = []
		self.counts = {}
		self.getCounts()

class Unit:
	def __init__(self, style, injured=False):
		self.style = style
		self.dice_mod = unit_dice[style]
		self.casualities_mod = unit_casualities[style]
		self.injured = injured

countries_dict = {}
players_dict = {}
with open("countries.json", "r", encoding='utf-8-sig') as f:
	y = json.loads(f.read())
	for i in y["countries"]:
		countries_dict[i] = Country(y["countries"][i]["name"], y["countries"][i]["player"],
			y["countries"][i]["image"], y["countries"][i]["flag"], y["countries"][i]["info"])
		players_dict[int(y["countries"][i]["player"])] = countries_dict[i]

def getCountry(ctx, player):
	embed=discord.Embed(title=f"{players_dict[player].name}",color=discord.Color.green())
	info = players_dict[player].info.split("\n")
	info_list = []
	for i in info:
		info_list.append(i.split("** "))
	for i in info_list:
		embed.add_field(name=f"{i[0][2:]}", value=f"{i[1]}", inline=True)
	players_dict[player].getReserveCount()
	reserves_msg = ""
	for k, v in players_dict[player].reserve_count.items():
		reserves_msg += f"{k}: {v[0]} ({v[1]} injured)\n"
	embed.add_field(name="Reserves", value=reserves_msg, inline=True)
	armies_msg = ""
	for i in players_dict[player].armies:
		temp_dict = players_dict[player].armies[i].counts
		armies_msg += f"`{i}` ({temp_dict['irregular'][0]}/{temp_dict['regular'][0]}/{temp_dict['tank'][0]}/{temp_dict['heli'][0]})\n"
	embed.add_field(name="Armies", value=armies_msg, inline=True)
	embed.set_author(name=ctx.guild.get_member(int(player)).display_name, icon_url=ctx.guild.get_member(int(player)).avatar.url)
	embed.set_thumbnail(url=f"{players_dict[player].image}")
	return embed

def isAdmin(person):
	stringed_roles = [str(x) for x in person.roles]
	if ("Game Master" in stringed_roles) or ("Code Creature" in stringed_roles):
		return True
	return False

def userIDFromAt(ctx, at):
	return ctx.guild.get_member(int(at[2:-1])).id