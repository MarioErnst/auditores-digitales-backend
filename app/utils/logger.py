# -*- coding: utf-8 -*-
import sys


def _print(message: str) -> None:
    """Imprime a stdout con fallback para terminales Windows (cp1252)."""
    try:
        print(message)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((message + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()


def log_info(message: str) -> None:
    _print(f"[INFO] {message}")


def log_success(message: str) -> None:
    _print(f"[OK]   {message}")


def log_warning(message: str) -> None:
    _print(f"[WARN] {message}")


def log_error(message: str) -> None:
    _print(f"[ERR]  {message}")


def log_start(message: str) -> None:
    _print(f"[START] {message}")


def log_stop(message: str) -> None:
    _print(f"[STOP]  {message}")


def log_upload(message: str) -> None:
    _print(f"[UP]   {message}")


def log_chat(message: str) -> None:
    _print(f"[CHAT] {message}")
