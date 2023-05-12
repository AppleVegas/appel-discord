import discord
from discord.ext import commands

class Chat(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    async def check_permission(ctx: commands.Context):
        permission = "chat"
        if await ctx.bot.get_cog("PermissionSystem").has_permission(ctx.guild, ctx.author, permission):
            return True
        else:
            raise commands.CheckFailure(permission)

    @commands.command(description="Clear chat messages. User can be specified. Usage: `clear *message_count* *user_mention*`")
    @commands.check(check_permission)
    async def clear(self, ctx: commands.Context, count: int, user: discord.Member = None):
        await ctx.message.delete()
        if user is None:
            deleted = await ctx.channel.purge(limit=count, reason=ctx.author.name)
        else:
            deleted = await ctx.channel.purge(limit=count, check=lambda m: m.author == user, reason=ctx.author.name)
        await ctx.channel.send(f'Deleted {len(deleted)} message(s)', delete_after=2)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f"You don't have a permission `{error}`!")
        else: 
            await ctx.reply(error)
        #if isinstance(error, commands.CommandInvokeError):
        #    await ctx.reply(error)
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "украин" in message.content.lower():
            await message.reply("Страна 404")


async def setup(client):
    await client.add_cog(Chat(client))