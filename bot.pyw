from enum import Enum
import discord
from discord.ext import commands

import logging

from os import listdir
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
from dotenv import load_dotenv
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

class Game(Enum):
    OVERWATCH = 0
    ROCKET_LEAGUE = 1
    DEADLOCK = 2

class MyBot(commands.Bot):
    async def on_ready(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged on as {self.user}")
    
    async def load_extension(self, name, *, package = None):
        return await super().load_extension(name, package=package)

    async def setup_hook(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        COGS_DIR = os.path.join(BASE_DIR, "cogs")
        for cog in os.listdir(COGS_DIR):
            if cog.endswith('.py') == True:
                print(f"LOADING: cogs.{cog[:-3]}")
                await self.load_extension(f'cogs.{cog[:-3]}')
                
        await self.tree.sync() # Updates Slash Commands
        return await super().setup_hook()    
    
class SheetsManagement():
    def __init__(self):
        creds = None
        self.OW_ADMIN_SHEET = os.environ.get("OW_ADMIN_SHEET")
        self.RL_ADMIN_SHEET = os.environ.get("RL_ADMIN_SHEET")
        self.DL_ADMIN_SHEET = os.environ.get("DL_ADMIN_SHEET")
        #self.VAL_ADMIN_SHEET = os.environ.get("VAL_ADMIN_SHEET")
        self.VERIFICATION_SHEET = os.environ.get("VERIFICATION_SHEET")

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SERVICE_ACCOUNT_PATH = os.path.join(
            BASE_DIR,
            "service-account.json"
        )

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH,
            scopes=SCOPES
        )

        self.service = build(
            "sheets",
            "v4",
            credentials=creds
        )

        self.sheet = self.service.spreadsheets()

    def get_admin_sheet(self, game):
        if (game == Game.OVERWATCH):
            return self.OW_ADMIN_SHEET
        if (game == Game.ROCKET_LEAGUE):
            return self.RL_ADMIN_SHEET
        if (game == Game.DEADLOCK):
            return self.DL_ADMIN_SHEET
        #if (game == Game.VALORANT):
            #return self.VAL_ADMIN_SHEET
        
        return self.OW_ADMIN_SHEET
    
    def write_data(self, data, query, game):
        body = {"values": data}
        
        sheet = self.get_admin_sheet(game);
        result = (self.service.spreadsheets()
            .values().update(
                spreadsheetId=sheet,
                range=query,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute())

    def read_data(self, query, game):
        sheet = self.get_admin_sheet(game);
        result = (
        self.sheet.values()
        .get(spreadsheetId=sheet, range=query)
        .execute())
        return result.get("values", [])
    
    def read_verified(self):
        try:
            result = (
            self.sheet.values()
            .get(spreadsheetId=self.VERIFICATION_SHEET, range="Sheet1!C:F")
            .execute())
            values = result.get("values", [])
            col_indexes = [0, 3] 

            return [[row[i] for i in col_indexes if i < len(row)] for row in values]
        except:
            logging.log(5, "Verification could not be read..")
            return [];
        

def main():
    INTENTS = discord.Intents.default()
    INTENTS.message_content = True
    INTENTS.members = True

    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

    client = MyBot(command_prefix='!', intents=INTENTS)
    
    client.run(os.environ.get('DISCORD_BOT_TOKEN'), log_handler=handler, root_logger=True)

if __name__ == "__main__":
    main()