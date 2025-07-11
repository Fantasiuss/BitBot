import discord
from discord.ext import commands
from Helpers import constants,data

async def group_autocomplete(interaction,current)-> list[discord.app_commands.Choice[str]]:
    async def function(interaction, current)-> list[discord.app_commands.Choice[str]]:
        options = data.Get("groups")
        return list({
            discord.app_commands.Choice(name=f'{group["name"]} ({group["grouptype"]})', value=group["name"])
            for group in options if current.lower() in group["name"].lower()
        })[0:25]

class GroupsCog(commands.Cog):
    def __init__(self):
        self.bot = constants.bot
    
    @commands.hybrid_group(name="group")
    async def group(self,ctx):
        pass
    
    @group.command()
    async def create(self,ctx):
        """Register a created nation or claim."""
        user_data = data.GetOne("users", {"user_id": ctx.author.id})
        if not user_data: return await ctx.reply("You have not created a profile yet. Use /register to create a profile.",ephemeral=True)
        embed = discord.Embed(title="Group Creation",description="What type of group are you creating?")
        embed.set_footer("You should be the owner of this claim/empire in-game.")
        
        class GroupCreationModal(discord.ui.Modal):
            def __init__(self, grouptype:str):
                self.grouptype = grouptype
                super().__init__(title=grouptype.capitalize()+" Creation", timeout=360)
                self.add_item(discord.ui.TextInput(label=grouptype.capitalize()+" Name"))
                self.add_item(discord.ui.TextInput(label="Region",placeholder="Use F4 to find, please use the number."))
        
            def on_submit(self, interaction:discord.Interaction):
                data.Update("groups",{"name":self.children[0].value},{"owner_id":interaction.user.id,"group_type":self.grouptype})

        class GroupCreationView(discord.ui.View):
            def __init__(self, *, timeout = 180):
                super().__init__(timeout=timeout)
            
            @discord.ui.button(label="Empire")
            async def empire(self,interaction:discord.Interaction,btn):
                await interaction.response.send_modal(GroupCreationModal("empire"))
            
            @discord.ui.button(label="Claim")
            async def claim(self,interaction,btn):
                await interaction.response.send_modal(GroupCreationModal("claim"))
                
        await ctx.reply(embed=embed,view=GroupCreationView(),ephemeral=True)
    
    @group.command()
    @discord.app_commands.autocomplete(groupname=group_autocomplete)
    async def view(self,ctx,groupname:str):
        group = data.GetOne("groups",{"name":groupname})
        if not group: return await ctx.reply("Group not found.",ephemeral=True)
        embed = discord.Embed(title=group["name"],description=group["description"])
        members = []
        if(group["group_type"] == "Claim"):
            members = data.Get("users",{"claim":group["name"]})
        elif(group["group_type"] == "Empire"):
            members = data.Get("users",{"empire":group["name"]})
            
        leader = data.GetOne("users",{"user_id":group["owner_id"]})
        
        embed.add_field(name="Leader",value=leader["name"])
        embed.add_field(name="Members",value=len(members))
        
        total_levels = 0
        for user in members:
            for v in members.values(): 
                if type(v) == int and v != user["user_id"]: total_levels += v
        
        embed.add_field(name="Total Levels",value=total_levels)
        
        await ctx.reply(embed=embed)
    
    @group.command()
    @discord.app_commands.autocomplete(groupname=group_autocomplete)
    async def join(self,ctx,groupname:str):
        user = data.GetOne("users",{"user_id":ctx.author.id})
        if not user: return await ctx.reply("You aren't registered. Use /register to register your account.",ephemeral=True)
        group = data.GetOne("groups",{"name":groupname})
        if not group: return await ctx.reply("Group not found.",ephemeral=True)
        if (group["group_type"] == "Claim" and user["claim"] != group["name"]) or (group["group_type"] == "Empire" and user["empire"] != group["name"]):
            return await ctx.reply("You are already in a group. Use /group leave to leave your current group.",ephemeral=True)
        
        data.Update("users",{"user_id":ctx.author.id},{group["group_type"].lower():group["name"]})
        
        await ctx.reply(f"You have successfully joined {group['name']}.",ephemeral=True)
        
    @group.command()
    @discord.app_commands.choices(type=[discord.app_commands.Choice(name="Empire",value="empire"),discord.app_commands.Choice(name="Claim",value="claim")])
    async def leave(self,ctx,type:discord.app_commands.Choice[str]):
        user = data.GetOne("users",{"user_id":ctx.author.id})
        if not user: return await ctx.reply("You aren't registered. Use /register to register your account.",ephemeral=True)
        if user[type.value] == 'None': return await ctx.reply("You aren't currently in a group.",ephemeral=True)
        
        group = data.GetOne("groups",{"name":user[type.value]})
        
        data.Update("users",{"user_id":ctx.author.id},{type.value:'None'})
        
        await ctx.reply(f"You have successfully left {group['name']}.",ephemeral=True)
    
async def setup(bot:commands.Bot):
    """await bot.add_cog(GroupsCog())"""