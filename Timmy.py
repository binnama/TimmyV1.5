import asyncio
import time
import random
import heapq
import re
import os
from typing import Final

from dotenv import load_dotenv
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix="!", intents=intents)


class War:
    def __init__(self, name, message, war_duration, wait_duration, repetitions):
        self.name = name
        self.user = message.author
        self.war_duration = war_duration
        self.wait_duration = wait_duration
        self.repetitions = int(repetitions)
        self.message = message
        self.start_time = time.time() + wait_duration
        if is_role(self.message.author, ["No-Countdown"]):
            self.mention_author = False
        else:
            self.mention_author = True

    def __str__(self, link=True):
        string = f"War: {self.name.strip()}. "

        if self.start_time > time.time():
            converted_time = convert_time_difference_to_str(
                self.start_time - time.time()
            )
            string += f"Starting in {converted_time}. "
        else:
            end_time = self.start_time + self.war_duration
            converted_time = convert_time_difference_to_str(end_time - time.time())
            string += f"{converted_time} remaining. "

        if self.repetitions > 1:
            string += f"{self.repetitions} more wars remaining"

        if link:
            string += self.message.jump_url

        return string

    async def countdown(self):
        if self.wait_duration == 0:
            await post_message(self.message, f"War: {self.name} is starting NOW")

        else:
            await post_message(
                self.message,
                f"War: {self.name} is starting in "
                f"{convert_time_difference_to_str(self.wait_duration)}",
            )
            if self.wait_duration >= 0.5 * minute_length:
                delay_countdown = minute_length / 2
                await asyncio.sleep(self.wait_duration - delay_countdown)
                if self.in_war():
                    user_mentions = await self.get_reactions_as_mentions(False)
                    await post_message(
                        self.message,
                        f"War: {self.name} starts in "
                        f"{convert_time_difference_to_str(delay_countdown)}. "
                        f"Get ready! {user_mentions}",
                        reply=True,
                        mention=True,
                    )
                    await asyncio.sleep(delay_countdown)
            elif (
                self.wait_duration < 0.5 * minute_length and not self.wait_duration == 0
            ):
                await asyncio.sleep(self.wait_duration)

        if self.in_war():
            await self.run_war()

    async def run_war(self):
        user_mentions = await self.get_reactions_as_mentions(False)
        await post_message(
            self.message,
            f"Start! War: {self.name} is on for "
            f"{convert_time_difference_to_str(self.war_duration)}. "
            f"{user_mentions}",
            mention=True,
        )

        remaining_duration = self.war_duration

        for interval in war_len_intervals:
            if not self.in_war():
                return
            if remaining_duration <= minute_length:
                await asyncio.sleep(remaining_duration)
                break
            if remaining_duration > interval:
                diff = remaining_duration - interval
                await asyncio.sleep(diff)
                if not self.in_war():
                    return
                remaining_duration = interval
                user_mentions = await self.get_reactions_as_mentions(True)
                await post_message(
                    self.message,
                    f"War: {self.name} has "
                    f"{convert_time_difference_to_str(remaining_duration)} "
                    f"remaining. {user_mentions}",
                    mention=self.mention_author,
                )

        # Denne her kan kanskje bli skrevet bedre
        if self.in_war():
            user_mentions = await self.get_reactions_as_mentions(False)
            await post_message(
                self.message,
                f"War: {self.name} has ended! {user_mentions}",
                tts=True,
                mention=True,
            )

            if self.repetitions > 1:
                self.repetitions -= 1
                self.start_time = time.time() + self.wait_duration
                if self.repetitions > 1:
                    await post_message(
                        self.message, f"{self.repetitions} more wars remaining"
                    )
                else:
                    await post_message(self.message, "One more war remaining")
                await self.countdown()
            else:
                wars.pop(self.name.lower())

    async def get_reactions_as_mentions(self, no_countdown):
        user_mention = ""
        for r in self.message.reactions:
            async for user in r.users():
                if no_countdown and is_role(user, ["No-Countdown"]):
                    continue
                if user.bot:
                    continue
                user_mention += " " + str(user.mention)
        return user_mention

    def in_war(self):
        if self.name.lower() in wars:
            if wars[self.name.lower()] == self:
                return True
        return False

