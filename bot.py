import discord
import asyncio
import json
from discord.ext import commands
import os

class AppelConfig(commands.Cog):
    def __init__(self, client: commands.Bot, cfg):
        self.client = client
        self.cfg = cfg

class CogSystem(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    async def load_cogs(self, reload: bool = False):
        for file in os.listdir("./cogs/extensions"):
            if file.endswith(".py"):
                name = f"cogs.extensions.%s" % file[:-3]
                if reload:
                    try:
                        await client.reload_extension(name)
                    except commands.ExtensionNotLoaded:
                        await client.load_extension(name)
                else:
                    await client.load_extension(name)
                print("Loaded %s extension." % name)
        print("Extensions (re)loaded!")

    async def check_permission(ctx: commands.Context):
        if ctx.author.id == 338460114560483329:
            return True
        return False
    
    @commands.command()
    @commands.check(check_permission)
    async def creload(self, ctx: commands.Context):
        await self.load_cogs(True)
        await ctx.message.delete()
        await ctx.send("Reloaded cogs.", delete_after=2)

with open("appel_cfg.json", "r") as cfg_file:
    cfg = json.loads(cfg_file.read())

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=cfg["prefix"], intents=intents)

async def load_cogs():
    cfg_cog = AppelConfig(client, cfg)
    await client.add_cog(cfg_cog)

    await client.load_extension("cogs.datasystem")
    await client.load_extension("cogs.permissions")

    cog_sys = CogSystem(client)
    await cog_sys.load_cogs()
    await client.add_cog(cog_sys)

asyncio.run(load_cogs())

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="In Alpha!"))

if __name__ == "__main__":
    client.run(cfg["token"])