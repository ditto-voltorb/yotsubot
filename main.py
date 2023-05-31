import discord
from discord.ext import commands
from lib import *
import random
import asyncio
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(
    command_prefix='&!', 
    intents=intents,
    activity = discord.Activity(type=discord.ActivityType.watching, name='Yotsuba&!: The Animation')
    )

with open("log.txt", "w") as f:
    f.write("")
    print("log cleared!")

@bot.slash_command(description="Roll a die. Default is a d100.",guild_ids=[1106333118253772850])
async def roll(
    ctx: discord.ApplicationContext,
    dicemax: discord.Option(int, "Maximum possible number to roll.", name="dice-max") = 100
):
    with open("log.txt", "a") as f:
        f.write(f"{ctx.author}: /roll dice-max:{dicemax}")
    print(f"{ctx.author}: /roll dice-max:{dicemax}")
    try:
        roll = random.randint(1, dicemax)
        await ctx.respond("Rolling.")
        await asyncio.sleep(0.5)
        await ctx.edit(content="Rolling..")
        await asyncio.sleep(0.5)
        await ctx.edit(content="Rolling...")
        await asyncio.sleep(0.5)
        await ctx.edit(content=f"Rolling...!\nYou rolled a {roll} {rollReaction(roll)}")
    except:
        with open("log.txt", "a") as f:
            f.write(f"error! {type(Exception)}")

@bot.slash_command(description="Displays info about your or others' countries.",guild_ids=[1106333118253772850])
async def country(
    ctx: discord.ApplicationContext,
    listorpersonorname: discord.Option(str, "Takes `list`, user @, or country name (doesn't have to be whole).", name="list-or-person-or-name",) = False
):
    with open("log.txt", "a") as f:
        f.write(f"{ctx.author}: /country listorpersonorname:{listorpersonorname}")
    print(f"{ctx.author}: /country listorpersonorname:{listorpersonorname}")
    try:
        if listorpersonorname == False:
            auth = ctx.author.id
            if auth in players_dict:
                await ctx.respond(embed=getCountry(ctx, auth))
        else:
            if listorpersonorname == "list":
                view_dict = {
                "Player Countries": players_dict,
                "Non-Player Countries [1-9]": nonplayer_countries[0:9],
                "Non-Player Countries [10-18]": nonplayer_countries[9:18],
                "Non-Player Countries [19-27]": nonplayer_countries[18:],
                "Foreign Nations": foreign_countries
                }
                view = Buttons(embed_list=view_dict, guild=ctx.guild, img="https://cdn.discordapp.com/attachments/1106350205793742858/1112484510030901369/image.png")
                await ctx.respond(embed=view.embed_list[0], view=view)
            elif listorpersonorname[0] == "<":
                auth = ctx.guild.get_member(int(listorpersonorname[2:-1])).id
                await ctx.respond(embed=getCountry(ctx, auth))
            else:
                auth = 0
                listorpersonorname = listorpersonorname.title()
                for i in list(players_dict.keys()):
                    if listorpersonorname in players_dict[i].name:
                        auth = int(players_dict[i].player)
                        await ctx.respond(embed=getCountry(ctx, auth))
                if auth == 0:
                    for i in nonplayer_countries:
                        if listorpersonorname in i.name:
                            auth = i
                            await ctx.respond(embed=getCountry(ctx, auth, nonplayer=True))
                if auth == 0:
                    for i in foreign_countries:
                        if listorpersonorname in i.name:
                            auth = i
                            await ctx.respond(embed=getCountry(ctx, auth, nonplayer=True))
    except:
        with open("log.txt", "a") as f:
            f.write(f"error! {type(Exception)}")

@bot.slash_command(description="Admin only! Give or remove units from a country's reserves.",guild_ids=[1106333118253772850])
async def unit(
    ctx: discord.ApplicationContext,
    person: discord.Option(str, "Takes user @."),
    irregulars: discord.Option(int, "# of irregulars"),
    regulars: discord.Option(int, "# of regulars"),
    tanks: discord.Option(int, "# of tanks"),
    helis: discord.Option(int, "# of helis")
):
    if not isAdmin(ctx.author):
        await ctx.respond("This command is admin only!", ephemeral=True)
    else:
        if person == False:
            player = ctx.author.id
        else:
            player = userIDFromAt(ctx, person)
        added_units = [irregulars, regulars, tanks, helis]
        zipped_units = zip(unit_styles, added_units)
        for i in zipped_units:
            for x in range(i[1]):
                players_dict[player].reserves.append(Unit(i[0]))
        players_dict[player].getReserveCount()
        await ctx.respond("Added units!", ephemeral=True)

