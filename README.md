<div align="center">

# 合成幻影坦克图

</div>

<p align="center">
  
  <a href="https://github.com/RafuiiChan/nonebot_plugin_miragetank/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-GPL-informational">
  </a>
  
  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot2-2.0.0rc1-green">
  </a>
  
  <a href="">
    <img src="https://img.shields.io/badge/release-v0.1.2-orange">
  </a>
  
</p>
</p>

## 版本

v0.1.2  - 可指定分离时的里图的亮度增强值

v0.1.0  - 增加分离幻影坦克功能

v0.0.5  - 适配了 rc 版本



## 安装

1. 通过`pip`或`nb`安装；

命令

`pip install nonebot_plugin_miragetank`

`nb plugin install nonebot_plugin_miragetank`

## 功能

生成幻影坦克图（在黑白背景下显示不同的图） 与 分离幻影坦克图（不过效果感觉不是很好，最好用来分离本插件合成的图，否则效果可能更差）
![image](./img/test1.png)

![image](./img/test2.png)


## 命令

`幻影坦克` / `miragetank`

`分离幻影坦克`

⚠ 需要 nonebot2 配置的命令前缀，如果没配置默认 `/` ,即发送`/miragetank`可触发

### 合成图片需要参数：
合成模式: `gray`或`color` （后者合成的里图是彩色的）

至少两张图片

可随时取消命令

### 分离图片需要参数：
一张幻影坦克图片

可选参数：需要增强的亮度，取值建议 1~6，值越大分离出的里图（即黑底状态下的图片）的亮度越高，默认是 3.3 

## 示例（不包含交互过程）
`/合成幻影坦克 color [图片1] [图片2]`

`/合成幻影坦克 [图片1] [图片2]`

`/合成幻影坦克 gray`

`/分离幻影坦克 [图片]`

`/分离幻影坦克 [图片] 5.5`

`/分离幻影坦克 [图片] 3.3`

`/分离幻影坦克 4.9`


## 致谢
幻影坦克合成算法来自 [MirageTankGO](https://github.com/Aloxaf/MirageTankGo)
