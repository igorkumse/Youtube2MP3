"""
youtube2mp3.py
==============

Prenese zvočni tok iz posameznega YouTube videa in ga s pomočjo ffmpeg
pretvori v MP3.

Funkcije:
- Kakovost (bitrate) zvočnega toka izbereš s parametrom --bitrate
  (privzeto 192 kbps).
- V MP3 zapiše metapodatke (naslov / izvajalec).
- Vgradi naslovno sliko (thumbnail) kot album art.
- Datoteke se privzeto shranijo v mapo "muzika" poleg tega programa.

Uporaba iz ukazne vrstice:
    python youtube2mp3.py <URL> [--bitrate 192] [--output MAPA]

Uporaba kot modul (glej playlist2mp3.py):
    from youtube2mp3 import download_audio
    pot = download_audio("https://www.youtube.com/watch?v=...", bitrate=256)

Zahteve:
    - Python paket:  yt-dlp   (pip install yt-dlp)
    - Zunanji program: ffmpeg (mora biti dosegljiv v PATH)
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
except ImportError:  # pragma: no cover
    print(
        "Manjka paket 'yt-dlp'. Namesti ga z:\n    pip install yt-dlp",
        file=sys.stderr,
    )
    raise

# Mapa, kjer se nahaja ta program, in privzeta ciljna mapa "muzika".
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "muzika")


def _build_ydl_opts(bitrate: int, output_dir: str, quiet: bool) -> dict:
    """Sestavi konfiguracijo za yt-dlp."""
    os.makedirs(output_dir, exist_ok=True)

    return {
        # Izberi najboljši zvočni tok (če ni ločenega, vzame najboljše, kar je).
        "format": "bestaudio/best",
        # Ime izhodne datoteke: <naslov>.<končnica>
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        # Naloži tudi naslovno sliko, da jo lahko vgradimo kot album art.
        "writethumbnail": True,
        # En video – tudi če je URL del seznama, ne prenašaj cele liste.
        "noplaylist": True,
        "quiet": quiet,
        "no_warnings": quiet,
        "ignoreerrors": False,
        # Postprocesorji – vse dela ffmpeg:
        "postprocessors": [
            # 1) Iz zvočnega toka naredi MP3 z izbranim bitrate-om.
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": str(bitrate),  # >=10 => -b:a <bitrate>k
            },
            # 2) Zapiši metapodatke (naslov, izvajalec ...).
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
            # 3) Vgradi naslovno sliko kot album art.
            {
                "key": "EmbedThumbnail",
                "already_have_thumbnail": False,
            },
        ],
    }


def download_audio(
    url: str,
    bitrate: int = 192,
    output_dir: str | None = None,
    quiet: bool = False,
) -> str:
    """Prenese in pretvori en YouTube video v MP3.

    Args:
        url: Povezava do YouTube videa.
        bitrate: Kakovost MP3 v kbps (privzeto 192).
        output_dir: Ciljna mapa (privzeto mapa "muzika" poleg programa).
        quiet: Če je True, yt-dlp piše manj sporočil.

    Returns:
        Absolutna pot do ustvarjene .mp3 datoteke.

    Raises:
        DownloadError: Če prenos ali pretvorba ne uspeta.
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    opts = _build_ydl_opts(bitrate=bitrate, output_dir=output_dir, quiet=quiet)

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Po pretvorbi je končnica vedno .mp3.
        base = ydl.prepare_filename(info)
        mp3_path = os.path.splitext(base)[0] + ".mp3"

    return os.path.abspath(mp3_path)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prenese zvočni tok YouTube videa in ga s ffmpeg pretvori v MP3 "
            "z metapodatki in vgrajeno naslovno sliko."
        )
    )
    parser.add_argument("url", help="Povezava do YouTube videa.")
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
        path = download_audio(
            url=args.url,
            bitrate=args.bitrate,
            output_dir=args.output,
            quiet=args.quiet,
        )
    except DownloadError as exc:
        print(f"Napaka pri prenosu: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Nepričakovana napaka: {exc}", file=sys.stderr)
        return 1

    print(f"Shranjeno: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
