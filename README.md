# Youtube2MP3

Dva Python programa za prenos zvoka iz YouTuba v MP3.

- **`youtube2mp3.py`** — prenese zvočni tok iz **enega** YouTube videa in ga s
  `ffmpeg` pretvori v MP3. Zapiše metapodatke (naslov / izvajalec) in vgradi
  naslovno sliko kot album art. Kakovost izbereš s parametrom `--bitrate`
  (privzeto **192 kbps**).
- **`playlist2mp3.py`** — prebere **celoten YouTube seznam predvajanja**
  (playlist) in za vsak video uporabi `youtube2mp3.py`, da ga shrani na disk.

Datoteke se privzeto shranijo v mapo **`muzika`** poleg programov.

## Zahteve

1. **Python 3.9+**
2. **ffmpeg** — mora biti nameščen in dosegljiv v `PATH`.
   - Windows: `winget install Gyan.FFmpeg` ali prenos z <https://ffmpeg.org>.
   - Preveri z: `ffmpeg -version`
3. **Python paketi**:

   ```bash
   pip install -r requirements.txt
   ```

## Uporaba

### En video

```bash
python youtube2mp3.py "https://www.youtube.com/watch?v=VIDEO_ID"
python youtube2mp3.py "https://www.youtube.com/watch?v=VIDEO_ID" --bitrate 256
python youtube2mp3.py "https://www.youtube.com/watch?v=VIDEO_ID" --output "D:\Glasba"
```

| Parameter        | Pomen                                   | Privzeto  |
| ---------------- | --------------------------------------- | --------- |
| `url`            | Povezava do videa                       | (obvezno) |
| `-b`, `--bitrate`| Kakovost zvoka v kbps                    | `192`     |
| `-o`, `--output` | Ciljna mapa                             | `muzika`  |
| `-q`, `--quiet`  | Manj izpisov                            | izklopljeno |

### Celoten seznam (playlist)

```bash
python playlist2mp3.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
python playlist2mp3.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --bitrate 320
```

Enaki parametri kot pri `youtube2mp3.py`. En neuspel video ne ustavi celotnega
seznama — program nadaljuje in na koncu izpiše, koliko skladb je uspešno shranil.

## Opomba

Program uporabljaj samo za vsebine, za katere imaš pravico do prenosa
(npr. lastne vsebine ali vsebine z ustreznim dovoljenjem).
