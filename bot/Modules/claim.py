import discord
from discord.ext import commands
from Helpers import constants,data,functions

class ClaimCog(commands.Cog):
    def __init__(self):
        self.bot = constants.bot
    
    

async def setup(bot:commands.Bot):
    await bot.add_cog(ClaimCog())