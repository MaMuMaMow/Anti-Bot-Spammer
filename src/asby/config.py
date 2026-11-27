import traceback
import discord
from db import asbyDb

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def num_input(value: int) -> discord.ui.TextInput:
    """Modals have no number field, so this is a short text box prefilled with the value."""
    return discord.ui.TextInput(default=str(value), max_length=7)

def parse_int(raw: str, name: str, lo: int, hi: int) -> int:
    try:
        n = int(raw.strip())
    except ValueError:
        raise ValueError(f"**{name}** must be a whole number.")
    if not lo <= n <= hi:
        raise ValueError(f"**{name}** must be between {lo} and {hi}.")
    return n


class SafeModal(discord.ui.Modal):
    """Base modal: logs errors and tells the user instead of failing silently."""

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        traceback.print_exception(type(error), error, error.__traceback__)
        msg = "Something went wrong saving your settings."
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


# --------------------------------------------------------------------------
# Modal 1: main settings
# --------------------------------------------------------------------------

class GeneralModal(SafeModal, title="Settings"):
    def __init__(self, guild_id: int, s: dict):
        super().__init__()
        self.guild_id = guild_id
        self.cache = s
        self.s = self.cache[guild_id]
        self.punishment = discord.ui.Select(
            options=[
                discord.SelectOption(label="Ban", value="ban",
                                     default=self.s["punishment"] == "ban"),
                discord.SelectOption(label="Kick", value="kick",
                                     default=self.s["punishment"] == "kick"),
                discord.SelectOption(label="Timeout", value="timeout",
                                     default=self.s["punishment"] == "timeout"),
            ],
        )
        self.timeout_duration = num_input(self.s["timeoutDuration"])
        self.min_rooms = num_input(self.s["minRooms"])
        self.time_gap = num_input(self.s["timeGap"])

        self.add_item(discord.ui.Label(
            text="Punishment",
            description="What to do to the spammer",
            component=self.punishment))
        self.add_item(discord.ui.Label(
            text="Timeout duration",
            description="Seconds (only used when punishment is timeout)",
            component=self.timeout_duration))
        self.add_item(discord.ui.Label(
            text="Min spam rooms",
            description="Minimum number of rooms the spam must appear in",
            component=self.min_rooms))
        self.add_item(discord.ui.Label(
            text="Time gap per message",
            description="Max 50",
            component=self.time_gap))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            data = {
                "punishment": self.punishment.values[0],
                "timeoutDuration": parse_int(self.timeout_duration.value,
                                             "Timeout duration", 60, 2_419_200),
                "minRooms": parse_int(self.min_rooms.value, "Min spam rooms", 1, 10),
                "timeGap": parse_int(self.time_gap.value, "Time gap", 1, 3600),
            }

            for key in data :
                self.cache[self.guild_id][key] = data[key]

        except ValueError as e:
            return await interaction.response.send_message(str(e), ephemeral=True)
        await asbyDb.update_setting(data=data,guildId=interaction.guild.id)
        await interaction.response.send_message("Settings saved.", ephemeral=True)

# --------------------------------------------------------------------------
# Modal 2: advanced settings
# --------------------------------------------------------------------------

class AdvancedModal(SafeModal, title="Advanced settings"):
    def __init__(self, guild_id: int, s: dict):
        super().__init__()
        self.guild_id = guild_id
        self.cache = s
        self.s = self.cache[guild_id]
        
        self.del_amount = num_input(self.s["msgCacheDelAmount"])
        self.del_time = num_input(self.s["msgCacheDelTime"])
        self.cache_duration = num_input(self.s["msgCacheDuration"])
        self.cache_amount = num_input(self.s["msgCacheAmount"])

        self.add_item(discord.ui.Label(
            text="Message delete amount",
            description="Max 50",
            component=self.del_amount))
        self.add_item(discord.ui.Label(
            text="Message delete time",
            description="Seconds, max 1800",
            component=self.del_time))
        self.add_item(discord.ui.Label(
            text="Message caching duration",
            description="Seconds, max 1800",
            component=self.cache_duration))
        self.add_item(discord.ui.Label(
            text="Message caching amount",
            description="Max 50",
            component=self.cache_amount))

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            data = {
                "msgCacheDelAmount": parse_int(self.del_amount.value,
                                               "Message delete amount", 1, 50),
                "msgCacheDelTime": parse_int(self.del_time.value,
                                             "Message delete time", 1, 1800),
                "msgCacheDuration": parse_int(self.cache_duration.value,
                                                "Message caching duration", 1, 1800),
                "msgCacheAmount": parse_int(self.cache_amount.value,
                                              "Message caching amount", 1, 50),
            }
            for key in data :
                self.cache[self.guild_id][key] = data[key]
        except ValueError as e:
            return await interaction.response.send_message(str(e), ephemeral=True)

        # Can't delete more than what was cached.
        if data["msgCacheDelAmount"] > data["msgCacheAmount"]:
            return await interaction.response.send_message(
                "Message delete amount can't be larger than the caching amount.",
                ephemeral=True)
        if data["msgCacheDelTime"] > data["msgCacheDuration"]:
            return await interaction.response.send_message(
                "Message delete time can't be longer than the caching duration.",
                ephemeral=True)

        await asbyDb.update_setting(data=data,guildId=interaction.guild.id)
        await interaction.response.send_message("Advanced settings saved.", ephemeral=True)
        print(self.cache)
# --------------------------------------------------------------------------
# Panel (two buttons, one per modal)
# --------------------------------------------------------------------------

class SettingsPanel(discord.ui.View):
    def __init__(self,setting : dict):
        super().__init__(timeout=300)
        self.setting = setting

    @discord.ui.button(label="Settings", style=discord.ButtonStyle.primary)
    async def general(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GeneralModal(interaction.guild_id, self.setting))

    @discord.ui.button(label="Advanced", style=discord.ButtonStyle.secondary)
    async def advanced(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdvancedModal(interaction.guild_id, self.setting))