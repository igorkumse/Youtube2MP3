"""
playlist2mp3.py
===============

Prebere celoten YouTube seznam predvajanja (playlist) in za vsak video
uporabi program youtube2mp3.py, da ga shrani na disk kot MP3.

Uporaba iz ukazne vrstice:
    python playlist2mp3.py <URL_SEZNAMA> [--bitrate 192] [--output MAPA]

Zahteve:
    - Python paket:  yt-dlp   (pip install yt-dlp)
    - Zunanji program: ffmpeg (mora biti dosegljiv v PATH)
    - Datoteka youtube2mp3.py v isti mapi.
"""

from __future__ import annotations

import argparse
import sys

try:
    from yt_dlp import YoutubeDL
except ImportError:  # pragma: no cover
    print(
        "Manjka paket 'yt-dlp'. Namesti ga z:\n    pip install yt-dlp",
        file=sys.stderr,
    )
    raise

# Uvozimo prvi program in ga uporabimo za dejanski prenos posameznih videov.
from youtube2mp3 import DEFAULT_OUTPUT_DIR, download_audio


def list_playlist(url: str) -> list[dict]:
    """Prebere seznam vseh videov iz playliste (brez prenosa).

    Uporabi "flat" ekstrakcijo, da hitro dobi le osnovne podatke
    (naslov in URL) o vsakem videu v seznamu.

    Returns:
        Seznam slovarjev z ključi 'title' in 'url' za vsak video.
    """
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",  # ne prenašaj, samo naštej
        "skip_download": True,
    }

    videos: list[dict] = []
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries") if info else None
    if not entries:
        # Morda je bil podan URL enega samega videa.
        if info and info.get("webpage_url"):
            return [
                {
                    "title": info.get("title", "neznano"),
                    "url": info["webpage_url"],
                }
            ]
        return videos

    for entry in entries:
        if not entry:
            continue
        # 'url' je pri flat ekstrakciji lahko le ID; sestavimo polni naslov.
        raw_url = entry.get("url") or entry.get("id")
        if raw_url and not str(raw_url).startswith("http"):
            raw_url = f"https://www.youtube.com/watch?v={raw_url}"
        webpage = entry.get("webpage_url") or raw_url
        if not webpage:
            continue
        videos.append(
            {
                "title": entry.get("title", "neznano"),
                "url": webpage,
            }
        )

    return videos


def download_playlist(
    url: str,
    bitrate: int = 192,
    output_dir: str | None = None,
    quiet: bool = False,
) -> list[str]:
    """Prenese vse videe iz seznama in vrne poti do shranjenih MP3 datotek."""
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    videos = list_playlist(url)
    if not videos:
        print("V seznamu ni bilo mogoče najti nobenega videa.", file=sys.stderr)
        return []

    total = len(videos)
    print(f"Najdenih {total} videov v seznamu.\n")

    saved: list[str] = []
    for index, video in enumerate(videos, start=1):
        title = video["title"]
        print(f"[{index}/{total}] {title}")
        try:
            path = download_audio(
                url=video["url"],
                bitrate=bitrate,
                output_dir=output_dir,
                quiet=quiet,
            )
            saved.append(path)
            print(f"    OK -> {path}\n")
        except Exception as exc:  # noqa: BLE001
            # En neuspel video ne sme ustaviti celotnega seznama.
            print(f"    Napaka, preskočeno: {exc}\n", file=sys.stderr)

    print(f"Končano. Uspešno shranjenih {len(saved)}/{total} skladb.")
    return saved


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prebere celoten YouTube seznam predvajanja in vsak video "
            "shrani kot MP3 (s pomočjo youtube2mp3.py)."
        )
    )
    parser.add_argument("url", help="Povezava do YouTube seznama (playliste).")
    parser.add_argument(
        "-b",
        "--bitrate",
        type=int,
        default=192,
        help="Kakovost zvoka v kbps (privzeto 192).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help='Ciljna mapa (privzeto mapa "muzika" poleg programa).',
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Manj izpisov.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        download_playlist(
            url=args.url,
            bitrate=args.bitrate,
            output_dir=args.output,
            quiet=args.quiet,
        )
    except KeyboardInterrupt:
        print("\nPrekinjeno.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"Nepričakovana napaka: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
