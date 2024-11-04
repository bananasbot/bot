from os.path import join
import logging
import discord.ui

import config


class PreferencesEmbed(discord.Embed):
    def __init__(self):
        super().__init__(
            title="Preferences",
            description="""The attachment above contains your current preferences and raid configuration. 
            Import it on the scheduler to edit your preferences, then upload its exported version.""",
        )
        # self.set_footer(icon_url="")  # add bananas url

        self.add_field(name="", value="")  # spacer
        self.add_field(
            name="First",
            value="`Download` the attachment and click on `🗓️ Open Scheduler`",
            inline=False,
        )
        self.add_field(name="", value="")  # spacer
        self.add_field(
            name="Then",
            value="`Import` the attachment into the Scheduler and edit your preferences",
            inline=False,
        )
        self.add_field(name="", value="")  # spacer
        self.add_field(
            name="Finally",
            value="`Copy to Clipboard` your preferences and click on `✅ Upload Preferences`",
            inline=False,
        )


class PreferencesButtons(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)

        self.add_item(
            discord.ui.Button(
                url="https://bananasbot.github.io/",
                label="Open Scheduler",
                emoji="🗓️",
            )
        )

    @discord.ui.button(
        label="Upload Preferences", style=discord.ButtonStyle.blurple, emoji="✅"
    )
    async def upload(self, interaction: discord.Interaction, button: discord.ui.Button):
        logging.getLogger(PreferencesButtons.__name__).info(
            f"{interaction.user.id} ({interaction.user.name})"
        )
        await interaction.response.send_modal(UploadModal())


class UploadModal(discord.ui.Modal, title="Upload Preferences"):
    upload = discord.ui.TextInput(
        label="Paste here your preferences",
        style=discord.TextStyle.long,
        placeholder='{ "timezone": "...',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        logging.getLogger(UploadModal.__name__).info(
            f"{interaction.user.id} ({interaction.user.name})"
        )

        dest = join(config.playersPath, f"{interaction.user.id}.json")
        with open(dest, "w") as text_file:
            text_file.write(self.upload.value)

        await interaction.response.send_message(
            "Preferences updated!",
            ephemeral=True,
        )
        await interaction.response.edit_message(
            content=None,
            embed=None,
            view=None,
            attachments=[],
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(
            f"Oops! Something went wrong. {error}", ephemeral=True
        )
        raise error


__logger = logging.getLogger("preferencesUx")