class Timer:
    def __init__(self, name, message, timer_duration, wait_duration, repetitions):
        self.name = name
        self.user = message.author
        self.timer_duration = timer_duration
        self.wait_duration = wait_duration
        self.repetitions = int(repetitions)
        self.message = message
        self.start_time = time.time() + wait_duration
        self.mention_author = True

    def __str__(self, link=True):
        string = f"Timer: {self.name.strip()}. "

        if self.start_time > time.time():
            converted_time = convert_time_difference_to_str(
                self.start_time - time.time()
            )
            string += f"Starting in {converted_time}. "
        else:
            end_time = self.start_time + self.timer_duration
            converted_time = convert_time_difference_to_str(end_time - time.time())
            string += f"{converted_time} remaining. "

        if self.repetitions > 1:
            string += f"{self.repetitions} more timers remaining"

        if link:
            string += self.message.jump_url

        return string

    async def countdown(self):
        if self.wait_duration == 0:
            await post_message(self.message, f"Timer: {self.name} is starting NOW")

        else:
            await post_message(
                self.message,
                f"Timer: {self.name} is starting in "
                f"{convert_time_difference_to_str(self.wait_duration)}",
            )
            if self.wait_duration >= 0.5 * minute_length:
                delay_countdown = minute_length / 2
                await asyncio.sleep(self.wait_duration - delay_countdown)
                if self.in_timer():
                    user_mentions = await self.get_reactions_as_mentions(False)
                    await post_message(
                        self.message,
                        f"Timer: {self.name} starts in "
                        f"{convert_time_difference_to_str(delay_countdown)}. "
                        f"Get ready! {user_mentions}",
                        reply=True,
                        mention=True,
                    )
                    await asyncio.sleep(delay_countdown)
            elif (
                self.wait_duration < 0.5 * minute_length and not self.wait_duration == 0
            ):
                await asyncio.sleep(self.wait_duration)

        if self.in_timer():
            await self.run_timer()

    async def run_timer(self):
        user_mentions = await self.get_reactions_as_mentions(False)
        await post_message(
            self.message,
            f"Timer: {self.name} is on for "
            f"{convert_time_difference_to_str(self.timer_duration)}. "
            f"{user_mentions}",
            mention=True,
        )

        remaining_duration = self.timer_duration
        for interval in timer_intervals:
            if not self.in_timer():
                return
            if remaining_duration <= minute_length:
                await asyncio.sleep(remaining_duration)
                break
            if remaining_duration > interval:
                diff = remaining_duration - interval
                await asyncio.sleep(diff)
                if not self.in_timer():
                    return
                remaining_duration = interval


        # Denne her kan kanskje bli skrevet bedre
        if self.in_timer():
            user_mentions = await self.get_reactions_as_mentions(False)
            await post_message(
                self.message,
                f"Timer: {self.name} has ended! {user_mentions}",
                tts=True,
                mention=True,
            )

            if self.repetitions > 1:
                self.repetitions -= 1
                self.start_time = time.time() + self.wait_duration
                if self.repetitions > 1:
                    await post_message(
                        self.message, f"{self.repetitions} more timers remaining"
                    )
                else:
                    await post_message(self.message, "One more timer remaining")
                await self.countdown()
            else:
                timers.pop(self.name.lower())

    async def get_reactions_as_mentions(self, no_countdown):
        user_mention = ""
        for r in self.message.reactions:
            async for user in r.users():
                if no_countdown and is_role(user, ["No-Countdown"]):
                    continue
                if user.bot:
                    continue
                user_mention += " " + str(user.mention)
        return user_mention

    def in_timer(self):
        if self.name.lower() in timers:
            if timers[self.name.lower()] == self:
                return True
        return False



class Event:
    def __init__(self, name, message, tts):
        self.name = name
        self.message = message
        self.events = []
        heapq.heapify(self.events)
        self.current = []
        self.tts = tts

    def __contains__(self, item):
        if item in self.events or item in self.current:
            return True
        return False

    def __str__(self):
        msg = ""
        for event in self.current:
            msg += f"Event: {self.name} in {convert_time_difference_to_str(event - time.time())} \n"
        for event in self.events:
            msg += f"Event: {self.name} in {convert_time_difference_to_str(event - time.time())} \n"
        return msg

    def push(self, item):
        heapq.heappush(self.events, item)

    async def run_event(self):
        while len(self.events) > 0 and events[self.name] == self:
            event_time = heapq.heappop(self.events)
            self.current.append(event_time)
            wait = event_time - time.time()
            await asyncio.sleep(wait)
            self.current.remove(event_time)
            await post_message(self.message, self.name, self.tts, False)