@bot.slash_command(description="Create or delete armies of your country.",guild_ids=[1106333118253772850])
async def army(
    ctx: discord.ApplicationContext,
    newdeleterename: discord.Option(str, "Choose to create, delete, or rename an army.", name="new-delete-rename", choices=["new", "delete", "rename"]),
    name: discord.Option(str, "Name of army"),
    new_name: discord.Option(str, "New name for army being renamed", required=False),
    irregulars: discord.Option(int, "# of irregulars") = 0,
    regulars: discord.Option(int, "# of regulars") = 0,
    tanks: discord.Option(int, "# of tanks") = 0,
    helis: discord.Option(int, "# of helis") = 0
):
    with open("log.txt", "a") as f:
        f.write(f"{ctx.author}: /army newdeleterename:{newdeleterename} name:{name} new_name:{new_name} irregulars:{irregulars} regulars:{regulars} tanks:{tanks} helis:{helis}")
    print(f"{ctx.author}: /army newdeleterename:{newdeleterename} name:{name} new_name:{new_name} irregulars:{irregulars} regulars:{regulars} tanks:{tanks} helis:{helis}")
    try:   
        country = players_dict[ctx.author.id]
        if newdeleterename == "new":
            if (irregulars + regulars + tanks + helis) > 10:
                await ctx.respond("Too many units to pack in this army! They have a max size of 10 units.", ephemeral=True)
            else:
                if (country.reserve_count["irregular"][0] >= irregulars) and (country.reserve_count["regular"][0] >= regulars) and (country.reserve_count["tank"][0] >= tanks) and (country.reserve_count["heli"][0] >= helis):
                    country.armies[name] = Army(name, ctx.author.id)
                    injured_irregulars = max(0, irregulars - country.reserve_count["irregular"][2])
                    injured_regulars = max(0, regulars - country.reserve_count["regular"][2])
                    injured_tanks = max(0, tanks - country.reserve_count["tank"][2])
                    injured_helis = max(0, helis - country.reserve_count["heli"][2])
                    country.armies[name].reconstructUnits(
                        irregulars - injured_irregulars, 
                        injured_irregulars,
                        regulars - injured_regulars, 
                        injured_regulars,
                        tanks - injured_tanks, 
                        injured_tanks,
                        helis - injured_helis, 
                        injured_helis,
                    )
                    country.reconstructReserves(
                        country.reserve_count["irregular"][2] - (irregulars - injured_irregulars),
                        country.reserve_count["irregular"][1] - injured_irregulars,
                        country.reserve_count["regular"][2] - (regulars - injured_regulars),
                        country.reserve_count["regular"][1] - injured_regulars,
                        country.reserve_count["tank"][2] - (tanks - injured_tanks),
                        country.reserve_count["tank"][1] - injured_tanks,
                        country.reserve_count["heli"][2] - (helis - injured_helis),
                        country.reserve_count["heli"][1] - injured_helis
                    )
                    await ctx.respond(f"Army `{name}` created!", ephemeral=True)
                else:
                    await ctx.respond("Not enough units in reserves! Delete and reorganize your armies or RP conscription.", ephemeral=True)
        elif newdeleterename == "delete":
            try:
                for i in country.armies[name].units:
                    country.reserves.append(i)
                del country.armies[name]
                await ctx.respond(f"Army `{name}` deleted!", ephemeral=True)
            except KeyError:
                await ctx.respond(f"No army called `{name}`. Did you get the name wrong?", ephemeral=True)
        elif newdeleterename == "rename":
            try:
                country.armies[new_name] = country.armies.pop(name)
                await ctx.respond(f"Army `{name}` renamed to `{new_name}`!", ephemeral=True)
            except KeyError:
                await ctx.respond(f"No army called `{name}`. Did you get the name wrong?", ephemeral=True)
    except:
        with open("log.txt", "a") as f:
            f.write(f"error! {type(Exception)}")

@bot.slash_command(description="Admin only! Debugging tool.",guild_ids=[1106333118253772850])
async def debug(
    ctx: discord.ApplicationContext,
    command: discord.Option(str, "Takes anything."),
):
    if not isAdmin(ctx.author):
        await ctx.respond("This command is admin only!", ephemeral=True)
    else:
        exec(command)


KEY = ""
with open("client_key.txt", "r") as f:
    KEY = f.read()

bot.run(KEY)