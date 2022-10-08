<div align="center">

# 合成幻影坦克图

</div>

<p align="center">
  
  <a href="https://github.com/RafuiiChan/nonebot_plugin_miragetank/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-GPL-informational">
  </a>
  
  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot2-2.0.0beta.1-green">
  </a>
  
  <a href="">
    <img src="https://img.shields.io/badge/release-v0.0.1-orange">
  </a>
  
</p>
</p>

## 版本

v0.0.4  - 修复了参数获取的 bug ， ~~有没有新bug就不知道了~~

### ⚠ 适配nonebot2-2.0.0beta版本；（rc版本需要更改部分内容，下面说）

## 安装

1. 通过`pip`或`nb`安装；

命令

`pip install nonebot_plugin_miragetank`

`nb plugin install nonebot_plugin_miragetank`

## 功能

生成幻影坦克图（在黑白背景下显示不同的图）

## 命令

`生成幻影坦克` / `miragetank`

⚠ 需要 nonebot2 配置的命令前缀，如果没配置默认 `/` ,即发送`/miragetank`可触发

### 需要参数：
合成模式: `gray`或`color` （后者合成的里图是彩色的）

至少两张图片

可随时取消命令

## 版本适配问题
beta2 及以上可以更改如下内容

`from nonebot.params import CommandArg, State` 改为 `from nonebot.params import CommandArg`

`state: T_State = State()` 改为 `state: T_State` （所有地方都要改，可以使用全文替换来做）

其他问题可提 issue

## 致谢
插件核心算法来自 [MirageTankGO](https://github.com/Aloxaf/MirageTankGo)
