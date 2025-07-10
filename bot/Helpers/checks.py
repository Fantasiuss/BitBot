import discord
from discord.ext import commands

from Helpers import constants, data

def is_verified():
    """Check if the user is verified."""
    async def predicate(ctx) -> bool:
        user_id = ctx.author.id
    
        user_profile = data.GetOne("users", {"user_id": user_id})
        
        if not user_profile:
            raise commands.CheckFailure("You need to register first using the `/register` command.")
        
        return True
    return commands.check(predicate)
    

def is_owner() -> bool:
    """Check if the user is the owner of the bot."""
    async def predicate(ctx) -> bool:
        return ctx.author.id == constants.owner_id
    return commands.check(predicate)
    

def is_admin() -> bool:
    """Check if the user has admin permissions in the guild."""
    async def predicate(ctx) -> bool:
        if ctx.guild is None:
            return False  # Not in a guild context
        
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)