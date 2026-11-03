
import os
import asyncio
import discord

from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

from onboarding import welcome_embed, dm_embed
from ai_service import analyze_message
from memory_service import add_message, get_memory
from embeded import pulse_embed
from database import connect_db
from goals import add_goal, get_goals


# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN is missing from your .env file")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

pending_goals = {}


# ==========================================
# GOAL PRIORITY VIEW
# ==========================================

class GoalView(View):

    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = str(user_id)

    async def save_goal(self, interaction, priority):

        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "This goal selection does not belong to you.",
                ephemeral=True
            )
            return

        goal_data = pending_goals.get(self.user_id)

        if not goal_data:
            await interaction.response.send_message(
                "Goal expired.",
                ephemeral=True
            )
            return

        add_goal(
            self.user_id,
            goal_data["goal"],
            priority,
            deadline=goal_data.get("deadline"),
            goal_type=goal_data.get("goal_type", "general")
        )

        del pending_goals[self.user_id]

        embed = discord.Embed(
            title="☕ Goal Added",
            description=(
                f"**{goal_data['goal']}**\n"
                f"Priority: {priority.capitalize()}\n"
                f"Type: {goal_data.get('goal_type', 'general').capitalize()}"
            ),
            color=0x2D3A47
        )

        if goal_data.get("deadline"):
            embed.add_field(
                name="Deadline",
                value=goal_data["deadline"],
                inline=False
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
    async def high(self, interaction, button):
        await self.save_goal(interaction, "high")

    @discord.ui.button(
        label="Medium",
        style=discord.ButtonStyle.secondary,
        emoji="🟨"
    )
    async def medium(self, interaction, button):
        await self.save_goal(interaction, "medium")

    @discord.ui.button(
        label="Low",
        style=discord.ButtonStyle.success,
        emoji="🟩"
    )
    async def low(self, interaction, button):
        await self.save_goal(interaction, "low")


# ==========================================
# AMBIGUOUS GOAL CONFIRMATION
# ==========================================

class GoalConfirmationView(View):

    def __init__(self, user_id, goal_data):
        super().__init__(timeout=300)

        self.user_id = str(user_id)
        self.goal_data = goal_data

    @discord.ui.button(
        label="Confirm Goal",
        style=discord.ButtonStyle.success,
        emoji="☑️"
    )
    async def confirm(self, interaction, button):

        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "This confirmation does not belong to you.",
                ephemeral=True
            )
            return

        goal_data = pending_goals.get(self.user_id)

        if not goal_data:
            await interaction.response.send_message(
                "This goal confirmation has expired.",
                ephemeral=True
            )
            return

        add_goal(
            self.user_id,
            goal_data["goal"],
            "medium",
            deadline=goal_data.get("deadline"),
            goal_type=goal_data.get("goal_type", "general")
        )

        del pending_goals[self.user_id]

        embed = discord.Embed(
            title="☕ Goal Saved",
            description=(
                f"**{goal_data['goal']}**\n"
                "Priority: Medium"
            ),
            color=0x2D3A47
        )

        if goal_data.get("deadline"):
            embed.add_field(
                name="Deadline",
                value=goal_data["deadline"],
                inline=False
            )

        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.secondary,
        emoji="✖️"
    )
    async def cancel(self, interaction, button):

        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "This confirmation does not belong to you.",
                ephemeral=True
            )
            return

        pending_goals.pop(self.user_id, None)

        await interaction.response.edit_message(
            content="Goal discarded. Nothing was saved.",
            embed=None,
            view=None
        )


# ==========================================
# MEMBER JOIN EVENT
# ==========================================

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

    except discord.Forbidden:
        print(f"Could not DM {member.name}")


# ==========================================
# BOT READY EVENT
# ==========================================

@bot.event
async def on_ready():

    connect_db()

    print(f"{bot.user} is online!")
    print("Pulse is ready to help students.")


