import discord
from discord.ext import commands
from databases import Database

class DataSystem(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.db = Database('sqlite+aiosqlite:///data.db')
        self.ownerid = 338460114560483329

    async def cog_load(self):
        await self.db.connect()

    async def cog_unload(self):
        await self.db.disconnect()

    async def query(self, query):
        await self.db.execute(query=query)
    
    async def save_permission(self, guild_id: int, role_id: int, permission_hash: int):
        await self.db.execute('''CREATE TABLE IF NOT EXISTS permissions
                                (guild_id BIGINT, role_id BIGINT, permission_hash INT)''')
        query = "INSERT INTO permissions(guild_id, role_id, permission_hash) VALUES (:guild_id, :role_id, :permission_hash)"
        values = {
            "guild_id": guild_id, 
            "role_id": role_id, 
            "permission_hash": permission_hash
        }
        await self.db.execute(query=query, values=values)

    async def remove_permission(self, role_id: int, permission_hash: int):
        query = "DELETE FROM permissions WHERE role_id = :role_id AND permission_hash = :permission_hash"
        values = {
            "role_id": role_id,
            "permission_hash": permission_hash
        }
        await self.db.execute(query=query, values=values)

    async def remove_all_role_permissions(self, role_id: int):
        query = "DELETE FROM permissions WHERE role_id = :role_id"
        values = {
            "role_id": role_id
        }
        await self.db.execute(query=query, values=values)

    async def remove_all_guild_permissions(self, guild_id: int):
        query = "DELETE FROM permissions WHERE guild_id = :guild_id"
        values = {
            "guild_id": guild_id
        }
        await self.db.execute(query=query, values=values)

    async def get_role_permissions(self, role_id: int):
        if id == 0:
            return

        query = "SELECT * FROM permissions WHERE role_id = :role_id"
        values = {
            "role_id": role_id
        }
        rows = await self.db.fetch_all(query=query, values=values)
        if not rows:
            return None
        return rows

    async def get_guild_permissions(self, guild_id: int):
        if id == 0:
            return

        query = "SELECT * FROM permissions WHERE guild_id = :guild_id"
        values = {
            "guild_id": guild_id
        }
        rows = await self.db.fetch_all(query=query, values=values)
        if not rows:
            return None
        return rows

    async def get_permission_roles(self, guild_id: int, permission_hash: int):
        query = "SELECT role_id FROM permissions WHERE guild_id = :guild_id AND permission_hash = :permission_hash"
        values = {
            "guild_id": guild_id,
            "permission_hash": permission_hash,
        }
        rows = await self.db.fetch_all(query=query, values=values)
        if not rows:
            return False
        return rows

    async def has_permission(self, role_id: int, permission_hash: int):
        query = "SELECT 1 FROM permissions WHERE role_id = :role_id AND permission_hash = :permission_hash LIMIT 1"
        values = {
            "role_id": role_id,
            "permission_hash": permission_hash,
        }
        rows = await self.db.fetch_all(query=query, values=values)
        if not rows:
            return False
        return True

    async def save_vk(self, guild_id: int, channel_id: int, peer_id: int):
        await self.db.execute('''CREATE TABLE IF NOT EXISTS vk_chats
                                (guild_id BIGINT, channel_id BIGINT, peer_id INT)''')
        query = "INSERT INTO vk_chats(guild_id, channel_id, peer_id) VALUES (:guild_id, :channel_id, :peer_id)"
        values = {
            "guild_id": guild_id, 
            "channel_id": channel_id, 
            "peer_id": peer_id
        }
        await self.db.execute(query=query, values=values)

    async def remove_vk(self, id: int = 0):
        if id == 0:
            return

        query = "DELETE FROM vk_chats WHERE guild_id = :id OR channel_id = :id OR peer_id = :id"
        values = {
            "id": id
        }
        await self.db.execute(query=query, values=values)

    async def get_vk(self, id: int = 0):
        if id == 0:
            return

        query = "SELECT * FROM vk_chats WHERE guild_id = :id OR channel_id = :id OR peer_id = :id LIMIT 1"
        values = {
            "id": id
        }
        rows = await self.db.fetch_all(query=query, values=values)
        if not rows:
            return None
        return rows[0]

async def setup(client):
    await client.add_cog(DataSystem(client))