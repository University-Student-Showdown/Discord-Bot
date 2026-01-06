from enum import Enum
import discord
from discord.ext import commands

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent

sys.path.append(str(parent_dir))

from bot import SheetsManagement, Game

USS_COLOUR = 0x992299
OW_ADMIN_ROLE_NAME = "ow admin"
RL_ADMIN_ROLE_NAME = "rl admin"
LEAD_ROLE_NAME = "staff lead"


def is_admin():
    async def predicate(ctx):
        return any((role.name.lower() == OW_ADMIN_ROLE_NAME or  role.name.lower() == RL_ADMIN_ROLE_NAME or role.name.lower() == LEAD_ROLE_NAME) for role in ctx.author.roles)
    return commands.check(predicate)

class GameData():
    def __init__(self):
        self.teamsMapped = {}
        self.teamsMapped_user = {}
        self.checkInActive = {}

class CheckInCommands(commands.Cog):
    def __init__(self, bot):
        self.manager = SheetsManagement()
        self.overwatch = GameData();
        self.rocket_league = GameData();

        self.sync_team_data()

    @commands.hybrid_group(name="rl")
    async def rl(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply("Available subcommands: checkin, checkout, getcaptain")

    @commands.hybrid_group(name="ow")
    async def ow(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply("Available subcommands: checkin, checkout, getcaptain")

    
    @rl.command(name="checkin")
    async def check_in(self, ctx):
        sender : discord.Member = ctx.author

        if (self.checkInActive):
            message = self.check_in_sheet(sender.name, Game.ROCKET_LEAGUE)
        else:
            message = "Check-Ins are currently closed."

        embed = discord.Embed(title="USS Checkin - Rocket League", description=message, colour=USS_COLOUR)
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1969783689090363392/v_27TFgp_400x400.jpg")

        await ctx.reply(embed=embed)

    @ow.command(name="checkin")
    async def check_in(self, ctx):
        sender : discord.Member = ctx.author

        if (self.checkInActive):
            message = self.check_in_sheet(sender.name, Game.Overwatch)
        else:
            message = "Check-Ins are currently closed."

        embed = discord.Embed(title="USS Checkin - Overwatch", description=message, colour=USS_COLOUR)
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1969783689090363392/v_27TFgp_400x400.jpg")

        await ctx.reply(embed=embed)

    @rl.command(name="checkout")
    async def check_out(self, ctx):
        sender : discord.Member = ctx.author

        if (self.checkInActive):
            message = self.check_out_sheet(sender.name, Game.ROCKET_LEAGUE)
        else:
            message = "Check-Ins are currently closed."
            
        embed = discord.Embed(title="USS Checkin - Rocket League", description=message, colour=USS_COLOUR)
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1969783689090363392/v_27TFgp_400x400.jpg")

        await ctx.reply(embed=embed)

    @ow.command(name="checkout")
    async def check_out(self, ctx):
        sender : discord.Member = ctx.author

        if (self.checkInActive):
            message = self.check_out_sheet(sender.name, Game.OVERWATCH)
        else:
            message = "Check-Ins are currently closed."
            
        embed = discord.Embed(title="USS Checkin - Overwatch", description=message, colour=USS_COLOUR)
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1969783689090363392/v_27TFgp_400x400.jpg")

        await ctx.reply(embed=embed)

    @rl.command(name="getcaptain")
    async def get_connection(self, ctx, team :str):
        if team.lower() not in self.rocket_league.teamsMapped:
            message = f"Could not find team {team}"
        else:
            message = f"""**{self.rocket_league.teamsMapped[team.lower()]['formalised_name']}**\nCaptain's Discord: {self.rocket_league.teamsMapped[team.lower()]['discord']}\n
            **Players:**
            {self.rocket_league.teamsMapped[team.lower()]['conn']}
            {self.rocket_league.teamsMapped[team.lower()]['conn2']}
            {self.rocket_league.teamsMapped[team.lower()]['conn3']}
            {self.rocket_league.teamsMapped[team.lower()]['conn4']}
            {self.rocket_league.teamsMapped[team.lower()]['conn5']}
            """
        embed = discord.Embed(title="USS - Rocket League", description=message, colour=USS_COLOUR)
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1969783689090363392/v_27TFgp_400x400.jpg")
        await ctx.reply(embed=embed)

    @ow.command(name="getcaptain")
    async def get_connection(self, ctx, team :str):
        if team.lower() not in self.overwatch.teamsMapped:
            message = f"Could not find team {team}"
        else:
            message = f"""**{self.overwatch.teamsMapped[team.lower()]['formalised_name']}**\nCaptain's Discord: {self.overwatch.teamsMapped[team.lower()]['discord']}\n
            **Players:**
            {self.overwatch.teamsMapped[team.lower()]['conn']}
            {self.overwatch.teamsMapped[team.lower()]['conn2']}
            {self.overwatch.teamsMapped[team.lower()]['conn3']}
            {self.overwatch.teamsMapped[team.lower()]['conn4']}
            {self.overwatch.teamsMapped[team.lower()]['conn5']}
            """
        embed = discord.Embed(title="USS - Overwatch", description=message, colour=USS_COLOUR)
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1969783689090363392/v_27TFgp_400x400.jpg")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="refreshteamdata")
    @is_admin()
    async def refresh_team_data(self, ctx):
        self.sync_team_data()
        await ctx.reply("Refreshed data")


    @rl.group(name="admincheckin")
    async def rl_admincheckin(self, ctx):
        return

    @rl_admincheckin.command(name="open")
    @is_admin()
    async def open_check_in(self, ctx):
        self.checkInActive = True;
        await ctx.reply("Check-in has been opened")

    @rl_admincheckin.command(name="close")
    @is_admin()
    async def open_check_in(self, ctx):
        self.checkInActive = False;
        await ctx.reply("Check-in has been closed")

    @rl_admincheckin.command(name="status")
    @is_admin()
    async def open_check_in(self, ctx):
        if (self.checkInActive):
            await ctx.reply("Check-in is open")
        else:
            await ctx.reply("Check-in is closed")


    @ow.group(name="admincheckin")
    async def ow_admincheckin(self, ctx):
        return

    @ow_admincheckin.command(name="open")
    @is_admin()
    async def open_check_in(self, ctx):
        self.checkInActive = True;
        await ctx.reply("Check-in has been opened")

    @ow_admincheckin.command(name="close")
    @is_admin()
    async def open_check_in(self, ctx):
        self.checkInActive = False;
        await ctx.reply("Check-in has been closed")

    @ow_admincheckin.command(name="status")
    @is_admin()
    async def open_check_in(self, ctx):
        if (self.checkInActive):
            await ctx.reply("Check-in is open")
        else:
            await ctx.reply("Check-in is closed")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.reply("You need the **admin** role to use this command.")

    def get_game_obj(self, game:Game):
        if (game == Game.OVERWATCH):
            return self.overwatch
        else:
            return self.rocket_league

    def sync_team_data(self):
        self.rocket_league.teamsMapped.clear()
        data : list = self.manager.read_data("TeamContact!A2:G", Game.ROCKET_LEAGUE)
        for row in data:
            self.rocket_league.teamsMapped[row[0].lower()] = {"discord":row[1], "conn": row[2], "conn2": row[3], "conn3": row[4], "conn4": row[5], "conn5": row[6], "formalised_name": row[0]}
            self.rocket_league.teamsMapped_user[row[1].lower()] = {"team_name":row[0], "conn": row[2], "conn2": row[3], "conn3": row[4], "conn4": row[5], "conn5": row[6]}

        self.overwatch.teamsMapped.clear()
        data : list = self.manager.read_data("TeamContact!A2:G", Game.OVERWATCH)
        for row in data:
            self.overwatch.teamsMapped[row[0].lower()] = {"discord":row[1], "conn": row[2], "conn2": row[3], "conn3": row[4], "conn4": row[5], "conn5": row[6], "formalised_name": row[0]}
            self.overwatch.teamsMapped_user[row[1].lower()] = {"team_name":row[0], "conn": row[2], "conn2": row[3], "conn3": row[4], "conn4": row[5], "conn5": row[6]}

    def get_team_from_user(self, username : str, game: Game):
        gameObj = self.get_game_obj(game)
        if username not in gameObj.teamsMapped_user: return "N/A"

        return self.teamsMapped_user[username]["team_name"]

    def find_and_flip_checkin(self, teamName : str, checkin : bool, game: Game):
        if teamName == "N/A": return "You are not registered as a captain\n\nIf you believe this is wrong, please contact an admin"
        data : list = self.manager.read_data("Datasheet!A2:C", game)

        i = 2
        for row in data:
            if row[0] == teamName:
                flag = self.google_bool(row[2])
                if checkin and not flag:
                    self.manager.write_data([[checkin]], f"Datasheet!C{i}", game)
                    return f"Checked in {teamName}"
                elif checkin and flag:
                    return f"{teamName} are already checked in."
                elif not checkin and not flag:
                    return f"{teamName} are already checked out."
                else:
                    self.manager.write_data([[checkin]], f"Datasheet!C{i}", game)
                    return f"Checked out {teamName}"

            i = i+1

    def check_in_sheet(self, username:str, game: Game):
        return self.find_and_flip_checkin(self.get_team_from_user(username.lower(), game),True)
    
    def check_out_sheet(self, username:str, game: Game):
        return self.find_and_flip_checkin(self.get_team_from_user(username, game),False)
    
    def google_bool(self, value):
        if isinstance(value, bool):
            return value 
        if isinstance(value, str):
            return value.strip().upper() == "TRUE"
        return bool(value) 

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CheckInCommands(bot))