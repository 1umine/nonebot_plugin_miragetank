import re
from nonebot.adapters import Bot, Event
from nonebot.params import Depends

from nonebot_plugin_alconna.uniseg import reply_fetch
from nonebot_plugin_alconna import Image, UniMessage


def Images():
    """
    消息包含的图片
    
    支持获取回复的消息中的图片
    """
    async def d(bot: Bot, event: Event):
        reply = await reply_fetch(event, bot)
        msg = UniMessage.generate_without_reply(event=event, bot=bot)
        if reply:
            msg.extend(UniMessage.generate_without_reply(message=reply.msg))  # type: ignore
        return msg.get(Image)

    return Depends(d)


def Mode():
    """
    幻影坦克合成模式: gray / color

    支持从回复消息中获取
    """
    async def d(bot: Bot, event: Event):
        reply = await reply_fetch(event, bot)
        m = ""
        if reply and reply.msg:
            m = (
                reply.msg.strip()
                if isinstance(reply.msg, str)
                else reply.msg.extract_plain_text().strip()
            )
        return event.get_plaintext().strip() or m

    return Depends(d)


def Bright():
    async def d(bot: Bot, event: Event):
        reply = await reply_fetch(event, bot)
        b = ""
        if reply and reply.msg:
            b = (
                reply.msg.strip()
                if isinstance(reply.msg, str)
                else reply.msg.extract_plain_text().strip()
            )
        matched_nums = re.search(r"\d+.?\d+", event.get_plaintext() + " " + b)
        if matched_nums:
            bright = float(matched_nums.group())
            if bright > 6:
                bright = 6.0
            return bright
        return 2.0

    return Depends(d)


def get_img_urls(msg_imgs: list[Image] = []):
    img_urls: list[str] = []
    if msg_imgs:
        img_urls.extend(img.url for img in msg_imgs if img.url)
    return img_urls
