import discord
from discord.ext import commands
from Helpers import constants,data,checks,functions
import discord.ext

class VerificationCog(commands.Cog):
    def __init__(self):
        self.bot = constants.bot

    @commands.hybrid_command()
    @checks.is_admin()
    async def verification_embed(self, ctx: commands.Context):
        """Creates a verification embed in the current channel."""
        await ctx.interaction.response.defer(ephemeral=True)
        
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
                    await functions.send_register_modal(interaction)
        view = VerificationButton()
        
        try:
            message = await ctx.channel.send(embed=embed, view=view)
        except discord.Forbidden:
            return await ctx.reply("I do not have permission to send messages in this channel.", ephemeral=True)
            
        try:
            existing_message_data = data.GetOne("verification_messages", {"guild_id": ctx.guild.id, "channel_id": ctx.channel.id})
            if existing_message_data:
                guild = constants.bot.get_guild(ctx.guild.id) or await self.bot.fetch_guild(ctx.guild.id)
                if guild:
                    channel = guild.get_channel(ctx.channel.id) or await guild.fetch_channel(ctx.channel.id)
                    if channel:
                        try:
                            existing_message = await channel.fetch_message(existing_message_data["message_id"])
                            await existing_message.delete()
                        except discord.NotFound:
                            print(f"Message {existing_message_data['message_id']} not found in channel {ctx.channel.id} of guild {ctx.guild.id}")
        except:
            pass
        
        data.Update("verification_messages", {"guild_id": ctx.guild.id},{"channel_id": ctx.channel.id, "message_id": message.id})
        await ctx.interaction.followup.send("Verification embed created successfully.", ephemeral=True)
        
        
    
async def setup(bot:commands.Bot):
    await bot.add_cog(VerificationCog())
    