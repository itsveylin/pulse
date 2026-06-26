import discord
import random

quotes = [
    "☾ one page at a time.",
    "☾ rest is productive too.",
    "☾ small steps count.",
    "☾ today's effort matters.",
    "☾ progress is still progress."
]

def pulse_embed(answer):

    embed = discord.Embed(
        title="☕ a note from Pulse",
        description=answer,
        color=0x2D3A47
    )

    embed.set_footer(
        text=random.choice(quotes)
    )

    return embed