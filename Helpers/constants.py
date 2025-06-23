import discord
from discord.ext import commands

bot: commands.Bot = None
guild: discord.Guild = None
debug: bool = False
client = None

class ListStorage():
    def __init__(self,args:list[str] = []):
        self._list:list[str] = args
    
    _list:list[str] = []
    
    @property
    def choices(self):
        return [discord.app_commands.Choice(label=str(i), value=str(i)) for i in self._list]
    
    async def autocomplete(self,interaction,current)-> list[discord.app_commands.Choice[str]]:
        async def function(interaction, current)-> list[discord.app_commands.Choice[str]]:
            return list({
                discord.app_commands.Choice(name=object, value=object)
                for object in self._list if current.lower() in object.lower()
            })[0:25]
    
professions = ListStorage(["Carpentry","Farming","Fishing","Foraging","Forestry","Hunting","Leatherworking","Masonry","Mining","Scholar","Smithing","Tailoring"])