class Spam:
    def __init__(self, message, spam, frequency):
        self.message = message
        self.spam = spam
        self.frequency = frequency

    def __str__(self):
        return (
            f"Spam: {self.spam} every {convert_time_difference_to_str(self.frequency)}"
        )

    async def run(self):
        while self.spam in spam_dict:
            await post_message(self.message, self.spam)
            await asyncio.sleep(self.frequency)


class Session:
    def __init__(self, name, message, in_list):
        self.name = name
        self.user = message.author
        self.message = message
        self.duration = in_list[0]
        self.difficulty = in_list[1]
        self.max_war = in_list[2]
        self.min_war = in_list[3]
        self.max_wait = in_list[4]
        self.min_wait = in_list[5]

    def __str__(self):
        if self.duration > self.min_war:
            return (
                f"Session: {self.name} with {convert_time_difference_to_str(self.duration * minute_length)} "
                f"remaining"
            )
        else:
            return f"Session: {self.name} finishing up last war"

    async def run(self):
        while self.duration > 0 and self.name.lower() in sessions:
            if self.duration < (self.max_war + self.max_wait):
                if self.duration > self.max_war:
                    war_duration = random.randint(self.min_war, self.max_war)
                    self.duration -= war_duration
                    if self.duration > self.max_wait:
                        wait_duration = random.randint(self.min_wait, self.max_wait)
                    elif self.duration > self.min_wait:
                        wait_duration = random.randint(self.min_wait, self.duration)
                    else:
                        wait_duration = 1
                        self.duration = 0
                else:
                    war_duration = self.duration
                    wait_duration = 1
                    self.duration = 0
            else:
                war_duration = random.randint(self.min_war, self.max_war)
                self.duration -= war_duration
                wait_duration = random.randint(self.min_wait, self.max_wait)
                self.duration -= wait_duration

            if self.difficulty > 0:
                name = int(
                    war_duration
                    * (10 + random.randint(0, self.difficulty) / 2)
                    * random.randint(1, self.difficulty)
                )
            else:
                name = get_prompt()
            await post_message(
                self.message,
                f"!startwar {war_duration} {wait_duration} {name}",
                reply=False,
            )
            await asyncio.sleep((war_duration + wait_duration + 0.1) * minute_length)

        if self.name in sessions:
            sessions.pop(self.name)


class Reminder:
    def __init__(self, reminder, message, wait):
        self.reminder = reminder
        self.message = message
        self.wait = wait
        self.end = time.time() + wait

    def __str__(self):
        return (
            f"{self.message.author.name}'s Reminder: {self.reminder} in "
            f"{convert_time_difference_to_str(self.end - time.time())}"
        )

    async def post_reminder(self):
        await asyncio.sleep(self.wait)
        await post_message(self.message, self.reminder)
        reminders.remove(self)


