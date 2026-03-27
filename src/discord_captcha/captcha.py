from __future__ import annotations

import asyncio
import io
import logging
from dataclasses import dataclass, field
from typing import Awaitable, Callable

import discord
from discord.ext import commands

from .channel import resolve_channel
from .create_captcha import CaptchaImageData, create_captcha

logger = logging.getLogger(__name__)

AsyncCallback = Callable[["CaptchaEventData"], Awaitable[None]]


@dataclass
class CaptchaOptions:
    role_id: int | None = None
    channel_id: int | None = None
    send_to_text_channel: bool = False
    kick_on_failure: bool = True
    case_sensitive: bool = True
    attempts: int = 1
    timeout: float = 60.0
    show_attempt_count: bool = True
    custom_prompt_embed: discord.Embed | None = None
    custom_success_embed: discord.Embed | None = None
    custom_failure_embed: discord.Embed | None = None


@dataclass
class CaptchaEventData:
    member: discord.Member
    captcha_text: str
    captcha_options: CaptchaOptions
    responses: list[str] = field(default_factory=list)
    attempts: int = 0


class Captcha:
    def __init__(
        self,
        bot: commands.Bot,
        options: CaptchaOptions | None = None,
        **kwargs
    ):
        if options is None:
            options = CaptchaOptions(**kwargs)

        if options.send_to_text_channel and not options.channel_id:
            raise ValueError(
                'Option "send_to_text_channel" was set to True, but "channel_id" was not provided.'
            )
        if options.attempts < 1:
            raise ValueError('Option "attempts" must be greater than 0.')
        if options.timeout < 1:
            raise ValueError('Option "timeout" must be greater than 0.')

        self.bot = bot
        self.options = options
        self._listeners: dict[str, list[AsyncCallback]] = {
            "prompt": [],
            "answer": [],
            "success": [],
            "failure": [],
            "timeout": [],
        }

    async def _emit(self, event: str, data: CaptchaEventData) -> None:
        for callback in self._listeners[event]:
            await callback(data)

    def on_prompt(self, func: AsyncCallback) -> AsyncCallback:
        self._listeners["prompt"].append(func)
        return func

    def on_answer(self, func: AsyncCallback) -> AsyncCallback:
        self._listeners["answer"].append(func)
        return func

    def on_success(self, func: AsyncCallback) -> AsyncCallback:
        self._listeners["success"].append(func)
        return func

    def on_failure(self, func: AsyncCallback) -> AsyncCallback:
        self._listeners["failure"].append(func)
        return func

    def on_timeout(self, func: AsyncCallback) -> AsyncCallback:
        self._listeners["timeout"].append(func)
        return func

    async def _send_result(
        self,
        channel: discord.DMChannel | discord.TextChannel,
        captcha_message: discord.Message,
        embed: discord.Embed,
        member: discord.Member,
        kick: bool,
        is_text_channel: bool
    ) -> None:
        if is_text_channel:
            try:
                await captcha_message.delete()
            except discord.HTTPException:
                pass
            result_msg = await channel.send(embed=embed)
            if kick:
                try:
                    await member.kick(reason="Failed to Pass CAPTCHA")
                except discord.Forbidden:
                    logger.warning("Missing permissions to kick %s in guild %s.", member, member.guild.id)
            await _delete_after(result_msg, 3)
        else:
            try:
                await channel.send(embed=embed)
            except discord.HTTPException:
                logger.warning("Failed to send DM result message to %s.", member)
            if kick:
                try:
                    await member.kick(reason="Failed to Pass CAPTCHA")
                except discord.Forbidden:
                    logger.warning("Missing permissions to kick %s in guild %s.", member, member.guild.id)

    async def present(
        self,
        member: discord.Member,
        custom_captcha: CaptchaImageData | None = None
    ) -> bool:
        if custom_captcha:
            if not isinstance(custom_captcha.image, bytes):
                raise ValueError("Custom captcha image must be bytes.")
            if not isinstance(custom_captcha.text, str):
                raise ValueError("Custom captcha text must be a string.")

        captcha_data = custom_captcha or await create_captcha(
            6,
            blacklist="" if self.options.case_sensitive else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        )

        captcha_answer = captcha_data.text if self.options.case_sensitive else captcha_data.text.lower()

        guild_icon = member.guild.icon.url if member.guild.icon else None

        # Build failure embed
        failure_embed = self.options.custom_failure_embed or discord.Embed(
            title="\u274c You Failed to Complete the CAPTCHA!",
            description=f"{member.mention}, you failed to solve the CAPTCHA!\n\nCAPTCHA Text: **{captcha_data.text}**",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        ).set_thumbnail(url=guild_icon)

        # Build success embed
        success_embed = self.options.custom_success_embed or discord.Embed(
            title="\u2705 CAPTCHA Solved!",
            description=f"{member.mention}, you completed the CAPTCHA successfully, and you have been given access to **{member.guild.name}**!",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        ).set_thumbnail(url=guild_icon)

        # Build prompt embed
        prompt_embed = self.options.custom_prompt_embed or discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            color=discord.Color.random()
        ).add_field(
            name="I'm Not a Robot",
            value=f"{member.mention}, to gain access to **{member.guild.name}**, please solve the CAPTCHA below!\n\nThis is done to protect the server from raids consisting of spam bots."
        ).set_thumbnail(url=guild_icon)

        attempts_left = self.options.attempts
        attempts_taken = 0
        captcha_responses: list[str] = []

        if self.options.show_attempt_count:
            if self.options.attempts == 1:
                prompt_embed.set_footer(text="You have one attempt to solve the CAPTCHA.")
            else:
                prompt_embed.set_footer(text=f"Attempts Left: {attempts_left}")

        prompt_embed.set_image(url="attachment://captcha.png")

        # Resolve channel
        channel = await resolve_channel(self.bot, self.options, member)
        is_text_channel = isinstance(channel, discord.TextChannel)

        # Send prompt
        captcha_file = discord.File(io.BytesIO(captcha_data.image), filename="captcha.png")
        captcha_message = await channel.send(embed=prompt_embed, file=captcha_file)

        # Emit prompt event
        await self._emit("prompt", CaptchaEventData(
            member=member,
            captcha_text=captcha_data.text,
            captcha_options=self.options
        ))

        def check(m: discord.Message) -> bool:
            return m.author.id == member.id and m.channel.id == channel.id and not m.author.bot

        while attempts_left > 0:
            attempts_taken += 1

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=self.options.timeout)
            except asyncio.TimeoutError:
                await self._emit("timeout", CaptchaEventData(
                    member=member,
                    captcha_text=captcha_data.text,
                    captcha_options=self.options,
                    responses=captcha_responses,
                    attempts=attempts_taken
                ))

                await self._send_result(channel, captcha_message, failure_embed, member, self.options.kick_on_failure, is_text_channel)
                return False

            answer = msg.content
            captcha_responses.append(answer)

            await self._emit("answer", CaptchaEventData(
                member=member,
                captcha_text=captcha_data.text,
                captcha_options=self.options,
                responses=captcha_responses,
                attempts=attempts_taken
            ))

            compare = answer.lower() if not self.options.case_sensitive else answer

            if is_text_channel:
                try:
                    await msg.delete()
                except discord.HTTPException:
                    pass

            if compare == captcha_answer:
                await self._emit("success", CaptchaEventData(
                    member=member,
                    captcha_text=captcha_data.text,
                    captcha_options=self.options,
                    responses=captcha_responses,
                    attempts=attempts_taken
                ))

                if self.options.role_id:
                    role = member.guild.get_role(self.options.role_id)
                    if role:
                        try:
                            await member.add_roles(role)
                        except discord.Forbidden:
                            logger.warning("Missing permissions to assign role %s to %s in guild %s.", role.id, member, member.guild.id)
                    else:
                        logger.warning("Role %s not found in guild %s - captcha passed but role not assigned.", self.options.role_id, member.guild.id)

                await self._send_result(channel, captcha_message, success_embed, member, False, is_text_channel)
                return True
            else:
                attempts_left -= 1
                if attempts_left > 0:
                    if self.options.show_attempt_count:
                        prompt_embed.set_footer(text=f"Attempts Left: {attempts_left}")

                    if is_text_channel:
                        captcha_file = discord.File(io.BytesIO(captcha_data.image), filename="captcha.png")
                        await captcha_message.edit(embed=prompt_embed, attachments=[captcha_file])
                    else:
                        try:
                            captcha_file = discord.File(io.BytesIO(captcha_data.image), filename="captcha.png")
                            await channel.send(embed=prompt_embed, file=captcha_file)
                        except discord.HTTPException:
                            logger.warning("Failed to send DM attempt prompt to %s.", member)
                    continue

        # All attempts exhausted
        await self._emit("failure", CaptchaEventData(
            member=member,
            captcha_text=captcha_data.text,
            captcha_options=self.options,
            responses=captcha_responses,
            attempts=attempts_taken
        ))

        await self._send_result(channel, captcha_message, failure_embed, member, self.options.kick_on_failure, is_text_channel)
        return False


async def _delete_after(message: discord.Message, delay: float) -> None:
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except discord.HTTPException:
        pass
