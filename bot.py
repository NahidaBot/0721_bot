import json
import logging
import datetime
import subprocess

from config import config

from telegram import Update, BotCommand, InputMediaDocument, Message
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

if config.debug:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(config.txt_help, parse_mode=ParseMode.HTML)


async def get_origin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    # 如果是自动转发的
    if msg.from_user.id == 777000:
        return await reply_origin_pic(msg)
    await reply_origin_pic(update.message.reply_to_message)
    # 如果不是由自动转发触发的（使用 /get_origin 命令手动触发），则删除原消息
    await update.message.delete(read_timeout=20)


async def reply_origin_pic(channel_msg: Message):
    try:
        urls: list[str] = []
        for entity in channel_msg.caption_entities:
            caption: str = channel_msg.caption
            if entity.type == "text_link":
                urls.append(entity.url)
            if entity.type == "url":
                url = caption[entity.offset : entity.length + entity.offset]
                urls.append(url)
    except Exception as e:
        logger.error(e)
        return await channel_msg.reply_text(
            f"获取失败，请在对应消息的评论区回复该命令：`/get_origin`", parse_mode=ParseMode.MARKDOWN_V2
        )
    url = urls[0]  # 只取第一个 url
    try:
        # 要执行的命令, 包括 gallery-dl 命令和要下载的图库URL
        command = ["gallery-dl", url, "-j", "-q"]

        # 使用subprocess执行命令
        result: subprocess.CompletedProcess = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.debug(result.stdout)
        logger.debug("获取完成！")
    except subprocess.CalledProcessError as e:
        logger.error("获取出错:" + e)
        return await channel_msg.reply_text("获取失败，请查看日志")
    tweet_json: list[list] = json.loads(result.stdout)
    if len(tweet_json) <= 1:
        return await channel_msg.reply_text("推文中没有获取到图片")
    await channel_msg.reply_chat_action("upload_document")
    media_group = []
    for image in tweet_json:
        if image[0] == 3:
            media_group.append(InputMediaDocument(image[1]))

    await channel_msg.reply_media_group(media_group, write_timeout=60, read_timeout=20)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("online! (* /ω＼*)")


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = [
        BotCommand("ping", "在线检测"),
        BotCommand("get_origin", "(在频道评论区发送) 获取原图"),
        BotCommand("help", "帮助"),
    ]

    r = await context.bot.set_my_commands(commands)
    await update.message.reply_text(str(r))

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raise SystemExit

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    global application
    application = Application.builder().token(config.bot_token).build()

    global bot
    bot = application.bot
    application.bot_data["last_msg"] = datetime.datetime.fromtimestamp(0)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("set_commands", set_commands))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("get_origin", get_origin))
    application.add_handler(
        MessageHandler(
            filters.FORWARDED
            & filters.PHOTO 
            & filters.User(777000),
            get_origin,
        )
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
