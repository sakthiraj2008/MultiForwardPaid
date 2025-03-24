import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
import os, sys, io, traceback
from datetime import datetime 
from contextlib import redirect_stdout
from subprocess import getoutput as run
from pyrogram.enums import ChatAction
from pyrogram.errors import PeerIdInvalid

logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('log.txt'),
                                                  logging.StreamHandler()], format="[KORA]: %(message)s")

API_ID = 22499495
API_HASH = "0d993e3aef2c008361850e995ace3adb"
BOT_TOKEN = "5842656006:AAE17eEnRGpiVDA4I6MXJtXA2LYs6FkFPg4"  

SOURCE_CHANNEL = -1002591052260  

DEST_CHANNELS = [
    -1002547462385,  
    -1002646034742,
    #-1003333333333,  
    #-1004444444444,  
    #-1005555555555,  
    #-1006666666666,  
    #-1007777777777,  
    #-1008888888888,  
    #-1009999999999,  
    #-1001010101010,  
]

AUTH_USERS = [6495253163]  

app = Client("ForwardBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id in AUTH_USERS:
        await message.reply_text("✅ Bot is Active!")
    else:
        await message.reply_text("🚫 Unauthorized Access!")

@app.on_message(filters.channel & filters.chat(SOURCE_CHANNEL))
async def forward_messages(client, message):
    for channel in DEST_CHANNELS:
        if channel:
            try:
                await message.copy(chat_id=channel)
            except PeerIdInvalid:
                print(f"Skipping invalid channel: {channel}")
            except Exception as e:
                print(f"Error forwarding to {channel}: {e}")


prefix = [".","!","?","*","$","#","/"]
DEV_ID = [6495253163]

@app.on_message(filters.command(["sh", "shell"], prefix) & filters.user(DEV_ID))
async def sh(client,message):

    if len(message.command) <2:
         await message.reply_text("`No Input Found!`")
    else:
          code = message.text.replace(message.text.split(" ")[0], "")
          x = run(code)
          string = f"**📎 Input**: `{code}`\n\n**📒 Output **:\n`{x}`"
          try:
             await message.reply_text(string) 
          except Exception as e:
              with io.BytesIO(str.encode(string)) as out_file:
                 out_file.name = "shell.text"
                 await message.reply_document(document=out_file, caption=e)


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)
 
@app.on_message(filters.command(["eval", "e"], prefix) & filters.user(DEV_ID))
async def eval(client, message):
    if len(message.text.split()) < 2:
        return await message.reply_text("No codes found!")
    
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(None, 1)[1]
    start = datetime.now()
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    
    end = datetime.now()
    ping = (end - start).microseconds / 1000
    final_output = f"📎 Input: {cmd}\n\n📒 Output:\n{evaluation.strip()} \n\n✨ Taken Time: {ping}ms"

    if len(final_output) > 1020:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file, caption="Evaluation Output", disable_notification=True
            )
    else:
        await status_message.edit_text(final_output)
        
@app.on_message(filters.command(["log", "logs"], prefix) & filters.user(DEV_ID))
async def logs(app, message):
    run_logs = run("tail log.txt")
    text = await message.reply_text("`Getting Logs...`")
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    await message.reply_text(f"```shell\n{run_logs}```")
    await text.delete()

@app.on_message(filters.command(["flogs", "flog"], prefix) & filters.user(DEV_ID))
async def flogs(app, message):
    run_logs = run("cat log.txt")
    text = await message.reply_text("`Sending Full Logs...`")
    await app.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
    with io.BytesIO(str.encode(run_logs)) as logs:
        logs.name = "log.txt"
        await message.reply_document(
            document=logs,
        )
    await text.delete()

if __name__ == "__main__":
    logging.info("Bot is starting...")
    app.run()
