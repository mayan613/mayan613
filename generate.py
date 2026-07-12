from PIL import Image, ImageDraw, ImageFont
import random
import os


images = [
    "assets/anime1.png",
    "assets/anime2.png",
    "assets/anime3.png",
    "assets/anime4.png",
    "assets/anime5.png"
]


source = random.choice(images)


img = Image.open(source)

img = img.resize((500,500))


draw = ImageDraw.Draw(img)


text = """
🌸 Galeros喵~

🤖 最喜欢鼓捣AI的猫猫开发者喵！
🐧 Linux系统的小忠犬…不对，是小猫咪使用者喵~
🎮 游戏的创世神明喵！
✨ 永远都要努力学习、变强喵~💕
"""


draw.text(
    (20,20),
    text,
    fill=(255,255,255)
)


img.save(
    "assets/anime-card.png"
)
