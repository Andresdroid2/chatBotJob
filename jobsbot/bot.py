import asyncio
import logging

import httpx
from sqlalchemy.orm import Session, sessionmaker
from telegram import LinkPreviewOptions, Update
from telegram.error import Forbidden, TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes

from .service import (
    MAX_FILTERS_PER_CHAT,
    add_filter,
    delete_chat_data,
    list_filters,
    mark_sent,
    pending_alerts,
    remove_filter,
)
from .source import JobPost, fetch_all_jobs

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "👋 Te aviso cuando aparezcan ofertas de trabajo remoto que coincidan con tus filtros.\n\n"
    "/agregar <palabras> - nuevo filtro (ej: /agregar python junior)\n"
    "/lista - ver tus filtros\n"
    "/quitar <número> - eliminar un filtro (ej: /quitar 2)\n"
    "/ayuda - ver este mensaje\n\n"
    "Un filtro con varias palabras exige que todas aparezcan en el título, empresa o etiquetas."
)

ADD_MESSAGES = {
    "added": "✅ Filtro agregado: {keyword}",
    "duplicate": "Ya tienes ese filtro.",
    "limit": f"Llegaste al máximo de {MAX_FILTERS_PER_CHAT} filtros. Quita alguno con /quitar.",
    "empty": "Uso: /agregar <palabras>, por ejemplo /agregar python junior",
}


def _sessions(context: ContextTypes.DEFAULT_TYPE) -> sessionmaker[Session]:
    return context.application.bot_data["session_factory"]


def format_job(job: JobPost) -> str:
    lines = [f"🆕 {job.title}"]
    if job.company:
        lines.append(f"🏢 {job.company}")
    if job.location:
        lines.append(f"📍 {job.location}")
    lines.append(f"🔗 {job.url}")
    lines.append(f"Fuente: {job.source}")
    return "\n".join(lines)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw = " ".join(context.args)
    with _sessions(context)() as session:
        result = add_filter(session, update.effective_chat.id, raw)
    keyword = " ".join(raw.lower().split())
    await update.message.reply_text(ADD_MESSAGES[result].format(keyword=keyword))


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with _sessions(context)() as session:
        filters = list_filters(session, update.effective_chat.id)
    if not filters:
        await update.message.reply_text("No tienes filtros. Agrega uno con /agregar python junior")
        return
    lines = [f"{i}. {f.keyword}" for i, f in enumerate(filters, start=1)]
    await update.message.reply_text("Tus filtros:\n" + "\n".join(lines))


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /quitar <número>, mira los números con /lista")
        return
    with _sessions(context)() as session:
        keyword = remove_filter(session, update.effective_chat.id, int(context.args[0]))
    if keyword is None:
        await update.message.reply_text("No existe un filtro con ese número. Revisa /lista")
    else:
        await update.message.reply_text(f"🗑️ Filtro eliminado: {keyword}")


async def check_jobs(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scheduled task: fetch jobs, find new matches and notify each chat."""
    headers = {"User-Agent": "jobs-alert-bot/1.0 (personal project)"}
    async with httpx.AsyncClient(timeout=20, headers=headers, follow_redirects=True) as client:
        jobs = await fetch_all_jobs(client)
    if not jobs:
        logger.warning("No jobs fetched from any source; skipping this run")
        return

    with _sessions(context)() as session:
        alerts = pending_alerts(session, jobs)
        logger.info("Fetched %d jobs, %d alerts to send", len(jobs), len(alerts))
        for chat_id, job in alerts:
            try:
                await context.bot.send_message(
                    chat_id,
                    format_job(job),
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            except Forbidden:
                logger.info("Chat %s blocked the bot; removing its data", chat_id)
                delete_chat_data(session, chat_id)
            except TelegramError:
                logger.exception("Could not send alert to chat %s", chat_id)
            else:
                mark_sent(session, chat_id, job.url)
            await asyncio.sleep(0.05)  # stay well under Telegram's rate limits


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler(["start", "ayuda"], help_command))
    application.add_handler(CommandHandler("agregar", add_command))
    application.add_handler(CommandHandler("lista", list_command))
    application.add_handler(CommandHandler("quitar", remove_command))