# ==========================================
# MESSAGE HANDLER
# ==========================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    is_dm = isinstance(
        message.channel,
        discord.DMChannel
    )

    should_respond = (
        is_dm
        or (
            not is_dm
            and bot.user in message.mentions
        )
    )

    if should_respond:

        question = message.content.replace(
            f"<@{bot.user.id}>",
            ""
        ).replace(
            f"<@!{bot.user.id}>",
            ""
        ).strip()

        user_id = str(message.author.id)

        # ----------------------------------
        # MANUAL ADD GOAL
        # ----------------------------------

        if question.lower().startswith("add goal"):

            goal = question[8:].strip()

            if not goal:
                await message.author.send(
                    "Please enter a goal."
                )
                return

            pending_goals[user_id] = {
                "goal": goal,
                "deadline": None,
                "goal_type": "general"
            }

            await message.author.send(
                "☕ Choose a priority:",
                view=GoalView(user_id)
            )

            return

        # ----------------------------------
        # SHOW GOALS
        # ----------------------------------

        if question.lower() == "show goals":

            goals = get_goals(user_id)

            if not goals:

                embed = discord.Embed(
                    title="☕ Your Goals",
                    description="No active goals.",
                    color=0x2D3A47
                )

            else:

                description = ""

                for _, goal, priority in goals:

                    if priority == "high":
                        emoji = "🟥"
                    elif priority == "medium":
                        emoji = "🟨"
                    else:
                        emoji = "🟩"

                    description += f"{emoji} **{goal}**\n"

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

        # ----------------------------------
        # EMPTY MESSAGE
        # ----------------------------------

        if not question:

            await message.author.send(
                "Hi! Ask me a question."
            )

            return

        # ----------------------------------
        # GROQ AI + SQLITE MEMORY
        # ----------------------------------

        try:

            history = get_memory(user_id)

            async with message.channel.typing():

                result = await asyncio.to_thread(
                    analyze_message,
                    question,
                    history
                )

            answer = result["response"]
            goal_data = result["goal_detection"]

            # ----------------------------------
            # EXPLICIT GOAL: SAVE AUTOMATICALLY
            # ----------------------------------

            if goal_data["intent"] == "explicit":

                goal = goal_data["goal"]

                add_goal(
                    user_id,
                    goal,
                    "medium",
                    deadline=goal_data.get("deadline"),
                    goal_type=goal_data.get("goal_type", "general")
                )

                answer += (
                    "\n\n☕ **Goal saved automatically.**\n"
                    f"**Goal:** {goal}\n"
                    "**Priority:** Medium"
                )

                if goal_data.get("deadline"):
                    answer += (
                        f"\n**Deadline:** {goal_data['deadline']}"
                    )

            # ----------------------------------
            # AMBIGUOUS GOAL: ASK FOR CONFIRMATION
            # ----------------------------------

            elif goal_data["intent"] == "ambiguous":

                goal = goal_data["goal"]

                pending_goals[user_id] = {
                    "goal": goal,
                    "deadline": goal_data.get("deadline"),
                    "goal_type": goal_data.get("goal_type", "general")
                }

                answer += (
                    "\n\n☕ **Is this something you'd like "
                    "me to track as a goal?**\n"
                    f"**Suggested goal:** {goal}\n"
                    "It will be saved with medium priority "
                    "if you confirm."
                )

            # ----------------------------------
            # SAVE CONVERSATION MEMORY
            # ----------------------------------

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

            # ----------------------------------
            # SEND RESPONSE
            # ----------------------------------

            chunks = [
                answer[i:i + 3500]
                for i in range(0, len(answer), 3500)
            ]

            for index, chunk in enumerate(chunks):

                embed = pulse_embed(chunk)

                view = None

                if (
                    index == len(chunks) - 1
                    and goal_data["intent"] == "ambiguous"
                ):
                    view = GoalConfirmationView(
                        user_id,
                        goal_data
                    )

                if is_dm:

                    await message.channel.send(
                        embed=embed,
                        view=view
                    )

                else:

                    await message.author.send(
                        embed=embed,
                        view=view
                    )

        except discord.Forbidden:

            print(
                f"Cannot send DM to {message.author}"
            )

        except Exception as e:

            print(f"AI Error: {e}")

            try:
                await message.author.send(
                    "☕ Pulse is having trouble thinking right now. Please try again."
                )

            except discord.Forbidden:
                print(
                    f"Could not notify {message.author}"
                )

    # ----------------------------------
    # COMMAND PROCESSING
    # ----------------------------------

    await bot.process_commands(message)


# ==========================================
# START BOT
# ==========================================

bot.run(TOKEN)
