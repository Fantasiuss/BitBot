import discord
from discord.ext import commands
from Helpers import constants,data

def create_user_profile(user_id, username, empire='None', claim='None'):
    """
    Creates a user profile in the database.
    
    :param user_id: The ID of the user.
    :param username: The username of the user.
    :param empire: The empire of the user (default is 'None').
    :param claim: The claim of the user (default is 'None').
    """
    conn, cursor = data.get_connection()
    
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, empire, claim) VALUES (?, ?, ?, ?)",
                   (user_id, username, empire, claim))
    
    cursor.execute("INSERT OR IGNORE INTO profession_data (user_id) VALUES (?)", (user_id,))
    
    data.close_connection(conn)
    
    return {"user_id":user_id,"username":username,"empire":empire,"claim":claim}

class RegistryCog(commands.Cog):
    def __init__(self):
        self.bot = constants.bot

    @commands.hybrid_command(description="View your profile or another user's profile.")
    async def profile(self, ctx:commands.Context, user:discord.User=None):
        """View your profile or another user's profile."""
        if user is None:
            user = ctx.author
        
        # Fetch user data from the database
        user_data = data.GetOne("users", {"user_id": user.id})
        profession_data = data.GetOne("profession_data", {"user_id": user.id})
        
        if user_data is None or profession_data is None:
            await ctx.send(f"No profile found for {user.name}.",ephemeral=True)
            return
        
        embed = discord.Embed(title=f"{user_data["username"]}'s Profile", color=discord.Color.blue())
        embed.add_field(name="Empire", value=user_data["empire"], inline=True)
        embed.add_field(name="Claim", value=user_data["claim"], inline=True)
        
        embed.add_field(name="", value="", inline=False)
        
        embed.add_field(name="Carpentry", value=profession_data["carpentry"], inline=True)
        embed.add_field(name="Mining", value=profession_data["mining"], inline=True)
        embed.add_field(name="Fishing", value=profession_data["fishing"], inline=True)
        embed.add_field(name="Farming", value=profession_data["farming"], inline=True)
        embed.add_field(name="Foraging", value=profession_data["foraging"], inline=True)
        embed.add_field(name="Forestry", value=profession_data["forestry"], inline=True)
        embed.add_field(name="Scholar", value=profession_data["scholar"], inline=True)
        embed.add_field(name="Masonry", value=profession_data["masonry"], inline=True)
        embed.add_field(name="Smithing", value=profession_data["smithing"], inline=True)
        embed.add_field(name="Tailoring", value=profession_data["tailoring"], inline=True)
        embed.add_field(name="Hunting", value=profession_data["hunting"], inline=True)
        embed.add_field(name="Leatherworking", value=profession_data["leatherworking"], inline=True)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        
        embed.set_footer(text="Use /register to create your own profile.")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(description="Register a new user profile.")
    async def register(self, ctx:commands.Context):
        user_data = data.GetOne("users", {"user_id": ctx.author.id})
        
        if not (user_data is None):
            await ctx.send(f"You are already registered as {user_data['username']}.",ephemeral=True)
            return
        
        class RegisterModal(discord.ui.Modal, title="Register Profile"):
            username = discord.ui.TextInput(label="Player Name", required=True)
            empire = discord.ui.TextInput(label="Empire", required=False, default='None')
            claim = discord.ui.TextInput(label="Claim", required=False, default='None')

            async def on_submit(self, interaction:discord.Interaction):
                user_id = interaction.user.id
                username = self.username.value
                empire = self.empire.value
                claim = self.claim.value
                
                profile = create_user_profile(user_id, username, empire, claim)
                
                await interaction.response.send_message(f"Profile created for {profile['username']}!", ephemeral=True)
        
        modal = RegisterModal()
        await ctx.interaction.response.send_modal(modal)
    
    @discord.app_commands.user_install()
    @commands.hybrid_command(description="Update your profile.")
    @discord.app_commands.choices(options=[discord.app_commands.Choice(name="Professions",value="professions"),discord.app_commands.Choice(name="Empire", value="empire"), discord.app_commands.Choice(name="Claim", value="claim")])
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
                profession_data = data.GetOne("profession_data", {"user_id": ctx.author.id})
                
                class ProfessionModalOne(discord.ui.Modal):
                    def __init__(self, *, title = "Update Professions", timeout = None):
                        super().__init__(title=title, timeout=timeout)
                    
                    carpentry = discord.ui.TextInput(label="Carpentry", required=True, placeholder=profession_data["carpentry"] if profession_data else "1")
                    fishing = discord.ui.TextInput(label="Fishing", required=True, placeholder=profession_data["fishing"] if profession_data else "1")
                    farming = discord.ui.TextInput(label="Farming", required=True, placeholder=profession_data["farming"] if profession_data else "1")
                    foraging = discord.ui.TextInput(label="Foraging", required=True, placeholder=profession_data["foraging"] if profession_data else "1")
                    
                    async def on_submit(self, interaction:discord.Interaction):
                        cursor.execute("UPDATE profession_data SET "
                                       "carpentry = ?, mining = ?, fishing = ?, farming = ?, "
                                       "foraging = ?, forestry = ?, scholar = ?, masonry = ?, "
                                       "smithing = ?, tailoring = ?, hunting = ?, leatherworking = ? "
                                       "WHERE user_id = ?",
                                       (self.carpentry.value, profession_data["mining"], self.fishing.value,
                                        self.farming.value, self.foraging.value, profession_data["forestry"],
                                        profession_data["scholar"], profession_data["masonry"], profession_data["smithing"],
                                        profession_data["tailoring"], profession_data["hunting"], profession_data["leatherworking"],
                                        interaction.user.id))
                        conn.commit()
                        conn.close()
                        
                        await interaction.response.send_message(f"Professions updated!", ephemeral=True)
                class ProfessionModalTwo(discord.ui.Modal):
                    def __init__(self, *, title = "Update Professions", timeout = None):
                        super().__init__(title=title, timeout=timeout)
                    
                    forestry = discord.ui.TextInput(label="Forestry", required=True, placeholder=profession_data["forestry"] if profession_data else "1")
                    hunting = discord.ui.TextInput(label="Hunting", required=True, placeholder=profession_data["hunting"] if profession_data else "1")  
                    leatherworking = discord.ui.TextInput(label="Leatherworking", required=True, placeholder=profession_data["leatherworking"] if profession_data else "1")
                    masonry = discord.ui.TextInput(label="Masonry", required=True, placeholder=profession_data["masonry"] if profession_data else "1")
                    
                    async def on_submit(self, interaction:discord.Interaction):
                        cursor.execute("UPDATE profession_data SET "
                                       "carpentry = ?, mining = ?, fishing = ?, farming = ?, "
                                       "foraging = ?, forestry = ?, scholar = ?, masonry = ?, "
                                       "smithing = ?, tailoring = ?, hunting = ?, leatherworking = ? "
                                       "WHERE user_id = ?",
                                       (profession_data["carpentry"], profession_data["mining"], profession_data["fishing"],
                                        profession_data["farming"], profession_data["foraging"], self.forestry.value,
                                        profession_data["scholar"], self.masonry.value, profession_data["smithing"],
                                        profession_data["tailoring"], self.hunting.value, self.leatherworking.value,
                                        interaction.user.id))
                        conn.commit()
                        conn.close()
                        
                        await interaction.response.send_message(f"Professions updated!", ephemeral=True)
                class ProfessionModalThree(discord.ui.Modal):
                    def __init__(self, *, title = "Update Professions", timeout = None):
                        super().__init__(title=title, timeout=timeout)
                        
                    mining = discord.ui.TextInput(label="Mining", required=True, placeholder=profession_data["mining"] if profession_data else "1")
                    scholar = discord.ui.TextInput(label="Scholar", required=True, placeholder=profession_data["scholar"] if profession_data else "1")
                    smithing = discord.ui.TextInput(label="Smithing", required=True, placeholder=profession_data["smithing"] if profession_data else "1")
                    tailoring = discord.ui.TextInput(label="Tailoring", required=True, placeholder=profession_data["tailoring"] if profession_data else "1")
                    
                    async def on_submit(self, interaction:discord.Interaction):
                        cursor.execute("UPDATE profession_data SET "
                                       "carpentry = ?, mining = ?, fishing = ?, farming = ?, "
                                       "foraging = ?, forestry = ?, scholar = ?, masonry = ?, "
                                       "smithing = ?, tailoring = ?, hunting = ?, leatherworking = ? "
                                       "WHERE user_id = ?",
                                       (profession_data["carpentry"], self.mining.value, profession_data["fishing"],
                                        profession_data["farming"], profession_data["foraging"], profession_data["forestry"],
                                        self.scholar.value, profession_data["masonry"], self.smithing.value,
                                        self.tailoring.value, profession_data["hunting"], profession_data["leatherworking"],
                                        interaction.user.id))
                        conn.commit()
                        conn.close()
                        await interaction.response.send_message(f"Professions updated!", ephemeral=True)
                
                class SelectProfessionModal(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=360)
                    
                    @discord.ui.button(label="Row 1: Carpentry, Farming, Fishing, Foraging", style=discord.ButtonStyle.primary)
                    async def on_row_one_click(self, interaction:discord.Interaction,_):
                        modal = ProfessionModalOne()
                        await interaction.response.send_modal(modal)
                    
                    @discord.ui.button(label="Row 2: Forestry, Hunting, Leatherworking, Masonry", style=discord.ButtonStyle.primary)
                    async def on_row_two_click(self, interaction:discord.Interaction,_):
                        modal = ProfessionModalTwo()
                        await interaction.response.send_modal(modal)
                        
                    @discord.ui.button(label="Row 3: Mining, Scholar, Smithing, Tailoring", style=discord.ButtonStyle.primary)
                    async def on_row_three_click(self, interaction:discord.Interaction,_):
                        modal = ProfessionModalThree()
                        await interaction.response.send_modal(modal)
                    
                    async def on_button_click(self, interaction:discord.Interaction):
                        match interaction.custom_id:
                            case "one":
                                modal = ProfessionModalOne()
                                await interaction.response.send_modal(modal)
                            case "two":
                                modal = ProfessionModalTwo()
                                await interaction.response.send_modal(modal)
                            case "three":
                                modal = ProfessionModalThree()
                                await interaction.response.send_modal(modal)
                
                await ctx.reply("Select a profession to update:", view=SelectProfessionModal(),ephemeral=True)
    
async def setup(bot:commands.Bot):
    await bot.add_cog(RegistryCog())
    