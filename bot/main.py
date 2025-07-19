import discord, discord.ext, os, json, datetime
from discord.ext import commands
from dotenv import load_dotenv

from Helpers import constants,data,functions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class BitBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("$"), intents=intents)
        
    async def setup_hook(self):
        data.initialize_data()
        await functions.refresh_verification_messages(self)
        
        for filename in constants.cogs:
            await self.load_extension(filename)
                    
    async def on_ready(self):
        constants.bot = self
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        for guild in self.guilds:
            
            print(f'Connected to guild: {guild.name} (ID: {guild.id})')
            data.command_line(f"INSERT OR IGNORE INTO guilds (guild_id) VALUES ({guild.id})")

bot = BitBot()

@discord.app_commands.context_menu(name="View Profile")
async def profile_context_menu(interaction:discord.Interaction, user:discord.User):
    """View your profile or another user's profile."""
    
    # Fetch user data from the database
    user_data = data.GetOne("users", {"user_id": user.id})
    
    if user_data is None:
        await interaction.response.send_message(f"No profile found for {user.name}.",ephemeral=True)
        return
    
    embed = discord.Embed(title=f"{user_data['username']}'s Profile", color=discord.Color.blue())
    embed.add_field(name="Empire", value=user_data["empire"], inline=True)
    embed.add_field(name="Claim", value=user_data["claim"], inline=True)
    
    embed.add_field(name="", value="", inline=False)
    
    for profession in constants.professions._list:
        embed.add_field(name=profession,value=user_data[profession.lower()],inline=True)
    
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    
    embed.set_footer(text="Use /register to create a profile.")
    
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.command(name='synctree')
@commands.is_owner()
async def synctree(ctx,glob:bool=False):
    """Sync the command tree with Discord."""
    guild = None if glob else ctx.guild
    await bot.tree.sync(guild=guild)
    await ctx.reply("Command tree synced successfully!", ephemeral=True)

@bot.command(name='cmdline')
@commands.is_owner()
async def cmdline(ctx,query):
    data.command_line(query)
    await ctx.reply("Query processed.",ephemeral=True)

@bot.check
async def check_blacklist(ctx:commands.Context):
    return not ctx.author.id in constants.blacklist

@bot.event
async def on_guild_join(guild:discord.Guild):
    """Event triggered when the bot joins a new guild."""
    data.Update("guilds",{"guild_id": guild.id})
    print(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
@bot.event
async def on_guild_remove(guild:discord.Guild):
    """Event triggered when the bot is removed from a guild."""
    data.Remove("guilds", {"guild_id": guild.id})
    print(f"Removed from guild: {guild.name} (ID: {guild.id})")

if __name__ == "__main__":
    bot.run(TOKEN)