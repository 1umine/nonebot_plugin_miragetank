from nonebot import require, on_command
from nonebot.adapters import Message
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.log import logger
from nonebot.params import CommandArg

require("nonebot_plugin_alconna")
require("nonebot_plugin_waiter")

from nonebot_plugin_alconna import Image, UniMessage
from nonebot_plugin_waiter import waiter

from .data_source import color_car, get_imgs, gray_car, seperate
from .depends import Images, Mode, Bright, get_img_urls


__plugin_meta__ = PluginMetadata(
    name="miragetank",
    description="合成/分离幻影坦克图片",
    usage="""
/miragetank <图片1> <图片2>
/分离幻影坦克 <图片> [亮度增强值]

可选参数：
    亮度增强值：取值建议 1~6，默认2（对应本插件合成的gray模式图，color模式图建议设置为5.5）
    """.strip(),
    type="application",
    homepage="https://github.com/1umine/nonebot_plugin_miragetank",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

PRIORITY = 27
BLOCK = True
mirage_tank = on_command(
    "生成幻影坦克",
    aliases={"miragetank", "幻影坦克", "合成幻影坦克"},
    priority=PRIORITY,
    block=BLOCK,
)
sep_miragetank = on_command("分离幻影坦克", priority=PRIORITY, block=BLOCK)


@mirage_tank.handle()
async def _(
    matched_imgs: list[Image] = Images(),
    mode: Message = CommandArg(),
):
    img_urls = get_img_urls(msg_imgs=matched_imgs)
    generate_mode = mode.extract_plain_text().strip()
    is_valid_mode = lambda: generate_mode in ("gray", "color")
    if not is_valid_mode():
        await mirage_tank.send("请输入合成模式: gray 或 color")
    elif len(img_urls) < 2:
        await mirage_tank.send(f"还需要 {2 - len(img_urls)} 张图")

    if not (is_valid_mode() and len(img_urls) >= 2):

        @waiter(waits=["message"], keep_session=True)
        async def get_params(m: str = Mode(), imgs: list[Image] = Images()):
            return m, imgs

        async for r in get_params(retry=5, prompt=""):  # type: ignore
            r: tuple[str, list[Image]]
            m, imgs = r
            if m and m.strip() in ("取消", "结束", "算了"):
                await mirage_tank.finish("已取消")

            if m and m.strip() in ("gray", "color"):
                generate_mode = m
            if not is_valid_mode():
                await mirage_tank.send("请输入合成模式: gray/color (二选一)")

            if imgs and len(img_urls) < 2:
                img_urls.extend(img.url for img in imgs if img.url)

            if len(img_urls) < 2:
                await mirage_tank.send(f"还需要 {2 - len(img_urls)} 张图")
            elif generate_mode:  # 图片数量已满足，生成模式已提供
                break

    await mirage_tank.send("开始合成...")
    wimg, bimg = await get_imgs(img_urls[:2])
    if not wimg:
        await mirage_tank.finish("表图下载失败")
    if not bimg:
        await mirage_tank.finish("里图下载失败")

    if generate_mode == "color":
        await UniMessage.image(raw=color_car(wimg, bimg)).send()
    elif generate_mode == "gray":
        await UniMessage.image(raw=gray_car(wimg, bimg)).send()


# 分离幻影坦克
@sep_miragetank.handle()
async def _(
    images: list[Image] = Images(),
    bright: float = Bright(),
):
    img_urls = get_img_urls(msg_imgs=images)
    if not img_urls:
        await sep_miragetank.send("请发送一张幻影坦克图片")

        @waiter(waits=["message"], keep_session=True)
        async def get_img(imgs: list[Image] = Images()):
            img_urls.extend(get_img_urls(msg_imgs=imgs))
            return img_urls

        async for r in get_img(retry=2, prompt="请发送一张幻影坦克图片"):
            if r:
                break
        else:
            if not img_urls:
                await sep_miragetank.finish("已终止")

    await sep_miragetank.send("稍等，正在分离")
    img = (await get_imgs(img_urls[:1]))[0]
    if not img:
        await sep_miragetank.finish("图片下载失败")

    if img.format != "PNG":
        await sep_miragetank.finish(f"图片格式为 {img.format or '未知'}, 需要 PNG")
    try:
        outer, inner = seperate(img, bright_factor=bright)
    except Exception as e:
        logger.error(f"分离幻影坦克失败：{e}")
        await UniMessage.text("分离失败，请稍后再试").send(at_sender=True)
    await UniMessage.image(raw=outer).image(raw=inner).send(at_sender=True)
