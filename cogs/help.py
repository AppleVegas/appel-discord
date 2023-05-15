import discord
from discord.ext import commands

class HelpCommand(commands.HelpCommand):
    def __init__(self, client: commands.Bot):
        self.client = client

class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.client.help_command = HelpCommand(client)


async def setup(client):
    await client.add_cog(Help(client))