import discord, discord.ext, os, json, datetime
from discord.ext import commands
from dotenv import load_dotenv

from Helpers import constants,data

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Botweaver(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("$"), intents=intents)
        
    async def setup_hook(self):
        for filename in os.listdir('./Modules'):
            if filename.endswith('.py'):
                await self.load_extension(f'Modules.{filename[:-3]}')
    
    async def on_ready(self):
        constants.bot = self
        constants.guild = self.get_guild(1118830743427235903)
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        for guild in self.guilds:
            print(f'Connected to guild: {guild.name} (ID: {guild.id})')

bot = Botweaver()

@bot.command(name='synctree')
@commands.is_owner()
async def synctree(ctx):
    """Sync the command tree with Discord."""
    await bot.tree.sync()
    await ctx.send("Command tree synced successfully!", ephemeral=True)
