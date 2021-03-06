from typing import List

import discord
from discord.utils import get

import kaizen85modules


class VoteCommand(kaizen85modules.ModuleHandler.Command):
    name = "vote"
    desc = "Установить :check: и :cross-1: на ваше сообщение"
    args = ""

    def __init__(self, bot: kaizen85modules.KaizenBot):
        guild: discord.Guild = bot.get_guild(bot.GLOBAL_GUILD_LOCK)
        self.cross: discord.Emoji = get(guild.emojis, name="cross")
        self.bot = bot

    async def run(self, message: discord.Message, args: str, keys: List[str]) -> bool:
        await message.add_reaction(self.cross)
        return True


class Module(kaizen85modules.ModuleHandler.Module):
    name = "Vote"
    desc = "Позволяет автоматически ставить эмодзи на сообщение (крестик и галочка)"

    async def run(self, bot: kaizen85modules.KaizenBot):
        bot.module_handler.add_command(VoteCommand(bot), self)
