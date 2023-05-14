import discord
from discord.ext import commands, tasks
from vkbottle.bot import Bot, Message
from vkbottle import GroupEventType
from vk_api.utils import get_random_id
import asyncio
import random

class VK(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.permission = self.client.get_cog("PermissionSystem").register_perm("vk")
        self.datasystem = self.client.get_cog("DataSystem")
        self.latestmsg = None
        self.bot = Bot(client.get_cog("AppelConfig").cfg["vk_token"])
        self.bot.on.chat_message()(self.vk_on_chat_message)
        self.pending = {}
    
    async def add_pending(self, peer_id):
        code = random.randint(1000,9999)
        message = f'''Чтобы использовать бота для пересылки медиаконтента в Discord сервер:

        1) Разрешите боту доступ ко всей переписке.
        2) Введите на сервере следующую команду:
        
        !vk add {str(code)}

        Писать команду надо в канале, в который вы хотите получать пересланные сообщения.
        Чтобы прекратить использовать бота для пересылки медиаконтента, введите следующую команду на своём Discord сервере:

        !vk remove
        '''
        self.pending[peer_id] = code
        await self.bot.api.messages.send(chat_id=peer_id - 2000000000,message=message, random_id=get_random_id())

    async def vk_on_chat_message(self, message: Message):
        if message.peer_id in self.pending:
            return

        reciever = await self.datasystem.get_vk(message.peer_id)
        if reciever is None:
            await self.add_pending(message.peer_id)
            #id = (await self.bot.api.groups.get_by_id())[0].id
            #await self.bot.api.messages.remove_chat_user(chat_id=(message.peer_id - 2000000000), member_id=(id*-1))
            return

        if len(message.attachments) == 0:
            return

        channel = self.client.get_channel(reciever[1])
        if channel is None:
            return

        urls = []
        user = (await self.bot.api.users.get(user_ids=[message.from_id], name_case="gen"))[0]
        urls.append(f"**От {user.first_name} {user.last_name}:**\n{message.text}")

        for attachment in message.attachments:
            if attachment.photo is not None:
                photo = attachment.photo.sizes[0]
                for p in attachment.photo.sizes:
                    if p.height > photo.height:
                        photo = p
                urls.append(photo.url)
            #elif attachment.video is not None:
            #    if attachment.video.player is not None:
            #        urls.append(attachment.video.player)
            elif attachment.doc is not None:
                if attachment.doc.url is not None:
                    urls.append(attachment.doc.url)
        
        for url in urls:
            try:
                await channel.send(url)
            except:
                pass

    @commands.Cog.listener()
    async def on_ready(self):
        self.vk_task.start()

    async def cog_load(self):
        self.vk_task.start()

    async def cog_unload(self):
        self.vk_task.cancel()

    @tasks.loop(seconds=5.0)
    async def vk_task(self):
        await self.bot.run_polling()

    async def add_vk(self, ctx: commands.Context, auth_code: int = 0):
        reciever = await self.datasystem.get_vk(ctx.guild.id)
        if reciever is not None:
            await ctx.reply("VK is already connected.")
            return

        if auth_code == 0:
            await ctx.reply("Auth code must be specified.")
            return

        if auth_code not in self.pending.values():
            await ctx.reply("Invalid auth code.")
            return
         
        for id in self.pending:
            if self.pending[id] == auth_code:
                peer_id = id

        await self.datasystem.save_vk(ctx.guild.id, ctx.channel.id, peer_id)
        del self.pending[id]
        await self.bot.api.messages.send(chat_id=peer_id - 2000000000,message=f"Сервер {ctx.guild.name} подключен!", random_id=get_random_id())
        await ctx.reply("VK has been connected successfully.")


    async def remove_vk(self, ctx: commands.Context):
        reciever = await self.client.get_cog("DataSystem").get_vk(ctx.guild.id)
        if reciever is None:
            await ctx.reply("VK chat isn't connected.")
            return
       
        await self.client.get_cog("DataSystem").remove_vk(ctx.guild.id)
        await self.bot.api.messages.send(chat_id=reciever[2] - 2000000000,message=f"Сервер {ctx.guild.name} отключен.", random_id=get_random_id())
        await ctx.reply("VK chat connection removed.")

    @commands.command(description="")
    async def vk(self, ctx: commands.Context, mode: str = "", auth_code: int = 0):
        #modes = {
        #    "add": lambda: (await self.add_vk(ctx, auth_code) for _ in '_').__anext__(),
        #    "remove": lambda: (await self.remove_vk(ctx) for _ in '_').__anext__()
        #}
        if mode == "add":
            await self.add_vk(ctx, auth_code)
        elif mode == "remove":
            await self.remove_vk(ctx)
        else:
            await ctx.reply("Invalid mode!")
            return 

        #modes[mode]()

        #await self.client.get_cog("DataSystem").save_vk(ctx.guild.id, ctx.channel.id, 2000000001)
        #await self.bot.api.messages.send(user_id=161488276, message="FUCKYOU", random_id=get_random_id())

async def setup(client):
    await client.add_cog(VK(client))