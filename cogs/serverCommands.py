#!/usr/bin/python3.8
import discord
from discord.ext import commands
import asyncio
from captcha.image import ImageCaptcha
from random import randint
import json

"""
✔️
❌

# TODO:

pattern function:

@commands.command()
async def name(self, ctx: commands.Context):
    pass

"""

class CommandsServer(commands.Cog):
    """
    COG POUR CERTAINES COMMANDES DE DBM.0
    """

    def __init__(self, bot):
        self.bot = bot
        self.lastOrderNumber = 0

    # COMMANDS :

    @commands.command(name="embedDiplay", aliases=["ed"])
    @commands.has_guild_permissions(administrator=True)
    async def embedDisplayMessage(self, ctx: commands.Context, author_display, *, text):
        await ctx.message.delete()
        embed = discord.Embed(description=text, colour=discord.Colour.blue())
        if author_display == "yes":
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="createcommand", aliases=["cc"])
    async def createCommand(self, ctx: commands.Context):
        # TODO: commande pour passer une commande --> ouvre un channel en me mentionnant

        # CHANNEL TEMPLATE:
        # CHANNEL NAME: order-[ChannelNumberHere]
        # CHANNEL TOPIC: [author.id]


        #DATA
        with open("info.json", "r") as f:
            data = json.load(f)

        guild = ctx.guild
        author = ctx.author
        orderCategory = guild.get_channel(data["orderCategory"])

        #CHECK IF USER HAS ALREADY CREATED A CHANNEL (an order)
        for category in guild.by_category():
            try:
                if category[0].id == data["orderCategory"]:
                    if len(category[1]) > 1:
                        for channel in category[1]:
                            if channel.topic == str(author.id):
                                await ctx.send(f"{author.mention}, you can only create 1 order at a time.", delete_after=3)
                                return
            except AttributeError:
                pass

        #CHECK THE LAST CHANNEL NUMBER
        if self.lastOrderNumber == 0:
            for category in guild.by_category():
                try:
                    if category[0].id == data["orderCategory"]:
                        if len(category[1]) > 1:
                            ticketNumbers = []
                            for channel in category[1]:
                                name, nb = channel.name.split("-")
                                ticketNumbers.append(nb)
                            ticketNumbers.sort()
                            self.lastOrderNumber = ticketNumbers[-1]
                except AttributeError:
                    pass


        #CREATE CHANNEL
        userChannel = await orderCategory.create_text_channel(name=f"order-{self.lastOrderNumber}", topic=str(author.id))
        await userChannel.set_permissions(guild.default_role, read_messages=False,
                                          send_messages=False)
        await userChannel.set_permissions(author, read_messages=True,
                                          send_messages=True)
        self.lastOrderNumber += 1
        await userChannel.send(f"||{(guild.get_role(int(data['adminRole']))).mention}|| \n"
                               f"{author.mention}, wich option ({(guild.get_channel(862068168024391680)).mention})do you"
                               f" want and explain what you want.\n")

    @commands.command(name="close")
    @commands.has_role(861966157569196032)
    async def close(self, ctx):
        channel = ctx.channel
        if "order-" in channel.name:
            await channel.delete(reason="Channel finished")
        else:
            await channel.send("This channel can't be deleted.", delete_after=3)

    @commands.command(name="clear")
    @commands.has_role(861966157569196032)
    async def clear(self, ctx, nb):
        if nb == "all":
            await ctx.channel.purge(limit=len(await ctx.channel.history().flatten()))
        else:
            await ctx.channel.purge(limit=int(nb)+1)


    # EVENT :

    # @commands.Cog.listener()
    # async def on_disconnect(self):
    #     channel = self.bot.get_channel(861667264075661312)
    #     await channel.send("DISCONNECT")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        #RETREIVE DATA
        with open("info.json", "r") as f:
            data = json.load(f)
            welcomeChannelId = data["welcomeChannel"]
            verifyChannelId = data["verifyChannel"]

        #GET CHANNELS
        guild = member.guild
        welcome_channel = guild.get_channel(welcomeChannelId)
        verify_channel = guild.get_channel(verifyChannelId)

        #add role to user
        role = discord.utils.get(guild.roles, id=data["userRole"])
        await member.add_roles(role)

        #send welcome message
        welcomeMessage = f"Hi {member.mention}, welcome in **{guild.name}**. Please go to {verify_channel.mention} to verify."
        await welcome_channel.send(welcomeMessage)

        not_verified = True
        while not_verified:

            #CHECK IF THE USER IS IN THE GUILD
            ids_list = []
            for m in guild.members:
                ids_list.append(m.id)

            if member.id not in ids_list:
                print("MEMBER LEFT THE SERVER")
                return
            else:
                print("Member is in the server")

            #generate random caracters
            word = ""
            for i in range(6):
                word += chr(randint(65, 90)).upper()

            #create captcha
            img = ImageCaptcha(width=320, height=140)
            image = img.generate_image(word)
            verifcationfilename = f"verif{member.id}.jpg" # TODO: CHECK IF IT WORKS
            image.save(f"img/verification/{verifcationfilename}")

            captcha_file = discord.File(f"img/verification/{verifcationfilename}")

            # TODO: ??ajouter un folder pour gérer les images??
            verifyMessage = f"Please {member.mention}, complete this captcha to get acces to the whole server. (90seconds to complete)"
            captcha_sent = await verify_channel.send(verifyMessage, file=captcha_file)

            def check_message(message):
                return message.author.id == member.id and message.channel.id == welcome_channel.id

            try:
                answer = await self.bot.wait_for("message", timeout=90)
                await answer.delete()
            except asyncio.TimeoutError:
                await welcome_channel.send(f"Pls {member.mention}, try again.", delete_after=3)
                await captcha_sent.delete()
                continue

            user_word = ""
            for i in answer.content.strip().upper():
                if i == " " or i == "":
                    pass
                else:
                    user_word += i

            if user_word == word.upper():
                await captcha_sent.delete()
                await verify_channel.send(f"Welcome {member.mention} to **{guild.name}** !", delete_after=2)
                await asyncio.sleep(2.3)
                await member.remove_roles(role)
                not_verified = False
            else:
                await verify_channel.send(f"Pls {member.mention}, try again.", delete_after=3)
                await captcha_sent.delete()
                continue

        # msg = f"Bienvenue {member.mention} dans {guild.name} !!"
        # await welcome_channel.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 862063652671717417 and message.author.id not in [830486558896816128]:
            await asyncio.sleep(2)
            await message.delete()

def setup(bot):
    bot.add_cog(CommandsServer(bot))
    print("CommandsServer cog loaded.")
