import discord
from Helpers import data,constants
from discord.ext import commands

async def send_register_modal(interaction:discord.Interaction):
    class RegisterModal(discord.ui.Modal, title="Register Profile"):
        username = discord.ui.TextInput(label="Player Name", required=True)
        region = discord.ui.TextInput(label="Region",required=True,placeholder="Enter your region's number, found with F4 (with debug keys on).")
        empire = discord.ui.TextInput(label="Empire", required=False, default='None',placeholder="Enter your empire's name as it appears ingame, or leave blank if none.")
        claim = discord.ui.TextInput(label="Claim", required=False, default='None',placeholder="Enter your claim's name as it appears ingame, or leave blank if none.")

        async def on_submit(self, interaction:discord.Interaction):
            profile = None
            try:
                user_id = interaction.user.id
                username = self.username.value
                region = int(self.region.value)
                empire = self.empire.value
                claim = self.claim.value
                
                profile = create_user_profile(user_id, username, region, empire, claim)
                
                await interaction.response.send_message(f"Profile created for {profile['username']}!", ephemeral=True)
            except:
                return await interaction.response.send_message(f"Error detected, profile has{'' if profile != None else ' not'} been registered.",ephemeral=True)
            
            
        
    modal = RegisterModal()
    await interaction.response.send_modal(modal)

def create_user_profile(user_id, username, region, empire='None', claim='None'):
    """
    Creates a user profile in the database.
    
    :param user_id: The ID of the user.
    :param username: The username of the user.
    :param empire: The empire of the user (default is 'None').
    :param claim: The claim of the user (default is 'None').
    """
    conn, cursor = data.get_connection()
    
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, region, empire, claim) VALUES (?, ?, ?, ?, ?)",
                   (user_id, username, region, empire, claim))
    
    try:
        return data.GetOne("users",{"user_id":user_id})
    finally: data.close_connection(conn)

async def refresh_verification_messages(bot: commands.Bot):
    """Refresh verification messages in all guilds."""
    for message_data in data.Get("verification_messages"):
        guild = bot.get_guild(message_data['guild_id']) or await bot.fetch_guild(message_data['guild_id'])
        if guild:
            channel = guild.get_channel(message_data['channel_id']) or await guild.fetch_channel(message_data['channel_id'])
            if channel:
                try:
                    message = await channel.fetch_message(message_data['message_id'])
                except discord.NotFound:
                    print(f"Message {message_data['message_id']} not found in channel {message_data['channel_id']} of guild {guild.name} (ID: {guild.id})")
                    continue
        
                embed = discord.Embed(
                    title="Verification",
                    description="Click the button below to verify yourself.",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="This will be changed in the future when API access reopens.")
                
                class VerificationButton(discord.ui.View):
                    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
                    async def verify_button(self, interaction: discord.Interaction,button: discord.ui.Button):
                        user_id = interaction.user.id
                        if data.GetOne("users", {"user_id": user_id}):
                            await interaction.response.send_message("You are already verified.", ephemeral=True)
                        else:
                            await send_register_modal(interaction)
                view = VerificationButton()
                
                await message.edit(embed=embed, view=view)
            else:
                print(f"Channel {message_data['channel_id']} not found in guild {guild.name} (ID: {guild.id})")
        else:
            print(f"Guild {message_data['guild_id']} not found for verification message refresh.")