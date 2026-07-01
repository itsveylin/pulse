import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

from onboarding import welcome_embed, dm_embed
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

    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    async def save_goal(self, interaction, priority):

        goal = pending_goals.get(self.user_id)

        if not goal:
            await interaction.response.send_message(
                "Goal expired.",
                ephemeral=True
            )
            return

        add_goal(
            self.user_id,
            goal,
            priority
        )

        del pending_goals[self.user_id]

        embed = discord.Embed(
            title="☕ Goal Added",
            description=(
                f"**{goal}**\n"
                f"Priority: {priority.capitalize()}"
            ),
            color=0x2D3A47
        )

        embed.set_footer(
            text="one step at a time."
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

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
        await self.save_goal(
            interaction,
            "high"
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
        await self.save_goal(
            interaction,
            "medium"
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
        await self.save_goal(
            interaction,
            "low"
        )


@bot.event
async def on_member_join(member):

    channel = discord.utils.get(
        member.guild.text_channels,
        name="welcome"
    )

    if channel:
        await channel.send(
            embed=welcome_embed(member)
        )

    try:
        await member.send(
            embed=dm_embed(member)
        )

    except Exception:
        print(
            f"Could not DM {member.name}"
        )


@bot.event
async def on_ready():

    connect_db()

    print(
        f"{bot.user} is online!"
    )


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if bot.user in message.mentions:

        question = message.content.replace(
            f"<@{bot.user.id}>",
            ""
        ).replace(
            f"<@!{bot.user.id}>",
            ""
        ).strip()

        user_id = str(
            message.author.id
        )

        # ADD GOAL
        if question.lower().startswith(
            "add goal"
        ):

            goal = question[8:].strip()

            if not goal:

                await message.author.send(
                    "Please enter a goal."
                )

                return

            pending_goals[user_id] = goal

            await message.author.send(
                "☕ Choose a priority:",
                view=GoalView(user_id)
            )

            return

        # SHOW GOALS
        if question.lower() == "show goals":

            goals = get_goals(
                user_id
            )

            if not goals:

                embed = discord.Embed(
                    title="☕ Your Goals",
                    description="No active goals.",
                    color=0x2D3A47
                )

                await message.author.send(
                    embed=embed
                )

                return

            description = ""

            for _, goal, priority in goals:

                if priority == "high":
                    emoji = "🟥"

                elif priority == "medium":
                    emoji = "🟨"

                else:
                    emoji = "🟩"

                description += (
                    f"{emoji} **{goal}**\n"
                )

            embed = discord.Embed(
                title="☕ Your Goals",
                description=description,
                color=0x2D3A47
            )

            embed.set_footer(
                text="one step at a time."
            )

            await message.author.send(
                embed=embed
            )

            return

        if not question:

            await message.author.send(
                "Hi! Ask me a question."
            )

            return

        try:

            history = get_memory(
                user_id
            )

            answer = await asyncio.to_thread(
                ask_ai,
                question,
                history
            )

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

                    embed = pulse_embed(
                        chunk
                    )

                    await message.author.send(
                        embed=embed
                    )

            else:

                embed = pulse_embed(
                    answer
                )

                await message.author.send(
                    embed=embed
                )

        except Exception as e:

            print(
                f"AI Error: {e}"
            )

            await message.author.send(
                "☕ Pulse is having trouble thinking right now. Please try again."
            )

    await bot.process_commands(
        message
    )


bot.run(TOKEN)