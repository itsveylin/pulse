import discord


def welcome_embed(member):

    embed = discord.Embed(
        title="☕ Welcome to Aurora",
        description=(
            f"Hello {member.mention},\n\n"
            "Welcome to our little study corner.\n"
            "I'm **Pulse**, your study companion."
        ),
        color=0x2D3A47
    )

    embed.add_field(
        name="📚 Start Here",
        value=(
            "• Read the rules\n"
            "• Introduce yourself\n"
            "• Explore study channels"
        ),
        inline=False
    )

    embed.add_field(
        name="☕ Pulse Can Help With",
        value=(
            "• Study questions\n"
            "• Goal tracking\n"
            "• Productivity support\n"
            "• Learning guidance"
        ),
        inline=False
    )

    embed.set_footer(
        text="one step at a time."
    )

    return embed


def dm_embed(member):

    embed = discord.Embed(
        title="☕ Welcome to Catalyst",
        description=(
            f"Hi {member.name}.\n\n"
            "I'm Pulse, your study companion.\n"
            "You can mention me anytime to:\n\n"
            "📚 Ask questions\n"
            "🎯 Manage goals\n"
            "💭 Get study help\n"
            "☕ Stay accountable"
        ),
        color=0x2D3A47
    )

    embed.set_footer(
        text="small steps count."
    )

    return embed