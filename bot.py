import os
import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

from ai_service import ask_ai
from memory_service import add_message, get_memory
from embeded import pulse_embed
from database import connect_db
from goals import add_goal, get_goals

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

pending_goals = {}


class GoalView(View):

    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(
        label="High",
        style=discord.ButtonStyle.danger,
        emoji="🟥"
    )
    async def high(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await interaction.response.send_message(
            "High priority selected.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Medium",
        style=discord.ButtonStyle.secondary,
        emoji="🟨"
    )
    async def medium(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await interaction.response.send_message(
            "Medium priority selected.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Low",
        style=discord.ButtonStyle.success,
        emoji="🟩"
    )
    async def low(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await interaction.response.send_message(
            "Low priority selected.",
            ephemeral=True
        )


@bot.event
async def on_ready():
    connect_db()
    print(f"{bot.user} is online!")


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if bot.user in message.mentions:

        question = message.content.replace(
            f"<@{bot.user.id}>", ""
        ).replace(
            f"<@!{bot.user.id}>", ""
        ).strip()

        if question.lower().startswith("add goal"):

            goal = question[8:].strip()

            pending_goals[
                str(message.author.id)
            ] = goal

            await message.author.send(
                "☕ Choose a priority for your goal.",
                view=GoalView()
            )

            return

        if not question:
            await message.author.send(
                "Hi! Ask me a question."
            )
            return

        try:
            user_id = str(message.author.id)

            history = get_memory(user_id)

            answer = ask_ai(question, history)

            add_message(
                user_id,
                "user",
                question
            )

            add_message(
                user_id,
                "assistant",
                answer
            )

            if len(answer) > 3500:

                chunks = [
                    answer[i:i + 3500]
                    for i in range(
                        0,
                        len(answer),
                        3500
                    )
                ]

                for chunk in chunks:
                    embed = pulse_embed(chunk)
                    await message.author.send(
                        embed=embed
                    )

            else:
                embed = pulse_embed(answer)
                await message.author.send(
                    embed=embed
                )

        except Exception as e:
            print(f"Error: {e}")

            await message.author.send(
                "Sorry, something went wrong."
            )

    await bot.process_commands(message)


bot.run(TOKEN)