import io
from typing import Tuple, List

import asyncio
import aiohttp
import numpy as np
from PIL import Image, ImageEnhance

np.seterr(divide="ignore", invalid="ignore")


def resize_image(
    im1: Image.Image, im2: Image.Image, mode: str
) -> Tuple[Image.Image, Image.Image]:
    """
    统一图像大小
    """
    im1_w, im1_h = im1.size
    if im1_w * im1_h > 1500 * 2000:
        if im1_w > 1500:
            im1 = im1.resize((1500, int(im1_h * (1500 / im1_w))))
        else:
            im1 = im1.resize((im1_w * (1500 / im1_h), 1500))

    _wimg = im1.convert(mode)
    _bimg = im2.convert(mode).resize(_wimg.size, Image.NEAREST)

    wwidth, wheight = _wimg.size
    bwidth, bheight = _bimg.size

    width = max(wwidth, bwidth)
    height = max(wheight, bheight)

    wimg = Image.new(mode, (width, height), 255)
    bimg = Image.new(mode, (width, height), 0)

    wimg.paste(_wimg, ((width - wwidth) // 2, (height - wheight) // 2))
    bimg.paste(_bimg, ((width - bwidth) // 2, (height - bheight) // 2))

    return wimg, bimg


def gray_car(
    wimg: Image.Image,
    bimg: Image.Image,
    chess: bool = False,
):
    """
    发黑白车
    :param wimg: 白色背景下的图片
    :param bimg: 黑色背景下的图片
    :param wlight: wimg 的亮度
    :param blight: bimg 的亮度
    :param chess: 是否棋盘格化
    :return: 处理后的图像
    """
    wimg, bimg = resize_image(wimg, bimg, "L")

    wpix = np.array(wimg).astype("float64")
    bpix = np.array(bimg).astype("float64")

    # 棋盘格化
    # 规则: if (x + y) % 2 == 0 { wpix[x][y] = 255 } else { bpix[x][y] = 0 }
    if chess:
        wpix[::2, ::2] = 255.0
        bpix[1::2, 1::2] = 0.0

    wpix = wpix * 0.5 + 128
    bpix *= 0.5

    a = 1.0 - wpix / 255.0 + bpix / 255.0
    r = np.where(abs(a) > 1e-6, bpix / a, 255.0)

    pixels = np.dstack((r, r, r, a * 255.0))

    pixels[pixels > 255] = 255

    output = io.BytesIO()
    Image.fromarray(pixels.astype("uint8"), "RGBA").save(output, format="png")
    return output


def color_car(
    wimg: Image.Image,
    bimg: Image.Image,
    wlight: float = 1.0,
    blight: float = 0.18,
    wcolor: float = 0.5,
    bcolor: float = 0.7,
    chess: bool = False,
):
    """
    发彩色车
    :param wimg: 白色背景下的图片
    :param bimg: 黑色背景下的图片
    :param wlight: wimg 的亮度
    :param blight: bimg 的亮度
    :param wcolor: wimg 的色彩保留比例
    :param bcolor: bimg 的色彩保留比例
    :param chess: 是否棋盘格化
    :return: 处理后的图像
    """
    wimg = ImageEnhance.Brightness(wimg).enhance(wlight)
    bimg = ImageEnhance.Brightness(bimg).enhance(blight)

    wimg, bimg = resize_image(wimg, bimg, "RGB")

    wpix = np.array(wimg).astype("float64")
    bpix = np.array(bimg).astype("float64")

    if chess:
        wpix[::2, ::2] = [255.0, 255.0, 255.0]
        bpix[1::2, 1::2] = [0.0, 0.0, 0.0]

    wpix /= 255.0
    bpix /= 255.0

    wgray = wpix[:, :, 0] * 0.334 + wpix[:, :, 1] * 0.333 + wpix[:, :, 2] * 0.333
    wpix *= wcolor
    wpix[:, :, 0] += wgray * (1.0 - wcolor)
    wpix[:, :, 1] += wgray * (1.0 - wcolor)
    wpix[:, :, 2] += wgray * (1.0 - wcolor)

    bgray = bpix[:, :, 0] * 0.334 + bpix[:, :, 1] * 0.333 + bpix[:, :, 2] * 0.333
    bpix *= bcolor
    bpix[:, :, 0] += bgray * (1.0 - bcolor)
    bpix[:, :, 1] += bgray * (1.0 - bcolor)
    bpix[:, :, 2] += bgray * (1.0 - bcolor)

    d = 1.0 - wpix + bpix

    d[:, :, 0] = d[:, :, 1] = d[:, :, 2] = (
        d[:, :, 0] * 0.222 + d[:, :, 1] * 0.707 + d[:, :, 2] * 0.071
    )

    p = np.where(abs(d) > 1e-6, bpix / d * 255.0, 255.0)
    a = d[:, :, 0] * 255.0

    colors = np.zeros((p.shape[0], p.shape[1], 4))
    colors[:, :, :3] = p
    colors[:, :, -1] = a

    colors[colors > 255] = 255

    output = io.BytesIO()
    Image.fromarray(colors.astype("uint8")).convert("RGBA").save(output, format="png")
    return output


async def _download_img(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as r:
        if r.status == 200:
            return Image.open(io.BytesIO(await r.read()))


async def get_imgs(img_urls: List[str]) -> List[Image.Image]:
    if not img_urls:
        return []
    async with aiohttp.ClientSession() as session:
        imgs = await asyncio.gather(*[_download_img(session, url) for url in img_urls])
        return [img for img in imgs if img]


def seperate(img: Image.Image, bright_factor: float = 3.3):
    """
    返回 表图，里图
    """

    black_bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
    black_bg.paste(img, mask=img)
    white_bg.paste(img, mask=img)
    black_bg = ImageEnhance.Brightness(black_bg).enhance(bright_factor)
    out_o = io.BytesIO()
    out_i = io.BytesIO()
    white_bg.convert("RGB").save(out_o, format="jpeg")
    black_bg.convert("RGB").save(out_i, format="jpeg")

    return out_o, out_i


class GenInfo:
    """
    生成图片所需信息
    """

    def __init__(self, mode: str, img_urls: List[str] = []):
        self.mode = mode
        self.img_urls = img_urls

    def valid_mode(self):
        """
        检查合成模式是否合法
        """
        return self.mode in ("gray", "color")

    def enough_img_url(self):
        """
        检查图片数量是否足够
        """
        return len(self.img_urls) >= 2

    def has_img(self):
        return len(self.img_urls) > 0

    def is_ready(self):
        return self.valid_mode() and self.enough_img_url()

    def params_info(self):
        return f"合成模式：{self.mode} (需为 gray | color)\n" f"图片数量：{len(self.img_urls)}/2"
