import discord

import kaizen85modules

MUTED_ROLE_ID = 397808474320404482
MODLOG_CHANNEL_ID = 485572652099174401


def pluralize_russian(number, nom_sing, gen_sing, gen_pl):
    s_last_digit = str(number)[-1]

    if int(str(number)[-2:]) in range(11, 20):
        # 11-19
        return gen_pl
    elif s_last_digit == '1':
        # 1
        return nom_sing
    elif int(s_last_digit) in range(2, 5):
        # 2,3,4
        return gen_sing
    else:
        # 5,6,7,8,9,0
        return gen_pl


class TempMutedMember:
    id = 0
    unmute_time = 0


class Module(kaizen85modules.ModuleHandler.Module):
    name = "Moderation"
    desc = "Полезные команды для модерации"

    async def run(self, bot: kaizen85modules.KaizenBot):
        bot.module_handler.add_param("moderation_mutes", [])

        class CommandPurge(bot.module_handler.Command):
            name = "purge"
            desc = "Удалить большое кол-во сообщений."
            args = "<1 - 100> [@пользователь]"
            permissions = ["manage_messages"]

            async def run(self, message: discord.Message, args: str, keys):
                if len(args) < 1:
                    return False

                try:
                    limit = int(args[0])
                except ValueError:
                    return False

                if limit < 1 or limit > 100:
                    return False

                def check(msg):
                    return True if len(message.mentions) < 1 else msg.author == message.mentions[0]

                await message.delete()

                deleted = await message.channel.purge(limit=limit, check=check)
                await bot.send_ok_embed(message.channel, "%s: Удалено %s %s." % (message.author.mention, len(deleted),
                                                                                 pluralize_russian(len(deleted),
                                                                                                   "сообщение",
                                                                                                   "сообщения",
                                                                                                   "сообщений")))

                return True

        class CommandMute(bot.module_handler.Command):
            name = "mute"
            desc = "Замутить пользователя навсегда."
            args = "<@пользователь> [причина]"
            permissions = ["manage_roles"]

            async def run(self, message: discord.Message, args: str, keys):
                if len(message.mentions) < 1:
                    return False

                if message.mentions[0] == bot.user:
                    await bot.send_error_embed(message.channel, "Вы не можете замутить бота!")
                    return True

                if message.mentions[0] == message.author:
                    await bot.send_error_embed(message.channel, "Вы не можете замутить самого себя!")
                    return True

                role = message.guild.get_role(MUTED_ROLE_ID)

                if role is None:
                    await bot.send_error_embed(message.channel, "Роль с ID %s не найдена!" % MUTED_ROLE_ID)
                    return True

                if role in message.mentions[0].roles:
                    await bot.send_error_embed(message.channel, "Этот пользователь уже в муте!")
                    return True

                if message.author.guild_permissions < message.mentions[0].guild_permissions:
                    await bot.send_error_embed(message.channel, "Вы не можете замутить этого пользователя.")
                    return True

                reason = None

                if len(args) > 1:
                    reason = " ".join(args[1:])

                await message.mentions[0].add_roles(role, reason=reason)
                await bot.send_error_embed(bot.get_channel(MODLOG_CHANNEL_ID), "%s был заткнут %s навсегда!" % (
                    message.mentions[0].mention, message.author.mention), "Информация")

                return True

            class CommandUnmute(bot.module_handler.Command):
                name = "unmute"
                desc = "Снять мут с пользователя."
                args = "<@пользователь>"
                permissions = ["manage_roles"]

                async def run(self, message: discord.Message, args: str, keys):
                    if len(message.mentions) < 1:
                        return False

                    role = message.guild.get_role(MUTED_ROLE_ID)

                    if role is None:
                        await bot.send_error_embed(message.channel, "Роль с ID %s не найдена!" % MUTED_ROLE_ID)
                        return True

                    if role not in message.mentions[0].roles:
                        await bot.send_error_embed(message.channel, "Этот пользователь не в муте!")
                        return True

                    await message.mentions[0].add_roles(role, reason="Unmute")
                    await bot.send_ok_embed(bot.get_channel(MODLOG_CHANNEL_ID), "%s снял мут с %s." % (
                        message.author.mention, message.mentions[0].mention), "Информация")

                    return True

        bot.module_handler.add_command(CommandPurge(), self)
        bot.module_handler.add_command(CommandMute(), self)
        bot.module_handler.add_command(CommandMute(), self)