@client.event
async def on_message(message):
    if not message.content:
        print("No message provided")

    message_string = message.content.lower()

    # Wars
    if message_string.startswith("!startwar") and in_slagmark(message):
        msgin = message.content.split()

        str_start = 0
        if len(msgin) > 1:
            match = re.match("\[\d+\]", msgin[1])
            if match is not None:
                msgin[1] = msgin[1].strip("[]")
                str_start += 1

        war_ins, str_start = split_input_variables(msgin[str_start:], war_defaults)

        name = get_name_string(msgin[str_start:], message)
        if name.lower() in wars:
            await message.reply(
                "A war with that name already exists, please use a different name or end the current "
                "war.",
                mention_author=False,
            )
            return

        repetitions = war_ins[0]
        war_duration = war_ins[1] * minute_length
        wait_duration = war_ins[2] * minute_length

        # Legg inn en egen mulighet for dersom noen ber om en krig på nøyaktig ett år
        if war_ins[1] >= 1000:
            await post_message(
                message,
                f"Assuming you want !words instead of a {int(war_ins[1])} min long war",
            )
            await do_words(message)
            return

        war = War(name, message, war_duration, wait_duration, repetitions)
        await message.add_reaction("⚔")
        wars[name.lower()] = war

        await war.countdown()

    if message_string.startswith("!startwar") and not in_slagmark(message):
        await post_message(message, "I can not start a war in this channel")


    # Timers
    if message_string.startswith("!starttimer") and in_slagmark(message):
        msgin = message.content.split()

        str_start = 0
        if len(msgin) > 1:
            match = re.match("\[\d+\]", msgin[1])
            if match is not None:
                msgin[1] = msgin[1].strip("[]")
                str_start += 1

        timer_ins, str_start = split_input_variables(msgin[str_start:], timer_defaults)

        name = get_name_string(msgin[str_start:], message)
        if name.lower() in timers:
            await message.reply(
                "A timer with that name already exists, please use a different name or end the current "
                "timer.",
                mention_author=False,
            )
            return

        repetitions = timer_ins[0]
        timer_duration = timer_ins[1] * minute_length
        wait_duration = timer_ins[2] * minute_length

        # Legg inn en egen mulighet for dersom noen ber om en krig på nøyaktig ett år
        if timer_ins[1] >= 1000:
            await post_message(
                message,
                f"Assuming you want !words instead of a {int(timer_ins[1])} min long timer",
            )
            await do_words(message)
            return

        timer = Timer(name, message, timer_duration, wait_duration, repetitions)
        await message.add_reaction("⏳")
        timers[name.lower()] = timer

        await timer.countdown()


    # Start sessions
    if message_string.startswith("!startsession") and in_slagmark(message):
        msgin = message.content.split()
        in_list, str_start = split_input_variables(msgin[1:], session_defaults)
        try:
            if msgin[str_start]:
                name = get_name_string(msgin[str_start:], message)
                if name.lower() in sessions:
                    await message.reply(
                        "A session with that name already exists, please use a different name or "
                        "end the current session.",
                        mention_author=False,
                    )
                    return
        except IndexError:
            await message.reply("Please include a name", mention_author=False)
            return
        if in_list[0] < in_list[2] + in_list[4]:
            await message.reply(
                "Duration must be greater than the sum of the max values",
                mention_author=False,
            )
            return
        if in_list[2] < in_list[3] or in_list[4] < in_list[5]:
            await message.reply(
                "Min values must be greater than max values", mention_author=False
            )
            return

        session = Session(name, message, in_list)
        sessions[name.lower()] = session
        await session.run()

    # Ending either sessions or a ongoing war.
    # Name of the war/session is required
    if message_string.startswith("!endwar") and in_slagmark(message):
        name = message.content.split()
        if name[0][4:].lower() == "session":
            ending = sessions
            ending_str = "session"
        else:
            ending = wars
            ending_str = "war"

        name = get_name_string(name[1:], message).lower()
        if name in ending:
            if ending[name].user == message.author or is_role(
                message.author, admin_roles
            ):
                ended = ending.pop(name)
                msgout = f"{ending_str.capitalize()}: {ended.name} cancelled"
            else:
                msgout = f"You can only end your own {ending_str}."
        else:
            msgout = f"No {ending_str} with that name."
        await post_message(message, msgout)

    if message_string.startswith("!endtimer") and in_slagmark(message):
        name = message.content.split()
        if name[0][4:].lower() == "session":
            ending = sessions
            ending_str = "session"
        else:
            ending = timers
            ending_str = "timer"

        name = get_name_string(name[1:], message).lower()
        if name in ending:
            if ending[name].user == message.author or is_role(
                message.author, admin_roles
            ):
                ended = ending.pop(name)
                msgout = f"{ending_str.capitalize()}: {ended.name} cancelled"
            else:
                msgout = f"You can only end your own {ending_str}."
        else:
            msgout = f"No {ending_str} with that name."
        await post_message(message, msgout)

    # TODO: Fix single war in another server
    # Lists all ongoing wars
    if message_string.startswith("!list"):
        listings = message.content.split()
        listings[0] = listings[0][5:]

        if listings[0] == "":
            listings = ["wars", "timers"]
        if listings[0] == "all":
            listings = params_list

        if listings[0] not in params:
            return

        if listings == ["wars"] and len(wars) == 1:
            for key in wars:
                war = wars[key]
            await post_message(war.message, war.__str__(False))
            return

        if listings == ["timers"] and len(timers) == 1:
            for key in timers:
                timer = timers[key]
            await post_message(timer.message, timer.__str__(False))
            return

        msg = ""
        for listing in listings:
            for param in params:
                if listing == param:
                    if len(params[param]) > 0:
                        for key in params[param]:
                            msg += params[param][key].__str__() + "\n"
                    else:
                        msg += f"No {param} at this time \n"
        await post_message(message, msg)

    # Role for those who do NOT want pings during a war.
    # Only start and end
    if message_string.startswith("!no-countdown"):
        if is_role(message.author, ["No-Countdown"]):
            await message.author.remove_roles(
                discord.utils.get(message.author.guild.roles, name="No-Countdown")
            )
        else:
            await message.author.add_roles(
                discord.utils.get(message.author.guild.roles, name="No-Countdown")
            )

    # Calls def for saving wordcount to user
    if message_string.startswith("!words"):
        await do_words(message)

    # EK Exclusive
    # TODO: Ta med videre
    # Sjekk ut hvordan event kan returnere et svar med en gang
    if (
        message_string.startswith("!makeevent")
        and is_role(message.author, admin_roles)
        and not in_slagmark(message)
    ):
        if "{" not in message.content or not message.content.endswith("}"):
            await message.reply(
                "Events must be formatted as !MakeEvent <message> <{YYYY-MM-DD HH:MM}>",
                mention_author=False,
            )
            return

        msgin = message.content.split("{")
        msg = (msgin[0]).split()
        msg = get_name_string(msg[1:], message)

        if msg[0:3] == "tts":
            tts = True
            msg = msg[3:]
        else:
            tts = False

        if msg == "":
            await message.reply(
                "Please include the name of the event", mention_author=False
            )
            return

        time_in = str(msgin[1]).replace("}", "")
        time_in = time_in.split(", ")

        msg_lower = msg.lower()

        for date in time_in:
            try:
                converted_time = time.mktime(time.strptime(date, "%Y-%m-%d %H:%M"))
                if converted_time > time.time():
                    if msg_lower in events:
                        if converted_time in events[msg_lower]:
                            await post_message(
                                message, f"Date {date} is already set for this event."
                            )
                        else:
                            events[msg_lower].push(converted_time)
                            await post_message(message, f"Event {msg} added for {date}")
                    else:
                        events[msg_lower] = Event(msg, message, tts)
                        events[msg_lower].push(converted_time)
                        await post_message(message, f"Event {msg} set for {date}")
                else:
                    await post_message(
                        message,
                        f"Date {date} is in the past. Make sure you format it"
                        f" correctly",
                    )
            except ValueError:
                await post_message(message, f"Date {date} was formatted incorrectly")

        if msg_lower in events:
            await events[msg_lower].run_event()
            return

    # TODO: Ta med videre
    # Tanke: en måte å registrere seg så man slipper @everyone
    # Creates a repetativ @everyone
    if (
        message_string.startswith("!spam")
        and is_role(message.author, admin_roles)
        and not in_slagmark(message)
    ):
        msgin = message.content.split()
        freq_list, str_start = split_input_variables(msgin[1:], spam_defaults)
        freq = freq_list[0] * minute_length
        print(f"Message: {msgin},\nFrequency list: {freq_list},\nFrequency: {freq}")
        try:
            if msgin[str_start]:
                msg = get_name_string(msgin[str_start:], message)
                if msg != "":
                    spam = Spam(message, msg, freq)
                    spam_dict[msg.lower()] = spam
                    await spam.run()
        except IndexError:
            await message.reply("Please include a message", mention_author=False)

    # Stops a spam-event(?)
    if message_string.startswith("!stop") and is_role(message.author, admin_roles):
        msgin = message.content.split()
        msg = get_name_string(msgin[1:], message).lower()
        msgout = ""
        for param in params:
            if msg in params[param]:
                params[param].pop(msg)
                msgout += f"{param.capitalize()}: {msg} stopped \n"
        if msgout == "":
            msgout += "No spam or event with that name"
        await post_message(message, msgout)

    if message_string.startswith("!nuke") and is_role(message.author, admin_roles):
        msgin = message.content.split()
        params_in = msgin[1:]

        if len(params_in) == 0:
            params_in = params_list
        if params_in[0] not in params:
            return

        msgout = ""
        for in_param in params_in:
            for param in params:
                if in_param == param:
                    msgout += f"All {param} ended \n"
                    params[param].clear()
                    break
        await message.reply(msgout, mention_author=False)

    if message_string.startswith("!purge") and is_role(message.author, admin_roles):
        try:
            roles = message.role_mentions
        except IndexError:
            await message.reply("Please ping at least one role", mention_author=False)
            return
        for role in roles:
            members = role.members
            for member in members:
                if is_role(member, [role.name]):
                    await member.remove_roles(
                        discord.utils.get(member.roles, name=role.name)
                    )

    if message_string.startswith("!addrole") and is_role(message.author, admin_roles):
        apply_to = []
        apply_roles = []

        try:
            roles = message.role_mentions
        except IndexError:
            await message.reply("Please ping at least two roles", mention_author=False)
            return

        for role in roles:
            if "⎼" in role.name:
                apply_roles.append(role)
            else:
                apply_to.append(role)

        if len(apply_to) < 1 or len(apply_roles) < 1:
            await message.reply(
                "Please ping both a role to apply and a role for it to be applied to. Roles to apply "
                "should contain the letter '-'",
                mention_author=False,
            )

        for role in apply_to:
            members = role.members
            for member in members:
                for r in apply_roles:
                    await member.add_roles(
                        discord.utils.get(message.author.guild.roles, name=r.name)
                    )

    # Reminders
    if message_string.startswith("!remind"):
        msgin = message_string.split()
        try:
            wait = float(msgin[1]) * minute_length
        except ValueError:
            await message.reply(
                "Please provide a number for how long until you want to be reminded in minutes",
                mention_author=False,
            )
            return

        msgout = get_name_string(msgin[2:], message)
        reminder = Reminder(msgout, message, wait)
        reminders.append(reminder)
        await reminder.post_reminder()

    if message_string.startswith("!rlist"):
        if len(reminders) > 0:
            msgout = ""
            for r in reminders:
                msgout += r.__str__() + "\n"
        else:
            msgout = "No reminders active at this time"
        await post_message(message, msgout)

    # Misc
    if (re.match("!(\d*)d(?!\D)", message_string) is not None) and in_slagmark(message):
        if re.match("(\d+)", message_string[1:]) is not None:
            amount = int(re.match("(\d+)", message_string[1:]).group())
            str_start = len(str(amount)) + 2
        else:
            amount = 1
            str_start = 2

        if re.match("(\d+)", message_string[str_start:]) is not None:
            num = int(re.match("(\d+)", message_string[str_start:]).group())
        else:
            num = 6

        ran_num = ""
        count = 0
        for _ in range(amount):
            count += 1
            ran_num += f"{random.randint(1, int(num))}, "
        ran_num = ran_num[:-2]
        await post_message(message, ran_num)

    if message_string.startswith("!hydra"):
        msgin = message.content.split()
        try:
            year = int(msgin[1])
        except (ValueError, IndexError):
            year = 0

        if year in year_end:
            if year - 1 == year_before_first:
                value_bottom = 0
            else:
                value_bottom = year_end[year - 1]
            value = random.randint(value_bottom, year_end[year])
        else:
            value = random.randint(0, len(hydras) - 1)

        await post_message(message, hydras[value])

    if message_string.startswith("!foof") and not in_slagmark(message):
        await message.channel.send("Righto... ")
        await asyncio.sleep(1.5)
        await message.channel.send(
            "**Timmy** surreptitiously works his way over to the couch, looking ever so casual.."
            "."
        )
        await asyncio.sleep(5)
        ran = random.randint(0, len(pillows) - 1)
        try:
            mention = message.mentions[0].mention
        except IndexError:
            mention = message.author.mention
        await message.channel.send(
            f"**Timmy** grabs a {pillows[ran]} pillow, and throws it at {mention},"
            " hitting them squarely in the back of the head."
        )

    # !reply
    elif message_string.startswith("!"):
        incommand = message.content.lower().split("!")
        # print(f'Message sent from user: {incommand}')
        if incommand[1] in commands:
            # print(f'Command ordered: {message, commands[incommand[1]]()}')
            try:
                await post_message(message, commands[incommand[1]]())
            except TypeError:
                await post_message(message, commands[incommand[1]])


