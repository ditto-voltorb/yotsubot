import discord
from discord.ext import commands
from lib import *

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(
    command_prefix='&!', 
    intents=intents,
    activity = discord.Activity(type=discord.ActivityType.watching, name='Yotsuba&!: The Animation')
    )

@bot.slash_command(description="Displays info about your or others' countries.",guild_ids=[1106333118253772850])
async def country(
    ctx: discord.ApplicationContext,
    listorperson: discord.Option(str, "Takes `list` or user @.", name="list-or-person",) = False
):
    if listorperson == False:
        auth = ctx.author.id
        if auth in players_dict:
            await ctx.respond(embed=getCountry(ctx, auth))
    else:
        if listorperson == "list":
            embed=discord.Embed(title=f"Country List", color=discord.Color.green())
            for key, value in countries_dict.items():
                player = ctx.guild.get_member(int(value.player))
                embed.add_field(name=f"{value.name} {value.flag}", value=f"Led by {player.display_name}\n{value.info}", inline=False)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1106333118794829886/1109320114974773268/mapper.png?width=960&height=678")
            await ctx.respond(embed=embed)
        elif listorperson[0] == "<":
            auth = ctx.guild.get_member(int(listorperson[2:-1])).id
            await ctx.respond(embed=getCountry(ctx, auth))
        elif int(listorperson) in players_dict:
            auth = ctx.guild.get_member(int(listorperson)).id
            await ctx.respond(embed=getCountry(ctx, auth))

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

@bot.slash_command(description="Admin only! Debugging tool.",guild_ids=[1106333118253772850])
async def debug(
    ctx: discord.ApplicationContext,
    command: discord.Option(str, "Takes anything."),
):
    if not isAdmin(ctx.author):
        await ctx.respond("This command is admin only!", ephemeral=True)
    else:
        exec(command)


bot.run('MTEwOTU3MDQ1MjAyMTU3OTgyMA.G3llZc.48D_N0Ol1fcc-h0-yCK0O8O3cmyDkqhBn2y9wY')