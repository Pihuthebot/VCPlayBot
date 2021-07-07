from asyncio.queues import QueueEmpty
from VCPlayBot.config import que
from pyrogram import Client, filters
from pyrogram.types import Message

from VCPlayBot.function.admins import set
from VCPlayBot.helpers.channelmusic import get_chat_id
from VCPlayBot.helpers.decorators import authorized_users_only, errors
from VCPlayBot.helpers.filters import command, other_filters
from VCPlayBot.services.callsmusic import callsmusic


@Client.on_message(filters.command("adminreset"))
async def update_admin(client, message: Message):
    chat_id = get_chat_id(message.chat)
    set(
        chat_id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("♻️️ 𝐀𝐝𝐦𝐢𝐧 𝐂𝐚𝐜𝐡𝐞 𝐑𝐞𝐟𝐫𝐞𝐬𝐞𝐝 !")


@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text("❗ 𝐇𝐞𝐲' 𝐒𝐭𝐮𝐩𝐢𝐝 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐈𝐬 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 𝐎𝐧 𝐕𝐜 😒!")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await message.reply_text("▶️ 𝐒𝐨𝐧𝐠 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐏𝐚𝐮𝐬𝐞𝐝 𝐌𝐲 𝐋𝐨𝐫𝐝 !")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text("❗ 𝐇𝐞𝐲' 𝐒𝐭𝐮𝐩𝐢𝐝 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐈𝐬 𝐑𝐞𝐬𝐮𝐦𝐞𝐝 𝐎𝐧 𝐕𝐜 😒!")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text("⏸ 𝐒𝐨𝐧𝐠 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐑𝐞𝐬𝐮𝐦𝐞𝐝 𝐌𝐲 𝐋𝐨𝐫𝐝 !")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ 𝐇𝐞𝐲' 𝐒𝐭𝐮𝐩𝐢𝐝 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐈𝐬 𝐒𝐭𝐫𝐞𝐚𝐦𝐢𝐧𝐠 𝐎𝐧 𝐕𝐜 😒!")
    else:
        try:
            callsmusic.queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("❌ 𝐒𝐨𝐧𝐠 𝐇𝐚𝐬 𝐁𝐞𝐞𝐧 𝐒𝐭𝐨𝐩𝐩𝐞𝐝 𝐌𝐲 𝐋𝐨𝐫𝐝 !")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ 𝐇𝐞𝐲' 𝐒𝐭𝐮𝐩𝐢𝐝 𝐍𝐨𝐭𝐡𝐢𝐧𝐠 𝐈𝐬 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 𝐓𝐨 𝐒𝐤𝐢𝐩 𝐎𝐧 𝐕𝐜 😒!")
    else:
        callsmusic.queues.task_done(chat_id)

        if callsmusic.queues.is_empty(chat_id):
            callsmusic.pytgcalls.leave_group_call(chat_id)
        else:
            callsmusic.pytgcalls.change_stream(
                chat_id, callsmusic.queues.get(chat_id)["file"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"✔️ 𝐒𝐤𝐢𝐩𝐩𝐞𝐝 :- **{skip[0]}**\n🎵 𝐍𝐨𝐰 𝐏𝐥𝐚𝐲𝐢𝐧𝐠 :- **{qeue[0][0]}**")


@Client.on_message(filters.command("admincache"))
@errors
async def admincache(client, message: Message):
    set(
        message.chat.id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("♻️️ 𝐀𝐝𝐦𝐢𝐧 𝐂𝐚𝐜𝐡𝐞 𝐑𝐞𝐟𝐫𝐞𝐬𝐞𝐝 !")
