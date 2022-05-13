import discord
from discord import File
from easy_pil import Editor, load_image_async, Font, load_image, Text
from ruamel.yaml import YAML
import Commands.rank

import KumosLab.Database.get


yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

def translate(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

async def generate(user: discord.Member = None, guild: discord.Guild = None):
    if guild is None:
        print("[Custom] Guild is None")
        return
    if user is None:
        print("[Custom] User is None")
        return
    try:
        xp = await KumosLab.Database.get.xp(user=user, guild=guild)
        level = 1
        next_level_xp = 0

        rank_colour = await KumosLab.Database.get.colour(user=user, guild=guild)

        blur = await KumosLab.Database.get.blur(user=user, guild=guild)

        if config['xp_per_level_type'] == 'default':
            while True:
                if xp < ((config['xp_per_level'] / 2 * (level ** 2)) + (config['xp_per_level'] / 2 * level)):
                    break
                level += 1
            xp -= ((config['xp_per_level'] / 2 * (level - 1) ** 2) + (config['xp_per_level'] / 2 * (level - 1)))

            next_level_xp = int(config['xp_per_level'] * 2 * ((1 / 2) * level))
        
        else:
            previous_total_xp_required = 0
            total_xp_required = 0
            while True:
                previous_total_xp_required = total_xp_required
                total_xp_required += (5 * ((level - 1) ** 2) + (50 * (level - 1)) + 100)
                if xp < total_xp_required:
                    break
                level += 1
            
            xp = xp - previous_total_xp_required
            next_level_xp = int((5 * (level ** 2) + (50 * level) + 100))

        percentage = int((xp / next_level_xp) * 100)

        user_background = await KumosLab.Database.get.background(user=user, guild=guild)
        user_border = await KumosLab.Database.get.border(user=user, guild=guild)

        background_image = load_image(str(user_background))
        background = Editor(background_image).resize((1050, 270)).blur(amount=int(blur))

        user_ranking = await KumosLab.Database.get.rankings(user=user, guild=guild)

        profile_image = load_image(user.avatar_url)
        profile = Editor(profile_image).resize((180, 180)).circle_image()
        border_image = load_image(user_border)
        border = Editor(border_image).resize((190, 190)).circle_image()


        font_25 = Font.poppins(size=35, variant="regular")
        font_60_bold = Font.montserrat(size=44, variant="bold")
        font_40_bold = Font.montserrat(size=38, variant="bold")

        background.paste(border, (30, 35))
        background.paste(profile, (35, 40))

        rankLevelText = list[Text]()

        if config['name_colour'] is True:
            background.text((264, 135), f"{user}", font=font_60_bold, color=rank_colour)
            rankLevelText.append(
                Text(text= f"Rank# {translate(user_ranking)}", font=font_60_bold,
                color="white")
            )
        else:
            background.text((264, 135), f"{user}", font=font_60_bold, color="white")
            rankLevelText.append(
                Text(text= f"Rank# {await KumosLab.Database.get.rankings(user=user, guild=user.guild):,}", font=font_60_bold,
                color="white")
            )
        rankLevelText.append(Text(text="  ", font=font_40_bold, color="white"))
        rankLevelText.append(Text(text=f"Level {level:,}", font=font_60_bold, color=rank_colour))
        background.multicolor_text((990, 35), rankLevelText, align="right")

        background.rectangle((260, 190), width=760, height=40, radius=20, color="#484b4e")
        if percentage > 5:
            background.bar(
                (260, 190),
                max_width=760,
                height=40,
                percentage=percentage,
                fill=rank_colour,
                radius=20,
            )

        background.text(
            (1010, 135), f"{translate(xp)} / {translate(next_level_xp)} XP", font=font_25, color="white", align="right"
        )

        card = File(fp=background.image_bytes, filename="rank_card.png")
        return card

    except Exception as e:
        print(f"[Custom Rank Card] {e}")
        raise e



