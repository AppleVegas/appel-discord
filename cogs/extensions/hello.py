import discord
from discord.ext import commands

class ModerationCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.command(name="kick")
    async def my_kick_command(self, ctx):
        await ctx.reply("Dicks on you " + ctx.author.name)

async def setup(client):
    await client.add_cog(ModerationCommands(client))