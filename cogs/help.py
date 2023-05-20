import discord
from discord.ext import commands
from typing import Mapping
import itertools
import pretty_help 

class AppelHelpCommand(commands.HelpCommand):
    def __init__(self):
        self = super().__init__()

    async def send_bot_help(self, mapping: Mapping):
        ctx = self.context
        bot = ctx.bot

        def get_cat(command: commands.Command) -> str:
            cog = command.cog
            return cog.qualified_name if cog is not None else "Other"

        filtered = await super().filter_commands(bot.commands, sort=True, key=get_cat)
        to_iterate = itertools.groupby(filtered, key=get_cat)

        outstr = f"**For {ctx.author.mention}**\n\n"
        for category, cmds in to_iterate:
            cmds = sorted(cmds, key=lambda c: c.name)
            joined = '`,\u2002`'.join(c.name for c in cmds)
            outstr = outstr + "**%s:**\n`%s`\n" % (category, joined)
        
        footer = '''
        Type *!help `command`* for more info on a command.
        You can also type *!help `category`* for more info on a category. 
        '''

        em = discord.Embed(title = f"Available Commands", description = outstr + footer,color = discord.Colour.from_rgb(254,31,104))
        await ctx.send(embed = em)
    
    async def send_cog_help(self, cog: commands.Cog):
        return await super().send_cog_help(cog)
    
    async def send_group_help(self, group: commands.Group):
        return await super().send_group_help(group)
    
    async def send_command_help(self, command: commands.Command):
        return await super().send_command_help(command)

class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.menu = pretty_help.AppMenu(timeout=15)
        self.client.help_command = pretty_help.PrettyHelp(
            menu = self.menu, 
            color = discord.Colour.from_rgb(254,31,104),
            no_category="Other",
            index_title="Available Categories") #AppelHelpCommand()


async def setup(client):
    await client.add_cog(Help(client))