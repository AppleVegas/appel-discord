from dis import disco
from math import perm
import discord
from discord.ext import commands
from zlib import crc32

class PermissionSystem(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.permissions = {}
        self.hashes = {}
        self.ownerid = 338460114560483329
        self.permission = self.register_perm("manage_permissions")
        self.datasystem = self.client.get_cog("DataSystem")
        self.client.check(self.check_permission)

    def is_perm(self, permission):
        return permission in self.permissions

    def register_perm(self, permission):
        if permission in self.permissions:
            return permission
        hashed = crc32(permission.encode())
        self.permissions[permission] = hashed
        self.hashes[hashed] = permission
        print("Registered permission: %s with hash %i" % (permission, hashed))
        return permission

    async def has_perm(self, guild: discord.Guild, member: discord.Member, permission: str) -> bool:
        roles = await self.datasystem.get_permission_roles(guild.id, self.permissions[permission])
        if not roles:
            return False
        for role in roles:
            guild_role = discord.utils.get(guild.roles, id=role[0])
            if not guild_role:
                continue
            if guild_role in member.roles:
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

        return await self.has_perm(guild, member, permission)

    async def has_permission(self, guild: discord.Guild, member: discord.Member, permission: str) -> bool:
        if member.id == self.ownerid:
            return True

        if guild.owner == member:
            return True

        if member.guild_permissions.administrator:
            return True

        return await self.has_perm(guild, member, permission)
    
    async def check_permission(self, ctx: commands.Context):
        if not hasattr(ctx.command.cog, 'permission'):
            return True
        if await self.has_permission(ctx.guild, ctx.author, ctx.command.cog.permission):
            return True
        else:
            await ctx.reply(f"You don't have a permission `{ctx.command.cog.permission}`!")
            return False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            return
        await ctx.reply(error)

    @commands.group(invoke_without_command=True)
    async def perms(self, ctx: commands.Context):
        await ctx.reply("Invalid mode! Modes: add, remove.")

    @perms.command(description="Give permission to a role.\nUsage: `add *role_name* *permission_name*`")
    async def add(self, ctx: commands.Context, role: discord.Role, permission: str):
        if permission not in self.permissions:
            await ctx.reply("No such permission!")
            return 

        if await self.datasystem.has_permission(role.id, self.permissions[permission]):
            await ctx.reply(f"Role `{role.name}` already has permission `{permission}`!")
            return 

        await self.datasystem.save_permission(ctx.guild.id, role.id, self.permissions[permission])
        await ctx.reply(f"Added permission `{permission}` to role `{role.name}`.")

    @perms.command(description="Remove permission from a role.\nUsage: `remove *role_name* *permission_name*`")
    async def remove(self, ctx: commands.Context, role: discord.Role, permission: str):
        if permission not in self.permissions:
            await ctx.reply("No such permission!")
            return 

        if not await self.datasystem.has_permission(role.id, self.permissions[permission]):
            await ctx.reply(f"Role `{role.name}` doesn't have permission `{permission}`!")
            return 

        await self.datasystem.remove_permission(role.id, self.permissions[permission])
        await ctx.reply(f"Removed permission `{permission}` from role `{role.name}`.")

async def setup(client):
    await client.add_cog(PermissionSystem(client))