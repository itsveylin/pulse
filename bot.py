import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from ai_service import ask_ai
from memory_service import add_message, get_memory

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

            # Get previous conversation history
            history = get_memory(user_id)

            # Get AI response
            answer = ask_ai(question, history)

            # Store conversation
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

            # Split long responses
            if len(answer) > 1900:

                chunks = [
                    answer[i:i + 1900]
                    for i in range(0, len(answer), 1900)
                ]

                for chunk in chunks:
                    await message.author.send(chunk)

            else:
                await message.author.send(answer)

        except Exception as e:
            print(f"Error: {e}")

            await message.author.send(
                "Sorry, I encountered an error while processing your request."
            )

    await bot.process_commands(message)


bot.run(TOKEN)