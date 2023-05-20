import discord
from discord.ext import commands
import asyncio
from io import BytesIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
#from rembg import remove

class ImageSettings(commands.FlagConverter):
    up: str = ""
    down: str = ""
    size: float = 1
    #bg: bool = True

class Images(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.description = "Image manipulation."
        self.client = client
        self.permission = self.client.get_cog("PermissionSystem").register_perm("images")

    @commands.command(help="Generate impact meme from image. Image must me attached.\n\nFlags:\nup: <upper text>\ndown: <lower text>\nsize: <text size = 1.0>")
    async def meme(self, ctx: commands.Context, *, flags: ImageSettings):
        if len(ctx.message.attachments) == 0 or ctx.message.attachments[0].content_type[:5] != "image":
            await ctx.send("No image attached.", delete_after=2)
            return
        image = Image.open(BytesIO(await ctx.message.attachments[0].read()))
        #if not flags.bg:
        #    loop = asyncio.get_event_loop()
        #    image = await loop.run_in_executor(None, remove, image)
        draw = ImageDraw.Draw(image)
        fontsize = int(image.height*0.1*flags.size)
        outlinesize = (fontsize*0.05)
        font = ImageFont.truetype("fonts/impact.ttf", fontsize)
        uppertext = flags.up
        lowertext = flags.down

        if uppertext != "":
            w, h = draw.textsize(uppertext, font)
            x, y = image.width/2, 10 + h/2
            draw.text((x-outlinesize, y), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x+outlinesize, y), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x, y-outlinesize), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x, y+outlinesize), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x-outlinesize, y-outlinesize), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x+outlinesize, y+outlinesize), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x+outlinesize, y-outlinesize), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x-outlinesize, y+outlinesize), uppertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x, y), uppertext,(255,255,255),font=font, anchor='mm')

        if lowertext != "":
            w, h = draw.textsize(lowertext, font)
            x, y = image.width/2, image.height - 10 - h/2
            draw.text((x-outlinesize, y), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x+outlinesize, y), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x, y-outlinesize), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x, y+outlinesize), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x-outlinesize, y-outlinesize), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x+outlinesize, y+outlinesize), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x+outlinesize, y-outlinesize), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x-outlinesize, y+outlinesize), lowertext, font=font, fill=(0,0,0), anchor='mm')
            draw.text((x, y), lowertext,(255,255,255),font=font, anchor='mm')

        filename = "temp/impactimage.%s.png" % ctx.guild.id
        image.save(filename)
        await ctx.reply(file=discord.File(filename))

async def setup(client):
    await client.add_cog(Images(client))