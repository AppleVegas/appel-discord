import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio 

class MusicPlayer(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.permission = self.client.get_cog("PermissionSystem").register_perm("manage_music")
        self.playing = {}

    async def play_music(self, guild: discord.Guild, member: discord.Member, url: str):
        pass
    
    @commands.command(description="Plays music in voice channel. Usage: `play *url*`")
    async def play(self, ctx: commands.Context, url: str):
        videoID = "dQw4w9WgXcQ"
        regurl = url.find("watch?v=")
        smolurl = url.find("youtu.be/")
        shorturl = url.find("shorts/")
        if regurl != -1:
            videoID = url[regurl + 8:].split("&")[0]
        elif smolurl != -1:
            videoID = url[smolurl + 9:].split("&")[0]
        elif shorturl != -1:
            videoID = url[shorturl + 7:].split("&")[0]
        else:
            await ctx.reply("Not a YouTube URL bruv.")
            return

        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            if not ctx.author.voice is None:
                channel = ctx.author.voice.channel
            else:
                channel = discord.utils.get(ctx.guild.voice_channels)
            await channel.connect(self_deaf=True)
        else:
            if voice.is_playing():
                voice.stop()
                await asyncio.sleep(0.05)
        #file_name = "music/youtube.%s.mp3" % str(ctx.guild.id)
        #try:
        #    if os.path.isfile(file_name):
        #        os.remove(file_name)
        #except Exception as e:
        #    raise commands.CommandInvokeError(e)
                    
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        em6 = discord.Embed(title = "Fetching YouTube Video Info", description = f'Please wait while video info is being fetched.',color = discord.Colour.from_rgb(254,31,104))
        downmsg = await ctx.send(embed = em6)

        ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        ydl_opts = {
            'format': 'bestaudio/best',
          #  'outtmpl': file_name[:-4],
          #  'postprocessors': [{
          #      'key': 'FFmpegExtractAudio',
          #      'preferredcodec': 'mp3',
          #      'preferredquality': '196',
          #  }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            #ydl.download([url])

        await ctx.message.delete()
        await downmsg.delete()
        voice.play(discord.FFmpegPCMAudio(info["url"], **ffmpeg_opts))
        em1 = discord.Embed(title = "Now Listening", description = f'**{info["title"]}**\n{url}\n\nPlease use `stop` command to stop.\nUse `play` command again to change video.\n\n*Video provided by {ctx.author.mention}*',color = discord.Colour.from_rgb(254,31,104))
        em1.set_thumbnail(url = f'https://img.youtube.com/vi/{videoID}/default.jpg'.format(videoID = videoID))
        await ctx.send(embed = em1)

    @commands.command(description="Stops playing music in voice channel and disconnects.")
    async def stop(self, ctx: commands.Context):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            await ctx.reply("Not playing anything!")
            return
        voice.stop()
        await voice.disconnect()
        await ctx.reply("Stopped.")

    @commands.command(description="Resumes playing music in voice channel if paused.")
    async def resume(self, ctx: commands.Context):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None or not voice.is_paused():
            await ctx.reply("Not paused!")
            return
        voice.resume()
        await ctx.reply("Resumed.")

    @commands.command(description="Pauses playing music in voice channel.")
    async def pause(self, ctx: commands.Context):
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice is None:
            await ctx.reply("Not playing anything!")
            return
        voice.pause()
        await ctx.reply("Paused.")

async def setup(client):
    await client.add_cog(MusicPlayer(client))