async def do_words(message):
    msgin = message.content.split()
    msgout = ""

    try:
        user_wordcount = int(msgin[1])
        if msgin == None:
            msgout = 'No value provided. Use "!words <wordcount>!'
        elif message.author in user_wordcounts:
            words_written = user_wordcount - user_wordcounts[message.author]
            msgout += f"You wrote {words_written} words. "
            user_wordcounts.pop(message.author)
            try:
                session_len = int(msgin[2])
                wpm = float(words_written / session_len)
                msgout += f"Your wpm is {round(wpm)}. "
            except (IndexError, ValueError):
                pass

            diff_to_goal = 0
            has_alt_goal = True
            try:
                alt_goal = int(msgin[3])
                diff_to_goal = user_wordcount - alt_goal
            except ValueError:
                has_alt_goal = False
            except IndexError:
                day = time.localtime()
                if day[1] == november:
                    diff_to_goal = user_wordcount - get_word_count()
                else:
                    has_alt_goal = False
            finally:
                if has_alt_goal:
                    msgout += "You're "
                    if diff_to_goal == 0:
                        msgout += "exactly on target"
                    else:
                        msgout += str(abs(diff_to_goal))
                        if diff_to_goal > 0:
                            msgout += " ahead of"
                        elif diff_to_goal < 0:
                            msgout += " behind"
                        msgout += " the goal for the day"

        else:
            user_wordcounts[message.author] = user_wordcount

    except (IndexError, ValueError):
        # msgout += 'Please provide a valid wordcount'
        current_word_count = user_wordcounts[message.author]
        msgout += f"Your current wordcount is {current_word_count}"

    await post_message(message, msgout)


