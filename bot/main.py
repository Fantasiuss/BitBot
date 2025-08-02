import discord, discord.ext, os, json, datetime
from discord.ext import commands
from dotenv import load_dotenv
from loguru import logger

from Helpers import constants,data,functions,server

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
        logger.debug(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.debug('------')
        for guild in self.guilds:
            logger.debug(f'Connected to guild: {guild.name} (ID: {guild.id})')
            data.command_line(f"INSERT OR IGNORE INTO guilds (guild_id) VALUES ({guild.id})")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the necessary permissions to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Please provide all required arguments. Usage: {ctx.command.usage}")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("This command does not exist. Please check the command name and try again.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have the necessary permissions to execute this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.UserInputError):
            await ctx.send("There was an error with your input. Please check and try again.")
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I do not have permission to perform this action.")
        elif isinstance(error, ValueError):
            await ctx.send(f"Value error: {str(error)}")
            
        else:
            # For unhandled errors, log them or send a generic message
            logger.error(f"Unhandled error in command {ctx.command}: {error}, {error.__traceback__}")
            await ctx.send("An unexpected error occurred. Please DM the bot owner (Fantasiuss) if this issue persists.")

bot = BitBot()

@discord.app_commands.context_menu(name="View Profile")
async def profile_context_menu(interaction:discord.Interaction, user:discord.User):
    """View your profile or another user's profile."""
    
    # Fetch user data from the database
    user_data = data.GetOne("users", {"user_id": user.id})
    
    if user_data is None:
        await interaction.response.send_message(f"No profile found for {user.name}.",ephemeral=True)
        return
    
    data.update_database(user_data['username'])
    user_data = data.GetOne("users", {"user_id": user.id})
    
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
    
@bot.command(name='checkempires')
@commands.is_owner()
async def check_empires(ctx):
    empires = []
    for empire in constants.r6_empires:
        empire_data = server.get_empire_data(empire)
        if empire_data:
            user = data.GetOne("users", {"username": empire_data["owner"]})
            if user:
                empire_data["owner_mention"] = f' (<@{user["user_id"]}>)'
            else:
                empire_data["owner_mention"] = ""
            
            empires.append(empire_data)
        else:
            logger.debug(f"Empire {empire} not found or has no data.")
            empires.append({"name":empire,"members":0,"owner":"NOBODY","owner_mention":""})
    
    empires.sort(key=lambda x: x["members"], reverse=True)
    string = ""
    for empire in empires:
        string += f"{empire['name']} - {empire['members']} members, owned by {empire["owner"]}{empire['owner_mention']}\n"
    
    if len(string) > 2000:
        # If the string is too long, split it into multiple messages
        for i in range(0, len(string), 2000):
            await ctx.send(embed=discord.Embed(description=string[i:i+2000], color=discord.Color.blue()))
    else:
        await ctx.send(embed=discord.Embed(description=string, color=discord.Color.blue()))

@bot.check
async def check_blacklist(ctx:commands.Context):
    return not ctx.author.id in constants.blacklist

@bot.event
async def on_guild_join(guild:discord.Guild):
    """Event triggered when the bot joins a new guild."""
    data.Update("guilds",{"guild_id": guild.id})
    logger.debug(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
@bot.event
async def on_guild_remove(guild:discord.Guild):
    """Event triggered when the bot is removed from a guild."""
    data.Remove("guilds", {"guild_id": guild.id})
    logger.debug(f"Removed from guild: {guild.name} (ID: {guild.id})")

if __name__ == "__main__":
    bot.run(TOKEN)