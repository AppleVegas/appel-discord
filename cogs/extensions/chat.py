import discord
from discord.ext import commands

class Chat(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.description = "Manage chat."
        self.client = client
        self.permission = self.client.get_cog("PermissionSystem").register_perm("manage_chat")
    
    @commands.command(help="Clear chat messages. \n\nFirst argument has to be the number of messages.\nUser can be mentioned as second argument.")
    async def clear(self, ctx: commands.Context, count: int, user: discord.Member = None):
        await ctx.message.delete()
        if user is None:
            deleted = await ctx.channel.purge(limit=count, reason=ctx.author.name)
        else:
            deleted = await ctx.channel.purge(limit=count, check=lambda m: m.author == user, reason=ctx.author.name)
        await ctx.channel.send(f'Deleted {len(deleted)} message(s)', delete_after=2)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        pass


async def setup(client):
    await client.add_cog(Chat(client))