async def post_message(message, msgin, tts=False, reply=True, mention=False):
    channel = message.channel
    if msgin == "":
        return
    if not reply:
        message = None
    if len(str(msgin)) < char_limit:
        await channel.send(msgin, tts=tts, reference=message, mention_author=mention)
    else:
        messages = []
        amount, remainder = divmod(len(msgin), char_limit)
        for i in range(amount):
            messages.append(msgin[0:char_limit])
            msgin = msgin[char_limit : len(msgin)]
        messages.append(msgin)
        for msgout in messages:
            await channel.send(
                msgout, tts=tts, reference=message, mention_author=mention
            )


def split_input_variables(list_of_strings, list_of_vars):
    num_vars = len(list_of_vars) + 1
    return_list = []
    for i in range(0, len(list_of_vars)):
        try:
            return_list.append(float(list_of_strings[i]))
        except (ValueError, IndexError):
            return_list.append(list_of_vars[i][1])
            num_vars -= 1
    return return_list, num_vars


def get_name_string(msg_list, message):
    msg = ""
    for i in msg_list:
        msg = msg + i + " "

    if msg == "" and message.content.lower().startswith("!startwar"):
        msg += get_prompt()

    if msg == "" and message.content.lower().startswith("!starttimer"):
        msg += ""

    return msg.strip()


