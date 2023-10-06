from typing import List, Dict
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.adapters.onebot.v11.helpers import HandleCancellation, Numbers
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .data_source import color_car, get_imgs, gray_car, seperate, GenInfo


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
    supported_adapters={"onebot"},
)

priority = 27

mirage_tank = on_command("生成幻影坦克", aliases={"miragetank", "幻影坦克"}, priority=priority)
sep_miragetank = on_command("分离幻影坦克", priority=priority)
gen_infos: Dict[str, GenInfo] = {}


def get_img_urls(event: MessageEvent):
    """
    获取消息中的图片链接（包括回复的消息）
    """
    urls: List[str] = []
    if event.reply:
        urls = [
            seg.data["url"]
            for seg in event.reply.message
            if (seg.type == "image") and ("url" in seg.data)
        ]
    urls.extend(
        [
            seg.data["url"]
            for seg in event.message
            if (seg.type == "image") and ("url" in seg.data)
        ]
    )
    return urls


@mirage_tank.handle()
async def handle_first(
    event: MessageEvent, state: T_State, args: Message = CommandArg()
):
    mode = args.extract_plain_text().strip()
    img_urls = get_img_urls(event)
    gen_info = GenInfo(mode, img_urls)
    gen_infos[event.get_session_id()] = gen_info
    if not gen_info.is_ready():
        state["miragetank_gen_prompt"] = f"缺少或存在不合法参数, 参数情况：\n{gen_info.params_info()}"
    else:
        state["miragetank_gen_info"] = True


@mirage_tank.got(
    "miragetank_gen_info",
    prompt=Message.template("{miragetank_gen_prompt}"),
    parameterless=[HandleCancellation("已取消")],
)
async def gen_img(event: MessageEvent, state: T_State):
    gen_info = gen_infos[event.get_session_id()]

    if not gen_info.valid_mode():
        gen_info.mode = event.get_plaintext().strip()
    if not gen_info.enough_img_url():
        gen_info.img_urls.extend(get_img_urls(event))

    if not gen_info.mode:
        await mirage_tank.reject("需要指定合成模式: gray | color")
    elif not gen_info.valid_mode():
        await mirage_tank.reject("合成模式必须为 gray | color")
    elif not gen_info.has_img():
        await mirage_tank.reject("请发送两张图片, 按表图，里图顺序")
    elif not gen_info.enough_img_url():
        await mirage_tank.reject("图片数量不足，请再发送一张")

    if gen_info.is_ready():
        gen_infos.pop(event.get_session_id())
        await mirage_tank.send("开始合成...")
        imgs = await get_imgs(gen_info.img_urls[:2])
        if len(imgs) < 2:
            await mirage_tank.finish("下载图片失败，过会再试吧")
        res = None
        if gen_info.mode == "gray":
            res = gray_car(*imgs)
        else:
            res = color_car(*imgs)
        if res:
            await mirage_tank.finish(MessageSegment.image(res))


# 分离幻影坦克
@sep_miragetank.handle()
async def _(
    event: MessageEvent,
    state: T_State,
    args: Message = CommandArg(),
    bright: List[float] = Numbers(),
):
    if event.reply:
        args.extend(event.reply.message)
    has_img = any(seg.type == "image" for seg in args)
    if has_img:
        state["miragetank_sep_img_url"] = args

    if bright:
        state["miragetank_sep_enhance_bright"] = bright[0]
    else:
        state["miragetank_sep_enhance_bright"] = 2


@sep_miragetank.got("miragetank_sep_img_url", prompt="请发送一张幻影坦克图片")
async def _(state: T_State):
    img_url = [
        seg.data["url"]
        for seg in state["miragetank_sep_img_url"]
        if seg.type == "image"
    ]
    if not img_url:
        await sep_miragetank.finish("没有检测到图片，已结束")

    img = await get_imgs(img_url[:1])
    if not img:
        await sep_miragetank.finish("图片下载失败，待会再试吧")
    elif img[0].format != "PNG":
        await sep_miragetank.finish(f"图片格式为 {img[0].format}, 需要 PNG")
    logger.info("获取幻影坦克图片成功")
    await sep_miragetank.send("稍等，正在分离")
    try:
        outer, inner = seperate(
            img[0], bright_factor=state["miragetank_sep_enhance_bright"]
        )
    except Exception as e:
        logger.error(f"分离幻影坦克失败：{e}")
        await sep_miragetank.finish(f"分离失败：{e}", at_sender=True)
    await sep_miragetank.finish(
        MessageSegment.image(outer) + MessageSegment.image(inner), at_sender=True
    )
