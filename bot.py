import os
import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

from ai_service import ask_ai

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
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

        # Goal command
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
            answer = ask_ai(question)

            if len(answer) > 1900:
                chunks = [
                    answer[i:i+1900]
                    for i in range(0, len(answer), 1900)
                ]

                for chunk in chunks:
                    await message.author.send(chunk)
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