def is_role(user, roles):
    for role in roles:
        if role in [role.name for role in user.roles]:
            return True
    return False


# Denne her er viktig for å få han til å fungere i DC-kanal (slagmark)
def in_slagmark(message):
    if "📎" in message.channel.name:
        return True
    return False


def convert_time_difference_to_str(diff):
    msg = ""
    for duration in duration_lengths:
        if int(diff) >= duration[0]:
            amount, diff = divmod(diff, duration[0])
            msg += f"{int(amount)} {duration[1]}"
            if amount > 1:
                msg += "s"
            if diff >= 1:
                msg += ", "
    return msg


def get_prompt():
    ran = random.randint(0, len(prompts) - 1)
    return prompts[ran]


def get_word_count():
    day = time.localtime()
    if day[1] == november:
        return nano_wordcounts[day[2] - 1]
    return ""


@client.event
async def on_ready():
    print("Yay")
    print(get_prompt())
    while True:
        day = time.localtime()
        if day[1] == november:
            status = f"Goal: {get_word_count()}"
        else:
            status = get_prompt()

        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name=status)
        )
        time_past_midnight = day[3] * 3600 + day[4] * 60 + day[5]
        time_to_midnight = 86400 - time_past_midnight
        await asyncio.sleep(time_to_midnight)


