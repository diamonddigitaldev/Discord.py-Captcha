from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from .captcha import CaptchaOptions

from .errors import CaptchaError

logger = logging.getLogger(__name__)


async def resolve_channel(
    bot: discord.Client,
    options: CaptchaOptions,
    member: discord.Member
) -> discord.DMChannel | discord.TextChannel:
    if options.send_to_text_channel and options.channel_id:
        channel = member.guild.get_channel(options.channel_id) or await bot.fetch_channel(options.channel_id)
        return channel

    try:
        return await member.create_dm()
    except discord.HTTPException:
        logger.warning("Failed to send CAPTCHA via DM to %s.", member)
        if options.channel_id:
            channel = member.guild.get_channel(options.channel_id) or await bot.fetch_channel(options.channel_id)
            return channel
        raise CaptchaError("Cannot send captcha: user's DMs are locked and no fallback channel_id was provided.")
