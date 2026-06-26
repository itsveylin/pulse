import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from ai_service import ask_ai
from memory_service import add_message, get_memory
from embeded import pulse_embed

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

        if not question:
            await message.author.send(
                "Hi! Ask me a question."
            )
            return

        try:
            user_id = str(message.author.id)

            # Get previous memory
            history = get_memory(user_id)

            # Get AI response
            answer = ask_ai(question, history)

            # Store memory
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

            # Send answer as embed
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