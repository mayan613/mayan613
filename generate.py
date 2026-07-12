"""
生成 GitHub Profile 用的 anime 卡片
左侧：assets/ 中随机抽取一张图（居中裁剪成正方形，不变形）
右侧：中文 + emoji 简介文字

使用前必须准备好两个字体文件（PIL 默认字体不支持中文/emoji，这是乱码的根本原因）：
  1. 中文字体（必需）：例如「得意黑 SmileySans」https://github.com/atelier-anchor/smiley-sans
     或「Noto Sans SC」https://fonts.google.com/noto/specimen/Noto+Sans+SC
     下载 .ttf/.otf 后放到 assets/fonts/ 目录，并修改下面 FONT_PATH。

  2. 彩色 emoji 字体（可选，不放的话 emoji 会被自动跳过而不是乱码）：
     推荐「Noto Color Emoji」https://github.com/googlefonts/noto-emoji
     放到 assets/fonts/NotoColorEmoji.ttf，并修改 EMOJI_FONT_PATH。
     需要 Pillow >= 9.2.0（pip install -U pillow）。
"""

from PIL import Image, ImageDraw, ImageFont
import random
import os
import re
import textwrap

# ---------------- 配置区 ----------------

IMAGES = [
    "assets/anime1.png",
    "assets/anime2.png",
    "assets/anime3.png",
    "assets/anime4.png",
    "assets/anime5.png",
]

FONT_PATH = "assets/fonts/SmileySans-Oblique.ttf"        # 中文字体，必需
EMOJI_FONT_PATH = "assets/fonts/NotoColorEmoji.ttf"       # emoji 字体，可选

FONT_TITLE_SIZE = 34
FONT_BODY_SIZE = 24
EMOJI_SIZE = 24  # Noto Color Emoji 是位图字体，部分版本固定尺寸，遇到报错可尝试改成 109

CARD_HEIGHT = 500
IMAGE_SIZE = 500          # 左侧正方形图的边长
TEXT_WIDTH = 700          # 右侧文字区域宽度
CARD_WIDTH = IMAGE_SIZE + TEXT_WIDTH

BG_COLOR = (255, 245, 250)       # 右侧背景色（浅粉）
ACCENT_COLOR = (255, 133, 161)   # 中间分隔条/强调色
TITLE_COLOR = (255, 90, 130)
TEXT_COLOR = (75, 60, 70)

OUTPUT_PATH = "assets/anime-card.png"

RAW_LINES = [
    "🌸 Galeros喵~",
    "🤖 最喜欢鼓捣AI的猫猫开发者喵！",
    "🐧 Linux系统的小忠犬…不对，是小猫咪使用者喵~",
    "🎮 游戏的创世神明喵！",
    "✨ 永远都要努力学习、变强喵~💕",
]

# 匹配大部分常见 emoji 的正则（够用即可，不追求 100% 覆盖）
EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
)

# ---------------- 工具函数 ----------------


def load_font(path, size, required=True):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        if required:
            raise FileNotFoundError(
                f"找不到字体文件：{path}\n"
                "请下载支持中文的字体，放到 assets/fonts/ 下并修改路径。"
            )
        return None


def crop_to_square(img: Image.Image) -> Image.Image:
    """居中裁剪成正方形，避免 resize 导致人物变形"""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def wrap_line(line: str, max_chars: int):
    """按字符数简单换行（中文没有空格分词，用 textwrap 按字数切）"""
    return textwrap.wrap(line, width=max_chars) or [""]


def draw_mixed_text(canvas, draw, xy, text, font, emoji_font, fill):
    """
    逐字符绘制：普通字符用中文字体，emoji 用彩色 emoji 字体。
    如果没有提供可用的 emoji 字体，则直接跳过 emoji（不会乱码）。
    返回绘制后本行的高度。
    """
    x, y = xy
    max_h = 0
    for ch in text:
        if EMOJI_PATTERN.match(ch):
            if emoji_font is not None:
                try:
                    draw.text((x, y), ch, font=emoji_font, embedded_color=True)
                    bbox = draw.textbbox((x, y), ch, font=emoji_font)
                except TypeError:
                    # 旧版本 Pillow 不支持 embedded_color 参数，直接跳过
                    continue
            else:
                continue
        else:
            draw.text((x, y), ch, font=font, fill=fill)
            bbox = draw.textbbox((x, y), ch, font=font)
        x = bbox[2]
        max_h = max(max_h, bbox[3] - bbox[1])
    return max_h if max_h else font.size


# ---------------- 主逻辑 ----------------


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 左侧：随机头像图，居中裁剪成正方形再等比缩放，不变形
    source = random.choice(IMAGES)
    avatar = Image.open(source).convert("RGBA")
    avatar = crop_to_square(avatar)
    avatar = avatar.resize((IMAGE_SIZE, CARD_HEIGHT), Image.LANCZOS)

    # 画布
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), BG_COLOR)
    card.paste(avatar, (0, 0))
    draw = ImageDraw.Draw(card)

    # 中间强调色分隔条
    draw.rectangle([(IMAGE_SIZE, 0), (IMAGE_SIZE + 6, CARD_HEIGHT)], fill=ACCENT_COLOR)

    # 字体
    font_title = load_font(FONT_PATH, FONT_TITLE_SIZE, required=True)
    font_body = load_font(FONT_PATH, FONT_BODY_SIZE, required=True)
    emoji_font = load_font(EMOJI_FONT_PATH, EMOJI_SIZE, required=False)

    # 右侧标题
    pad_x = IMAGE_SIZE + 40
    y = 50
    title_line = RAW_LINES[0]
    line_h = draw_mixed_text(card, draw, (pad_x, y), title_line, font_title, emoji_font, TITLE_COLOR)
    y += line_h + 24

    # 标题下的小分隔线
    draw.line([(pad_x, y), (CARD_WIDTH - 40, y)], fill=ACCENT_COLOR, width=2)
    y += 24

    # 正文，超出宽度自动换行
    max_chars_per_line = 18
    for raw in RAW_LINES[1:]:
        for line in wrap_line(raw, max_chars_per_line):
            line_h = draw_mixed_text(card, draw, (pad_x, y), line, font_body, emoji_font, TEXT_COLOR)
            y += line_h + 14
        y += 6  # 段落间距

    card.convert("RGB").save(OUTPUT_PATH)
    print(f"✅ 已生成：{OUTPUT_PATH}（本次使用的图片：{source}）")


if __name__ == "__main__":
    main()
