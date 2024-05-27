# Gucken

Project state: **Pre-Alpha**

## Description

Gucken is a Terminal User Interface which allows you to browse and watch your favorite anime's with style. 

## Usage

<img alt="Search" src="https://github.com/Commandcracker/gucken/assets/49335821/d91de2af-c086-485c-8aec-1e68cdb02aa3"/>
<img alt="Watch" src="https://github.com/Commandcracker/gucken/assets/49335821/7354eeff-bd97-4226-91b9-317939128a81"/> 

## Installation

<details><summary><b>Windows</b></summary>

Install [Python] and if you are **on Windows 10** [Windows Terminal] for a better experience.

```
pip install gucken
gucken
```

</details>

<details><summary><b>Linux</b></summary>

Install [Python] and then

```
pip install gucken
gucken
```

</details>

<details><summary><b>Android</b></summary>

Install [Termux](https://termux.dev/en/) and run:

```
yes|pkg update
pkg install python ffmpeg -y
pip install gucken
gucken
```

#### Shortcut

Install [Termux:Widget](https://github.com/termux/termux-widget?tab=readme-ov-file#Installation).

```
mkdir ~/.shortcuts
```

##### Lunch shortcut

```
echo gucken>~/.shortcuts/Gucken
```

##### Update shortcut

```
echo pip install -U gucken>~/.shortcuts/Update\ Gucken
```

#### Custom Font

If you want a custom font then just pace the ttf in `~/.termux/font.ttf`. Recommended fonts: [Nerd fonts](https://www.nerdfonts.com/font-downloads) (**Only use Mono fonts!**)

#### Downloads

Setup storage for downloads. (Default download location: `/data/data/com.termux/files/home/storage/movies`)

```
termux-setup-storage
```

</details>

## Features

- [x] Update checker
- [x] Language priority list
- [x] Hoster priority list
- [x] Automatically use working hoster
- [x] Browsing
  - [x] Descriptions
- [x] Watching
  - [ ] Trailer
  - [x] Automatically start next episode
  - [x] Discord Presence **Very WIP**
  - [MPV] only
    - [X] [ani-skip](https://github.com/synacktraa/ani-skip) support
    - [x] [Syncplay](https://github.com/Syncplay/syncplay) support (almost out of WIP)
    - [ ] Remember watch time **WIP**
    - [ ] Remember completed Episodes (and series)
  - [ ] Tracker support
    - [ ] [MyAnimeList](https://myanimelist.net/)
    - [ ] [AniList](https://anilist.co/)
    - [ ] [AniWorld.to] & [SerienStream.to]
- [ ] Downloading
  - [ ] Watch from download

## Provider

List of supported Anime sites

- [x] [AniWorld.to] & [SerienStream.to]
  - [ ] Filme
- [ ] [bs.to](https://bs.to/)
- [ ] [www3.streamcloud.info](https://www3.streamcloud.info/)
- [ ] [www.crunchyroll.com](https://www.crunchyroll.com)
- [ ] Add some from [International Piracy Sites German](https://fmhy.net/non-english#german-deutsch)

## Hoster

List of supported video hoster.

- [x] Streamtape
- [x] VEO
- [x] Vidoza
- [x] Doodstream

## Player

List of supported video players

- [x] [MPV] (most features, recommended)
- [x] [VLC]
- [x] [ffplay](https://www.ffmpeg.org/ffplay.html)
- [ ] Custom
- Windows
  - [x] [mpv.net](https://github.com/mpvnet-player/mpv.net)
  - [x] wmplayer.exe (fallback on Windows)
- Android
  - [x] [mpv-android](https://github.com/mpv-android/mpv-android)
  - [x] [VLC]
  - [x] Choose
- Linux (Flatpack)
  - [x] [MPV](https://flathub.org/apps/io.mpv.Mpv)
  - [x] [VLC](https://flathub.org/apps/org.videolan.VLC)
  - [x] [Celluloid](https://flathub.org/apps/io.github.celluloid_player.Celluloid)
- Linux
  - [x] [Celluloid](https://celluloid-player.github.io/)
- MacOS
  - [ ] [IINA](https://iina.io/)

## Custom CSS

**For power users only**

Place your custom CSS in `user_config_path("gucken").joinpath("custom.css")` and it will be automatically loaded by Gucken.

- [Textual CSS Guide](https://textual.textualize.io/guide/CSS/)
- [Textual CSS Reference](https://textual.textualize.io/css_types/)

## Optional dependencies

- `levenshtein` - Faster fuzzy sort/search. (with: `gucken[levenshtein]`)
- `socks` - SOCKS proxy support. (with: `gucken[socks]`)

## Todo

- [ ] Up-scaling (after download)
  - [ ] [video2x](https://github.com/k4yt3x/video2x)
  - [ ] [waifu2x](https://github.com/nagadomi/waifu2x)
  - [ ] [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
  - [ ] [FSRCNN](https://github.com/igv/FSRCNN-TensorFlow)
  - [ ] [Anime4k]
- [ ] Proxy support
  ```
  Note:
  Proxies can easiely be implented
  
  for the http client in python
  AsyncClient(proxy="http://...")
  
  for the player mpv Note: mpv dos not support socks5
  --http-proxy=<proxy>
    FFmpeg: env.http_proxy
    ytdl: --ytdl-raw-options=proxy=
  
  yt-dlp
  --proxy URL
  ```
  - [ ] [Tor](https://www.torproject.org/) as proxy
  ```
  Note:
  AniWorld.to need Cloudflare captcha and JS challange
  SerienStream.to can be bypassed by using diract ip
  
  Cloudflare captcha and JS challange can be solved by using something like
  selenium or playwright
  ```
- [ ] [MPV] Screen selection
- [ ] Custom player args
- [ ] Custom player
- [ ] Colors themes
- [ ] Installation helper
  - [ ] [MPV]
    - [ ] [Anime4k]
  - [ ] [VLC]
- [ ] Create shortcut Windows & Linux
- [ ] CI Testing (Windows, Linux)
- [ ] CD pip
- [ ] [Anime4k] options
- [ ] Modular (Custom extractors/players, API)
- [ ] Proper error handling
- [ ] Logging and Crash reports
- [ ] Pre-fetching
- [ ] Use something like opencv to time match a sub from aniworld with a high quality video form another site.
- [ ] Image preview (Kitty protocol, iterm protocol, Sixel, textual-web)
- [ ] Support textual-web
- [ ] Blacklist detection & bypass
- [ ] Mac support
- [ ] IOS support
- [ ] Update checker option to perform update
- [ ] Snap support ?
- [ ] 404 detection inside Hoster and don't crash whole program on http error + crash reports/logs
- [ ] s.to, aniworld.to scrape episode description
- [ ] search in episodes
- [ ] Focus window when ask next
- [ ] next and cancel hotkeys
- [ ] show hotkeys in Footer
- [ ] Window in settings menu to show where files are located (data, logs, config, downloads)
- [ ] Utilize next and previous buttons in mpv
- [ ] Nix
- [ ] Docker
- [ ] Flatpack ?
- [ ] Merge anime's from SerienStream.to to AniWorld.to to get more langs
- [ ] Do unescape and stripe only on render
- [ ] Dont coppy code from SerienStream.to to AniWorld.to
- [ ] BIG CODE CLEANUP
- [ ] Translation
- [ ] detect existing chapters and use them for skip
- [ ] Better settings design
- [ ] FIX TYPING SOMETIMES CAUSES CRASH
- [ ] Syncplay on Android
- [ ] More CLI args
- [ ] reverse proxy
- [ ] Chapters for VLC
- [ ] DoH support
- [ ] More threads and asyncio.gather to make everything faster
- [ ] Watchlist
- [ ] Notifications

[Anime4k]: https://github.com/bloc97/Anime4K
[MPV]: https://mpv.io/
[VLC]: https://www.videolan.org/vlc/
[AniWorld.to]: https://aniworld.to
[SerienStream.to]: https://186.2.175.5
[Python]: https://www.python.org/downloads/
[Windows Terminal]: https://apps.microsoft.com/detail/9n0dx20hk701
