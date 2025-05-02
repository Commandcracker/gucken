# Gucken

Project state: **Pre-Alpha**

## Description

Gucken is a Terminal User Interface which allows you to browse and watch your favorite anime's with style. 

## Usage

<img alt="Search" src="https://github.com/user-attachments/assets/bbb321d6-57a9-45cb-9029-f181957ffbc3"/>
<img alt="Watch" src="https://github.com/user-attachments/assets/53ff5d11-1032-4c1c-8f7f-8e7da8cca53e"/> 

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

- [x] VEO
- [x] Vidoza
- [x] Doodstream
- [x] SpeedFiles
- [x] Vidmoly
- [x] Streamtape (Removed from AniWorld & SerienStream)
- [x] Luluvdo
- [x] LoadX
- [x] Filemoon

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

- `speedups` (with: `gucken[speedups]`)
  - Faster fuzzy sort/search. (`levenshtein`)
  - Faster json parsing. (`orjson`)
- `socks` - SOCKS proxy support. (with: `gucken[socks]`)

## Todo

### Privacy

- [ ] Proxy support
```
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
AniWorld.to need Cloudflare captcha and JS challange
SerienStream.to can be bypassed by using diract ip
  
Cloudflare captcha and JS challange can be solved by using something like
selenium or playwright
```
- [ ] DoH support
- [ ] Reverse proxy for player
  - [ ] DoH
  - [ ] proxy

### UX

- [ ] Add hotkey to clear cache (F5)
- [ ] Translation DE, EN
- [ ] Improve settings design
- [ ] Merge SerienStream.to and AniWorld.to search results
- [ ] Focus window on autoplay popup
- [ ] Utilize next and previous buttons in mpv
- [ ] Chapters for VLC
- [ ] Window in settings menu to show where files are located (data, logs, config, downloads)
- [ ] s.to, aniworld.to scrape episode description
- [ ] Search in episodes
- [ ] Next and Cancel hotkeys
- [ ] Show hotkeys in Footer
- [ ] Create shortcut Windows & Linux
- [ ] Installation helper
  - [ ] [MPV]
    - [ ] [Anime4k]
  - [ ] [VLC]
- [ ] Colors themes

### Speedups

- [ ] Pre-fetching
- [ ] More threads and asyncio.gather to make everything faster
- [ ] More Caching
- [ ] Reuse Client

### Code

- [ ] Do unescape and stripe only on render
- [ ] Dont coppy code from SerienStream.to to AniWorld.to
- [ ] BIG CODE CLEANUP

### Features

- [ ] Update checker option to perform update
- [ ] Watchlist
- [ ] New anime/series Notifications
- [ ] Use something like opencv to time match a sub from aniworld with a high quality video form another site.
- [ ] Nix package
- [ ] Docker image
- [ ] Flatpack package
- [ ] Detect existing chapters and use them for skip
- [ ] Reverse proxy for players that do not support headers
- [ ] Up-scaling (after download)
  - [ ] [video2x](https://github.com/k4yt3x/video2x)
  - [ ] [waifu2x](https://github.com/nagadomi/waifu2x)
  - [ ] [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
  - [ ] [FSRCNN](https://github.com/igv/FSRCNN-TensorFlow)
  - [ ] [Anime4k]
- [ ] Modular (Custom extractors/players, open API)
- [ ] More CLI args
- [ ] [MPV] Screen selection
- [ ] Custom player args
- [ ] Custom player
- [ ] [Anime4k] options

#### Support

- [ ] Mac support
- [ ] IOS support
- [ ] Support textual-web
- [ ] Syncplay on Android
- [ ] Improve Flatpack support
- [ ] Improve Snap support

### Bugs & DX

- [ ] Logging and Crash reports
- [ ] Blacklist detection & bypass
- [ ] 404 detection inside Hoster and don't crash whole program on http error + crash reports/logs
- [ ] CI Testing (Windows, Linux)

[Anime4k]: https://github.com/bloc97/Anime4K
[MPV]: https://mpv.io/
[VLC]: https://www.videolan.org/vlc/
[AniWorld.to]: https://aniworld.to
[SerienStream.to]: https://186.2.175.5
[Python]: https://www.python.org/downloads/
[Windows Terminal]: https://apps.microsoft.com/detail/9n0dx20hk701
