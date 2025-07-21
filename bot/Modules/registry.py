import discord,re
from discord.ext import commands
from Helpers import constants,data,functions

class RegistryCog(commands.Cog):
    def __init__(self):
        self.bot = constants.bot

    @discord.app_commands.user_install()
    @commands.hybrid_command(description="View your profile or another user's profile.")
    async def profile(self, ctx:commands.Context, user:discord.User=None):
        """View your profile or another user's profile."""
        if user is None:
            user = ctx.author
        
        # Fetch user data from the database
        user_data = data.GetOne("users", {"user_id": user.id})
        
        if user_data is None:
            await ctx.send(f"No profile found for {user.name}.",ephemeral=True)
            return
        
        embed = discord.Embed(title=f"{user_data['username']}'s Profile", color=discord.Color.blue())
        embed.add_field(name="Empire", value=user_data["empire"], inline=True)
        embed.add_field(name="Claim", value=user_data["claim"], inline=True)
        
        embed.add_field(name="", value="", inline=False)
        
        for profession in constants.professions._list:
            embed.add_field(name=profession,value=user_data[profession.lower()],inline=True)
            
        embed.add_field(name="", value="", inline=False)
        
        for skill in constants.skills._list:
            embed.add_field(name=skill,value=user_data[skill.lower()],inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        
        embed.set_footer(text="Use /register to create a profile.")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(description="Register a new user profile.")
    async def register(self, ctx:commands.Context):
        user_data = data.GetOne("users", {"user_id": ctx.author.id})
        
        if not (user_data is None):
            await ctx.send(f"You are already registered as {user_data['username']}.",ephemeral=True)
            return
        
        await functions.send_register_modal(ctx.interaction)
    
    @discord.app_commands.user_install()
    @commands.hybrid_command(description="Update your profile.")
    @discord.app_commands.choices(options=[discord.app_commands.Choice(name="Professions",value="professions"),discord.app_commands.Choice(name="Skills",value="skills"),discord.app_commands.Choice(name="Empire", value="empire"), discord.app_commands.Choice(name="Claim", value="claim")])
    async def update_profile(self, ctx:commands.Context, options:discord.app_commands.Choice[str]):
        """Update your profile with a new empire, claim or profession."""
        user_data = data.GetOne("users", {"user_id": ctx.author.id})
        conn,cursor = data.get_connection()
        
        if user_data is None:
            await ctx.send("You need to register first using the `/register` command.", ephemeral=True)
            return
        
        match options.value:
            case "empire":
                class EmpireModal(discord.ui.Modal):
                    def __init__(self, *, title = "Update Profile Empire", timeout = None):
                        super().__init__(title=title, timeout=timeout)
                        
                    question = discord.ui.TextInput(label="Empire", required=True, placeholder=user_data["empire"])
                    async def on_submit(self, interaction:discord.Interaction):
                        empire = self.question.value
                        user_id = interaction.user.id
                        
                        cursor.execute("UPDATE users SET empire = ? WHERE user_id = ?", (empire, user_id))
                        conn.commit()
                        conn.close()
                        
                        await interaction.response.send_message(f"Empire updated to {empire}!", ephemeral=True)
                modal = EmpireModal()
                ctx.interaction.response.send_modal(modal)
            case "claim":
                class ClaimModal(discord.ui.Modal):
                    def __init__(self, *, title = "Update Profile Claim", timeout = None):
                        super().__init__(title=title, timeout=timeout)
                        
                    question = discord.ui.TextInput(label="Claim", required=True, placeholder=user_data["claim"])
                    async def on_submit(self, interaction:discord.Interaction):
                        claim = self.question.value
                        user_id = interaction.user.id
                        
                        cursor.execute("UPDATE users SET claim = ? WHERE user_id = ?", (claim, user_id))
                        conn.commit()
                        conn.close()
                        
                        await interaction.response.send_message(f"Claim updated to {claim}!", ephemeral=True)
                modal = ClaimModal()
                ctx.interaction.response.send_modal(modal)
            case "professions":
                class ProfessionModal(discord.ui.Modal):
                    def __init__(self, entries, *, title = "Profession Update Form", timeout = 300):
                        super().__init__(title=title, timeout=timeout)
                        user_data = data.GetOne("users", {"user_id": ctx.author.id})
                        for key in entries:
                            self.add_item(discord.ui.TextInput(label=key,style=discord.TextStyle.short,required=False,default=str(user_data[key.lower()])))
                    
                    async def on_submit(self, interaction):
                        try:
                            results = {item.label: int(item.value.replace(" ","")) for item in self.children}
                        except:
                            return await interaction.response.send_message("Provided value was not a number.",ephemeral=True)
                        
                        data.Update("users",{"user_id":interaction.user.id},results)
                        
                        await interaction.response.send_message("Professions updated!",ephemeral=True)
                            
                        return await super().on_submit(interaction)
                
                class SelectProfessions(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=360)
                    
                    @discord.ui.select(options=[discord.SelectOption(label=x,value=x) for x in constants.professions._list],max_values=5,min_values=1)
                    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
                        selected = select.values
                        modal = ProfessionModal(selected)
                        await interaction.response.send_modal(modal)
                
                await ctx.reply("Select up to 5 professions to update:", view=SelectProfessions(),ephemeral=True)
            case "skills":
                class SkillModal(discord.ui.Modal):
                    def __init__(self, entries, *, title = "Skill Update Form", timeout = 300):
                        super().__init__(title=title, timeout=timeout)
                        user_data = data.GetOne("users", {"user_id": ctx.author.id})
                        for key in entries:
                            self.add_item(discord.ui.TextInput(label=key,style=discord.TextStyle.short,required=False,placeholder=str(user_data[key.lower()])))
                    
                    async def on_submit(self, interaction):
                        try:
                            results = {item.label: int(item.value) for item in self.children}
                        except:
                            return await interaction.response.send_message("Provided value was not a number.",ephemeral=True)
                        
                        data.Update("users",{"user_id":interaction.user.id},results)
                        
                        await interaction.response.send_message("Skills updated!",ephemeral=True)
                            
                        return await super().on_submit(interaction)
                
                class SelectSkills(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=360)
                    
                    @discord.ui.select(options=[discord.SelectOption(label=x,value=x) for x in constants.skills._list],max_values=5,min_values=1)
                    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
                        selected = select.values
                        modal = SkillModal(selected)
                        await interaction.response.send_modal(modal)
                await ctx.reply("Select up to 5 skills to update:", view=SelectSkills(),ephemeral=True)
            
    @commands.hybrid_command()
    @discord.app_commands.choices(profession=constants.professions.choices+constants.skills.choices,scope=[discord.app_commands.Choice(name="Global",value="global"),discord.app_commands.Choice(name="Region",value="region"),discord.app_commands.Choice(name="Empire",value="empire"),discord.app_commands.Choice(name="Claim",value="claim")])
    async def leaderboard(self,ctx,profession:discord.app_commands.Choice[str],scope:discord.app_commands.Choice[str]=None,):
        """Shows the profession leaderboard"""
        user_data = data.GetOne("users",{"user_id":ctx.author.id})
        members = []
        scope = scope.value if scope else "global"
        match scope:
            case "global":
                members = data.Get("users")
            case _:
                if not user_data:
                    return await ctx.reply("You need to register first using the `/register` command.", ephemeral=True)
                
                members = data.Get("users",{scope:user_data[scope]})
        members.sort(key=lambda x: x[profession.value.lower()],reverse=True)
        description = ""
        index=1
        for user in members:
            if(index>10): break
            description += f"`[{index}]`{user['username']}: Level {str(user[profession.value.lower()])} {profession.value}\n"
            index += 1
                
        embed = discord.Embed(title=f"{profession.value.capitalize()} Leaderboards ({scope.capitalize()})",description=description)
        
        embed.set_footer(text="Currently this is only among users registered in the bot. Game-wide leaderboards coming soon!\nTo fill in your own data, /register and /update_profile.")
        
        await ctx.reply(embed=embed)
        
    
async def setup(bot:commands.Bot):
    await bot.add_cog(RegistryCog())
    