import logging
import discord
from redbot.core import Config, commands
from redbot.core import commands, app_commands

log = logging.getLogger("red.botc.follow")

class FollowCog(commands.Cog):
    """Allows members to follow arround a specific player"""

    __version__ = "0.0.1"
    __author__ = "Burnacid"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=68468174687465121987)
        default_guild = {
            "follows": {}
        }
        self.config.register_guild(**default_guild)
        pass
    
    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(member="The member you want to follow")
    async def follow(self, interaction: discord.Interaction, member: discord.Member):
        """Follow a member around through voicechannels"""

        # Initial Tests / Errors
        if interaction.user.id == member.id:
            await interaction.response.send_message(f"That is funny, you like to follow yourself. Are you a dog running after your own tail?", ephemeral=True)
            return
        
        if interaction.user.voice is None:
            await interaction.response.send_message(f"You are not connected to any voice channel. Please connect first!", ephemeral=True)
            return

        if member.voice is None:
            await interaction.response.send_message(f"{member.mention} is not connected to a voice channel", ephemeral=True)
            return
        
        permissions = member.voice.channel.permissions_for(interaction.user)

        if not permissions.connect:
            await interaction.response.send_message(f"You cannot follow {member.mention} here! Make sure you can connect to the channel you like to follow someone from.", ephemeral=True)
            return
        
        await interaction.response.send_message(f"{member.mention} you are being followed by {interaction.user.mention}")

        try:
            async with self.config.guild(interaction.guild).follows() as follow_list:
                # Remove old follows if exists
                for k in follow_list:
                    if interaction.user.id in follow_list[k]:
                        follow_list[k].remove(interaction.user.id)


                if str(member.id) in follow_list:
                    follow_list[str(member.id)].append(interaction.user.id)
                else:
                    follow_list[str(member.id)] = [interaction.user.id]

            
            # Move to member who is being followed
            if interaction.user.voice.channel.id != member.voice.channel.id:
                await interaction.user.move_to(member.voice.channel, reason=f"Following {member.name}")
        except Exception as e:
            log.error(e)
        
    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.describe(member="The member you want to remove from following you")
    async def removefollow(self, interaction: discord.Interaction, member: discord.Member = None):
        """Remove someone or everyone from following you"""

        # Check if this member is being followed
        async with self.config.guild(interaction.guild).follows() as follow_list:
            followers = follow_list.get(str(interaction.user.id), None)

            if followers is None:
                await interaction.response.send_message(f"You are not being followed!", ephemeral=True)
                return
        
            if member is None:
                listUnfollows = []
                for m in follow_list[str(interaction.user.id)]:
                    guildMember = interaction.guild.get_member(m)

                    if guildMember is not None:
                        listUnfollows.append(guildMember.mention)

                    follow_list[str(interaction.user.id)].remove(m)
                
                if len(listUnfollows) > 0:
                    unfollowString = ", ".join(listUnfollows)
                    await interaction.response.send_message(f"{interaction.user.mention} has removed {unfollowString} from following them", ephemeral=False)
                else:
                    await interaction.response.send_message(f"You are no longer being followed by anyone", ephemeral=True)
            else:
                if member.id not in followers:
                    await interaction.response.send_message(f"{member.mention} is not following you!", ephemeral=True)
                    return
                
                follow_list[str(interaction.user.id)].remove(member.id)
                await interaction.response.send_message(f"{interaction.user.mention} has removed {member.mention} from following them", ephemeral=False)

    @app_commands.command()
    @app_commands.guild_only()
    async def unfollow(self, interaction: discord.Interaction):
        """Stop following if you are following someone"""

        try:
            # Check if this member is being followed
            async with self.config.guild(interaction.guild).follows() as follow_list:
                for k in follow_list:
                    if interaction.user.id in follow_list[k]:
                        member_following = interaction.guild.get_member(k)
                        log.debug(k)

                        if member_following is None:
                            await interaction.response.send_message(f"You are no longer following a ghost", ephemeral=True)
                            return

                        follow_list[k].remove(interaction.user.id)
                        await interaction.response.send_message(f"{interaction.user.mention} is no longer following {member_following.mention}", ephemeral=False)
                        return
        
            await interaction.response.send_message(f"You are not following anyone", ephemeral=True)

        except Exception as e:
            log.error(e)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):

        try:
            # Check if this member is being followed
            async with self.config.guild(member.guild).follows() as follow_list:
                if str(member.id) in follow_list:
                    # Member is being followed

                    if after.channel is None:
                        del(follow_list[str(member.id)])
                        log.debug("Member that was followed has disconnected. Cleanup")
                        return
                    
                    for m in follow_list[str(member.id)]:
                        member_to_move = member.guild.get_member(m)

                        if member_to_move is None:
                            log.debug("Remove follow because member is not found in the guild")
                            follow_list[str(member.id)].remove(m)
                            continue

                        if member_to_move.voice is None:
                            log.debug("Remove follow because member is no longer connected to a voice channel")
                            follow_list[str(member.id)].remove(m)
                            continue

                        await member_to_move.move_to(after.channel)
                        log.debug(f"Move {m}")

                # Remove follows if user is disconnected
                if after.channel is None:
                    for k in follow_list:
                        if member.id in follow_list[str(k)]:
                            follow_list[str(k)].remove(member.id)
                            log.debug("Remove follow from disconnected member")
                
        except Exception as e:
            log.error(e)
                
                

        