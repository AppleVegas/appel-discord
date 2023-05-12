import discord
from discord.ext import commands

class PermissionSystem(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.perms = {}
        self.ownerid = 338460114560483329

    async def get_perm(self, guild_id, member_id, permission) -> bool:
        if permission == "music_player":
            return True
        return False

    async def id_has_permission(self, guild_id, member_id, permission) -> bool:
        if member_id == self.ownerid:
            return True

        guild = await self.client.get_guild(guild_id)
        if guild is None:
            return False

        if guild.owner_id == member_id:
            return True

        member = await guild.get_member(member_id)
        if member is None:
            return False

        if member.guild_permissions.administrator:
            return True

        return await self.get_perm(guild.id, member.id, permission)

    async def has_permission(self, guild: discord.Guild, member: discord.Member, permission: str) -> bool:
        if member.id == self.ownerid:
            return True

        if guild.owner == member:
            return True

        if member.guild_permissions.administrator:
            return True

        return await self.get_perm(guild.id, member.id, permission)
    
    async def check_permission(ctx: commands.Context):
        permission = "manage_permissions"
        if await ctx.bot.get_cog("PermissionSystem").has_permission(ctx.guild, ctx.author, permission):
            return True
        else:
            raise commands.CheckFailure(permission)

    @commands.command(description="Give permission to a role.\nUsage: `grant *role_name* *permission_name*`")
    @commands.check(check_permission)
    async def grant(self, ctx: commands.Context, role, permission):
        await ctx.reply("Not Implemented Yet!")

    @commands.command(description="Remove permission from a role.\nUsage: `remove *role_name* *permission_name*`")
    @commands.check(check_permission)
    async def remove(self, ctx: commands.Context, role, permission):
        await ctx.reply("Not Implemented Yet!")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f"You don't have a permission `{error}`!")
        else: 
            await ctx.reply(error)
        #if isinstance(error, commands.CommandInvokeError):
        #    await ctx.reply(error)

async def setup(client):
    await client.add_cog(PermissionSystem(client))