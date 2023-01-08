from typing import List
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, MessageEvent
from nonebot.adapters.onebot.v11.helpers import HandleCancellation, Numbers
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

from .data_source import color_car, get_img, gray_car, seperate


__plugin_meta__ = PluginMetadata(
    name="miragetank",
    description="合成/分离幻影坦克图片",
    usage="""
/miragetank <图片1> <图片2>
/分离幻影坦克 <图片> [亮度增强值]

可选参数：
    亮度增强值：取值建议 1~6，默认3.3（对应本插件合成的gray模式图，color模式图建议设置为5.5）
    """.strip(),
)

priority = 27

mirage_tank = on_command("生成幻影坦克", aliases={"miragetank", "幻影坦克"}, priority=priority)
sep_miragetank = on_command("分离幻影坦克", priority=priority)


@mirage_tank.handle()
async def handle_first(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    args: Message = CommandArg(),
):
    images = []
    for seg in args:
        if seg.type == "text":
            state["mod"] = seg.data["text"].strip()
        elif seg.type == "image":
            images.append(seg)
    if len(images) >= 1:
        state["img1"] = images[0]
    if len(images) >= 2:
        state["img2"] = images[1]


@mirage_tank.got(
    "mod", prompt="需要指定结果类型: gray | color", parameterless=[HandleCancellation("已取消")]
)
async def get_mod(event: MessageEvent, state: T_State):
    mod = str(state["mod"]).strip()
    if mod not in ["gray", "color"]:
        await mirage_tank.reject('"gray" | "color", 二选一')


@mirage_tank.got(
    "img1", prompt="请发送两张图，按表里顺序", parameterless=[HandleCancellation("已取消")]
)
@mirage_tank.got("img2", prompt="还需要一张图", parameterless=[HandleCancellation("已取消")])
async def get_images(state: T_State):
    imgs = []
    mod = str(state["mod"])
    for seg in state["img1"] + state["img2"]:
        if seg.type != "image":
            await mirage_tank.reject("有个不是图")
        imgs.append(await get_img(seg.data["url"]))

    await mirage_tank.send("开始合成")

    res = None
    if mod == "gray":
        res = await gray_car(imgs[0], imgs[1])
    elif mod == "color":
        res = await color_car(imgs[0], imgs[1])
    if res:
        await mirage_tank.finish(MessageSegment.image(res))


@sep_miragetank.handle()
async def get_img_arg(
    state: T_State, args: Message = CommandArg(), bright: List[float] = Numbers()
):
    has_img = any(seg.type == "image" for seg in args)
    if has_img:
        state["miragetank_img_url"] = args

    if bright:
        state["enhance_bright"] = bright[0]
    else:
        state["enhance_bright"] = 3.3


@sep_miragetank.got("miragetank_img_url", "请发送一张幻影坦克图片")
async def sep(state: T_State):
    img_url = [
        seg.data["url"] for seg in state["miragetank_img_url"] if seg.type == "image"
    ]
    if not img_url:
        await sep_miragetank.finish("没有检测到图片，已结束")

    img = await get_img(img_url[0])
    if not img:
        await sep_miragetank.finish("图片下载失败，待会再试吧")

    await sep_miragetank.send("稍等，正在分离")
    outer, inner = seperate(img, bright_factor=state["enhance_bright"])
    await sep_miragetank.finish(
        MessageSegment.image(outer) + MessageSegment.image(inner), at_sender=True
    )
