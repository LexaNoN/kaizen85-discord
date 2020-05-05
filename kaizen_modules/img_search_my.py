import os
import discord
import requests

import voxelmodules


request_url = "https://www.googleapis.com/customsearch/v1?q=%s&num=1&start=1" \
              "&searchType=image&key=%s&cx=%s"


class Module(voxelmodules.ModuleHandler.Module):
    name = "ImageSearch"
    desc = "Поиск картинок в Google с автоматическим помещением в спойлер при обнаружении NSFW (и цензурированием в " \
           "не NSFW каналах). "

    async def run(self, bot: voxelmodules.KaizenBot):

        cx = "Ключик"
        api_key = "Апи Ключик"

        if cx is None or api_key is None:
            bot.logger.log("[ImageSearch] CX or API key are not available. Check \"kaizen_image_search_cx\" amd "
                           "\"kaizen_image_search_apikey\" in PATH.")

        class CommandImg(bot.module_handler.Command):
            name = "img"
            desc = "Поиск изображений в Google"
            args = "<поисковый запрос>"
            keys = ["no-nsfw-check"]

            async def run(self, message: discord.Message, args, keys):
                if len(args) < 1:
                    return False
                global detector

                keyword = " ".join(message.clean_content.split()[1:])

                try:
                    resp = requests.get(request_url % (keyword, api_key, cx))
                except Exception:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при загрузке картинки по запросу \"%s\"!" % (
                                                   message.author.mention, keyword))
                    return True

                if resp.status_code != 200:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при загрузке картинки по запросу \"%s\": %s" % (
                                                   message.author.mention, keyword, resp.text))
                    return True

                data = resp.json()
                if data["searchInformation"]["totalResults"] == "0":
                    await bot.send_error_embed(message.channel, "%s, изображение по запросу \"%s\" не найдено!" % (
                        message.author.mention, keyword))
                    return True

                img_path = "./img_search/%s.%s" % (message.id, data["items"][0]["fileFormat"].split("/")[-1])

                try:
                    with open(img_path, "wb") as f:
                        f.write(requests.get(data["items"][0]["link"]).content)
                except Exception:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при скачивании картинки по запросу \"%s\"!" % (
                                                   message.author.mention, keyword))
                    return True
                global is_nsfw
                is_nsfw = False

                try:
                    if not ("no-nsfw-check" in keys
                            and bot.check_permissions(message.author.guild_permissions, ["administrator"])) \
                            and detector is not None:
                        is_nsfw = True if len(detector.detect(img_path)) > 0 else False
                except Exception:
                    pass
                resp1 = data
                jstr1 = resp1['items']
                jstrl1 = jstr1[0]
                content1 = jstrl1['link']

                r = requests.post(
                    "https://api.deepai.org/api/nsfw-detector",
                    data={
                        'image': content1,
                    },
                    headers={'api-key': 'Ещё ключик'}
                )
                resp = r.json()
                jstr = resp['output']
                jstrl = jstr
                content = jstrl['nsfw_score']
                if content >= 0.2:
                    detector = False
                    is_nsfw = True
                else:
                    detector = True
                    is_nsfw = False
                print(content)
                with open(img_path, "rb") as f:
                    img = discord.File(f, spoiler=is_nsfw)
                    await message.channel.send("Картинка по запросу \"%s\": (запросил: %s)%s%s" % (
                        keyword, message.author.mention if "anon" not in keys else "[данные удалены]",
                        "\n⚠️Обнаружен NSFW контент! Картинка спрятана под спойлер. Открывайте на свой страх и риск! ⚠️" if is_nsfw else "",
                        ""),
                                file=img)
                return True

        bot.module_handler.add_command(CommandImg(), self)
