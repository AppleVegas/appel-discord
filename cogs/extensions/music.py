from calendar import c
import queue
import discord
from discord.ext import commands, tasks
import yt_dlp as youtube_dl
import asyncio 
import re
from functools import partial

class MusicPlayer(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.description = "Manage music in voice chat."
        self.client = client
        self.permission = self.client.get_cog("PermissionSystem").register_perm("manage_music")
        self.playing = {}
        self.queued = {}
        self.queuemax = 16
        self.timepattern = re.compile("^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$")
        self.youtubepattern = re.compile("^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$")

    async def play_youtube(self, ctx: commands.Context, url: str, seek: str = "0", output: bool = True):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            if not ctx.author.voice is None:
                channel = ctx.author.voice.channel
            else:
                channel = discord.utils.get(ctx.guild.voice_channels)
            await channel.connect(self_deaf=True)
                    
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if output:
            em6 = discord.Embed(title = "Fetching YouTube Video Info", description = f'Please wait while video info is being fetched.',color = discord.Colour.from_rgb(254,31,104))
            downmsg = await ctx.send(embed = em6)

        ffmpeg_opts = {'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {seek}', 'options': '-vn'}
        ydl_opts = {
            'format': 'bestaudio/best',
            'source_address': '0.0.0.0',
            'cachedir': False
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(None, partial(ydl.extract_info, url=url, download=False))
        except Exception as e:
            em1 = discord.Embed(title = "Player Error", description = "%s\n%s" % (url,e),color = discord.Colour.from_rgb(254,31,104))
            self.client.loop.create_task(ctx.send(embed = em1))
            await downmsg.delete()
            await self.queue_next(ctx.guild)
            return

        if output:
            await downmsg.delete()

        if voice.is_playing():
            voice.source = await discord.FFmpegOpusAudio.from_probe(info["url"], **ffmpeg_opts)
        else:
            voice.play(await discord.FFmpegOpusAudio.from_probe(info["url"], **ffmpeg_opts), after=lambda e: self.after(e, ctx))

        self.playing[ctx.guild.id] = {
            "info": info,
            "ctx": ctx
        }

        if output: 
            em1 = discord.Embed(title = "Now Listening", description = f'**{info["title"]}**\n{url}\n\nPlease use `stop` command to stop.\nUse `play` command again to change audio.\n\n*Audio provided by {ctx.author.mention}*',color = discord.Colour.from_rgb(254,31,104))
            em1.set_thumbnail(url = f'https://img.youtube.com/vi/{info["id"]}/default.jpg')
            await ctx.send(embed = em1)
    
    def after(self, e, ctx: commands.Context):
        if e:
            em1 = discord.Embed(title = "Player Error", description = e,color = discord.Colour.from_rgb(254,31,104))
            self.client.loop.create_task(ctx.send(embed = em1))
        self.client.loop.create_task(self.queue_next(ctx.guild))
    
    async def queue_next(self, guild: discord.Guild):
        if guild.id not in self.queued:
            return False

        if not self.queued[guild.id]:
            return False
        
        queued = self.queued[guild.id].pop(0)

        await self.play_youtube(queued[1], queued[0])

        if not self.queued[guild.id]:
            del self.queued[guild.id]

        return True


    @commands.command(help="Plays music in voice channel.")
    async def play(self, ctx: commands.Context, url: str):
        if self.youtubepattern.match(url) is None:
            await ctx.reply("Invalid YouTube URL!")
            return

        await ctx.message.delete()
        await self.play_youtube(ctx, url)

    @commands.command(help="Play next music in queue.")
    async def next(self, ctx: commands.Context):
        if not await self.queue_next(ctx.guild):
            await ctx.reply("Queue is empty!")
            return

        await ctx.message.delete()

    @commands.command(help="Seeks currently playing song to a timestamp.\n\nExamples of timestamp:\n37 = 37 seconds\n13:37 = 13 minutes and 37 seconds\n13:37:51 = 13 hours, 37 minutes and 51 seconds")
    async def seek(self, ctx: commands.Context, timestamp: str):
        if ctx.guild.id not in self.playing:
            await ctx.send("Not playing anything!")
            return

        if self.timepattern.match(timestamp).group() is None:
            await ctx.send("Invalid timestamp! Correct format: HH:MM:SS")
            return

        info = self.playing[ctx.guild.id]["info"]

        await self.play_youtube(ctx, "https://youtube.com/watch?v=%s" % (info["id"]), timestamp, False)

        em1 = discord.Embed(title = f"Seeking Music", description = f'**{info["title"]}**\nSeeking to `{timestamp}`',color = discord.Colour.from_rgb(254,31,104))
        em1.set_thumbnail(url = f'https://img.youtube.com/vi/{info["id"]}/default.jpg')
        await ctx.send(embed = em1)

    @commands.group(invoke_without_command=True, help = "List and manage queue.")
    async def queue(self, ctx: commands.Context):
        if ctx.guild.id not in self.queued:
            await ctx.reply("Queue is empty.")
            return

        links = '\n'.join(((str(i + 1) + ": " + self.queued[ctx.guild.id][i][0] + " by " + self.queued[ctx.guild.id][i][1].author.name) for i in range(0, len(self.queued[ctx.guild.id]))))

        em1 = discord.Embed(title = f"Queue list:", description = links,color = discord.Colour.from_rgb(254,31,104))

        await ctx.send(embed = em1)

    @queue.command(help = "Add music to queue.")
    async def add(self, ctx: commands.Context, url: str):
        if self.youtubepattern.match(url) is None:
            await ctx.reply("Invalid YouTube URL!")
            return
        if ctx.guild.id not in self.queued:
            self.queued[ctx.guild.id] = []

        if len(self.queued[ctx.guild.id]) >= self.queuemax:
            await ctx.reply(f"Queue limit reached!")
            return

        self.queued[ctx.guild.id].append([url, ctx])

        await ctx.reply(f"Added `{url}` to queue!")

        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice is None or not voice.is_playing():
            await self.queue_next(ctx.guild)

    @queue.command(help ="Clear queue.")
    async def clear(self, ctx: commands.Context):
        del self.queued[ctx.guild.id]
        await ctx.reply(f"Cleared queue!")

    @commands.command(help="Stops playing music in voice channel and disconnects.")
    async def stop(self, ctx: commands.Context):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            await ctx.reply("Not playing anything!")
            return

        if ctx.guild.id in self.queued:
            del self.queued[ctx.guild.id]

        voice.stop()
        await voice.disconnect()
        await ctx.reply("Stopped.")

    @commands.command(help="Resumes playing music in voice channel if paused.")
    async def resume(self, ctx: commands.Context):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None or not voice.is_paused():
            await ctx.reply("Not paused!")
            return

        voice.resume()
        await ctx.reply("Resumed.")

    @commands.command(help="Pauses playing music in voice channel.")
    async def pause(self, ctx: commands.Context):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            await ctx.reply("Not playing anything!")
            return

        voice.pause()
        await ctx.reply("Paused.")

async def setup(client):
    await client.add_cog(MusicPlayer(client))