import discord
from discord.ext import commands
from zlib import crc32

class PermissionSystem(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.description = "Manage permissions."
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
        return await self.has_permission(ctx.guild, ctx.author, ctx.command.cog.permission)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            if hasattr(ctx.command.cog, 'permission'):
                await ctx.reply(f"You don't have a permission `{ctx.command.cog.permission}`!")
            return
        print(error)
        await ctx.send(error)

    def get_role_by_name(self, guild: discord.Guild, role_name: str) -> discord.Role:
        if role_name == "everyone":
            role = guild.default_role
        else:
            role = discord.utils.get(guild.roles, name=role_name)
        return role

    def get_role_by_id(self, guild: discord.Guild, role_id: int) -> discord.Role:
        role = discord.utils.get(guild.roles, id=role_id)
        return role

    @commands.group(invoke_without_command=True, help = "Manage/List permissions.")
    async def perms(self, ctx: commands.Context):
        await ctx.reply("Invalid subcommand! Valid ones are: `add`, `remove`, `list`, `roles`.")

    @perms.command(help = "Add permission to a role. \n\nEveryone role - 'everyone'")
    async def add(self, ctx: commands.Context, role_name: str, permission: str):
        role = self.get_role_by_name(ctx.guild, role_name)
        if role is None:
            await ctx.reply(f"Role {role_name} not found!")
            return
        if permission == "all":
            perms = []
            for perm in self.hashes:
                if await self.datasystem.has_permission(role.id, perm):
                    continue
                await self.datasystem.save_permission(ctx.guild.id, role.id, perm)
                perms.append(self.hashes[perm])
            
            if not perms:
                await ctx.reply(f"Role `{role.name}` already has all permissions!")
                return
                
            await ctx.reply(f"Added permissions `{', '.join(perms)}` to role `{role.name}`.")
            return
        
        if permission not in self.permissions:
            await ctx.reply("No such permission!")
            return 

        if await self.datasystem.has_permission(role.id, self.permissions[permission]):
            await ctx.reply(f"Role `{role.name}` already has permission `{permission}`!")
            return 

        await self.datasystem.save_permission(ctx.guild.id, role.id, self.permissions[permission])
        await ctx.reply(f"Added permission `{permission}` to role `{role.name}`.")

    @perms.command(help = "Remove permission from a role. \n\nEveryone role - 'everyone'")
    async def remove(self, ctx: commands.Context, role_name: str, permission: str):
        role = self.get_role_by_name(ctx.guild, role_name)
        if role is None:
            await ctx.reply(f"Role {role_name} not found!")
            return

        if permission == "all":
            await self.datasystem.remove_all_role_permissions(role.id)
            await ctx.reply(f"Removed all permissions from role {role.name}!")
            return 

        if permission not in self.permissions:
            await ctx.reply("No such permission!")
            return 

        if not await self.datasystem.has_permission(role.id, self.permissions[permission]):
            await ctx.reply(f"Role `{role.name}` doesn't have permission `{permission}`!")
            return 

        await self.datasystem.remove_permission(role.id, self.permissions[permission])
        await ctx.reply(f"Removed permission `{permission}` from role `{role.name}`.")
    
    @perms.command(help = "List of permissions. \n\nRole name can me specified as second argument to list all permissions for a specific role.\nRole name can be 'all' to list permissions for all roles.")
    async def list(self, ctx: commands.Context, role_name: str = None):
        if role_name is None:
            em = discord.Embed(title = "List of available permissions:", description = "`%s`" % ('\n'.join(self.permissions.keys())),color = discord.Colour.from_rgb(254,31,104))
            await ctx.reply(embed = em)
            return
        elif role_name == "all":
            roles = ""
            rows = await self.datasystem.get_guild_permissions(ctx.guild.id)
            if not rows:
                await ctx.reply(f"Permissions for `{ctx.guild.name}` not found!")
            for row in rows:
                role = self.get_role_by_id(ctx.guild, row[0])
                if role is None:
                    continue
                if not role.name in roles:
                    roles = roles + "\n`" + role.name + "`:\n"
                roles = roles + "\t`" + self.hashes[row[1]] + "`\n"
            em = discord.Embed(title = "Permissions for `%s`:" % ctx.guild.name, description = roles,color = discord.Colour.from_rgb(254,31,104))
            await ctx.reply(embed = em)
            return

        role = self.get_role_by_name(ctx.guild, role_name)
        if role is None:
            await ctx.reply(f"Role {role_name} not found!")
            return

        permissions = await self.datasystem.get_role_permissions(role.id)

        if permissions is None:
            await ctx.reply(f"Role `{role.name}` doesn't have any permissions!")
            return
        
        perms = []
        for perm in permissions:
            perms.append(self.hashes[perm[2]])

        em = discord.Embed(title = "Permissions of a role `%s`:" % role.name, description = "`%s`" % '\n'.join(perms),color = discord.Colour.from_rgb(254,31,104))
        await ctx.reply(embed = em)

    @perms.command(help = "List of guild roles. \n\nPermission name can be specified to list all roles that have this permission.")
    async def roles(self, ctx: commands.Context, permission: str = None):
        if permission is None:
            em = discord.Embed(title = "List of available roles:", description = "`%s`" % ('\n'.join(r.name for r in ctx.guild.roles)),color = discord.Colour.from_rgb(254,31,104))
            await ctx.reply(embed = em)
            return
        
        if permission not in self.permissions:
            await ctx.reply("No such permission!")
            return 

        roles = await self.datasystem.get_permission_roles(ctx.guild.id, self.permissions[permission])
        if not roles:
            await ctx.reply(f"Roles with permission to `{permission}` not found!")
            return
        out = ""
        for role in roles:
            r = self.get_role_by_id(ctx.guild, role[0])
            if r is None:
                continue
            out = out + r.name + "\n"

        em = discord.Embed(title = "Roles with permission to `%s`:" % permission, description = "`%s`" % out,color = discord.Colour.from_rgb(254,31,104))
        await ctx.reply(embed = em)

async def setup(client):
    await client.add_cog(PermissionSystem(client))