wars = {}
timers = {}
spam_dict = {}
events = {}
sessions = {}
reminders = []
params = {"wars": wars, "timers": timers, "spam": spam_dict, "events": events, "sessions": sessions}
params_list = ["wars", "timers", "spam", "events", "sessions"]
user_wordcounts = {}

char_limit = 2000
november = 11
minute_length = 60
session_defaults = [
    ("duration", 90),
    ("difficulty", 0),
    ("max_war", 30),
    ("min_war", 5),
    ("max_wait", 10),
    ("min_wait", 1),
]
spam_defaults = [("freq", 30)]
war_defaults = [("repetitions", 1), ("war_len", 10), ("wait_len", 1)]
timer_defaults = [("repetitions", 1), ("timer_len", 25), ("wait_len", 1)]
war_len_intervals = [120, 60, 30, 20, 10, 5, 1, 0]
war_len_intervals = [interval * minute_length for interval in war_len_intervals]
timer_intervals = [120, 60, 30, 20, 10, 5, 1, 0]
timer_intervals = [interval * minute_length for interval in timer_intervals]
duration_lengths = [(86400, "day"), (3600, "hour"), (60, "minute"), (1, "second")]
nano_wordcounts = [
    1667,
    3333,
    5000,
    6667,
    8333,
    10000,
    11667,
    13333,
    15000,
    16667,
    18333,
    20000,
    21667,
    23333,
    25000,
    26667,
    28333,
    30000,
    31667,
    33333,
    35000,
    36667,
    38333,
    40000,
    41667,
    43333,
    45000,
    46667,
    48333,
    50000,
]

pillows = []
reading = open("pillowlist.txt", "r")
for pillow in reading:
    pillows.append(pillow.strip())
reading.close()

prompts = []
reading = open("prompts.txt", "r")
for prompt in reading:
    prompts.append(prompt)
reading.close()

commands = {
    "starwar": "A long time ago, in a galaxy far far away.",
    "cheer": "You can do it! "
    "https://38.media.tumblr.com/91599091501f182b0fbffab90e115895/tumblr_nq2o6lc0Kp1s7widdo1_250.gif",
    "woot": "cheers! Hooray!",
    "help": "Read the section about Timmy in <#526175203873521694>",
    "count word": "https://cdn.discordapp.com/attachments/526175173867732993/636293153229373470/IMG_20191022_220137.jpg",
    "bart i sjela": "så da er det bart i sjela, komma i hjertet, tastatur i fingrene, fyllepenn i milten og "
    "lommer på skjørtet. snart har vi en full person med dette",
    "pisk": "<:pisk:556560214590095361> <:pisk:556560214590095361> <:pisk:556560214590095361>",
    "crawl": "https://docs.google.com/spreadsheets/d/1faSYMFcCR8_GabdAt4akegayoR9g9JWCLmLb5gnfPkQ/edit?usp=sharing",
    "trua": "I'm threatening you, you can do this",
    "belinda": "https://www.amazon.com/dp/B07D1JQ664/?tag=097-20&ascsubtag=v7_1_29_g_4j8r_4_x01_-srt5- \n"
    "https://www.flickr.com/photos/caroslines/760491974",
    "domherren": "https://www.fuglelyder.net/dompap/",
    "paven": "http://m.ocdn.eu/_m/a68e24c99236c40d6f9d01823a4b7ebe,14,1.jpg",
    "prompt": get_prompt,
    "wordcount": get_word_count,
    "ml": ":lizard:",
    "ekine": "https://docs.google.com/document/d/1AQX9uNqqn2-pQetUzivMySZPufIkxSGyJqotTJcy_ms/edit",
    "møbelet": "Det er et møbel. Med ansikt. Og det hater meg. "
    "https://cdn.discordapp.com/attachments/683656630138961921/824283058970558564/mbelet.jpg",
    "belindaserdeg": "https://tenor.com/view/chicken-petting-staring-im-watching-you-gif-4613862",
}

year_before_first = 2018
year_end = {2019: 16, 2020: 26}
hydras = []
reading = open("hydras.txt", encoding="utf8")
for hydra in reading:
    hydras.append(hydra)
reading.close()

admin_roles = ["Moderator", "Event Koordinator", "BotMaster"]

# reading = open('key.txt', 'r')
# TOKEN = reading.readline().strip()
# reading.close()

load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")


def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()
