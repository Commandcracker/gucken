# Gucken

## Description

Gucken is a Terminal User Interface which allows you to browse and watch your favorite anime's with style. 

## Usage

Search
![Search](.README/Search.png)
and watch
![Watch](.README/Watch.png)

## Installation

### Windows

Install [Python] and if you are **on Windows 10** [Windows Terminal] for a better experience.

```
pip install gucken
gucken
```

### Linux

Install [Python] and then

```
pip install gucken
gucken
```

### Android

Install [Termux](https://termux.dev/en/) and run:

```
pkg update -y
pkg upgrade -y
pkg install python ffmpeg -y
pip install gucken
gucken
```

#### Optional

Setup storage for downloads.

```
termux-setup-storage
```

## Features

- [x] Browsing
  - [x] Descriptions
- [x] Watching
  - [x] Automatically start next episode
  - [ ] Discord Presence
  - [MPV] only
    - [X] [ani-skip](https://github.com/synacktraa/ani-skip) support (very WIP)
    - [x] [Syncplay](https://github.com/Syncplay/syncplay) support
    - [ ] Remember watch time (WIP)
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
  - [ ] Language Selection
  - [x] Automatically use working provider
    - [x] Streamtape
    - [x] VEO
    - [x] Vidoza
    - [x] Doodstream
- [ ] [bs.to](https://bs.to/)
- [ ] [www3.streamcloud.info](https://www3.streamcloud.info/)
- [ ] [www.crunchyroll.com](https://www.crunchyroll.com)
- [ ] Add some from [International Piracy Sites German](https://fmhy.net/non-english#german-deutsch)

## Player

List of supported video players

- [x] [MPV] (most features, recommended)
- [x] [VLC]
- [x] [ffplay](https://www.ffmpeg.org/ffplay.html)
- [ ] [Elisa](https://apps.kde.org/elisa/)
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

## Todo

- [ ] Up-scaling (after download)
  - [ ] [video2x](https://github.com/k4yt3x/video2x)
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
- [ ] Save settings
- [ ] Custom player args
- [ ] Custom player
- [ ] Colors themes
- [ ] Installation helper
  - [ ] [MPV]
    - [ ] [Anime4k]
  - [ ] [VLC]
- [ ] Create shortcut Windows & Linux 
- [ ] Update checking and updating using pip
- [ ] CLI args
- [ ] CI Testing (Windows, Linux)
- [ ] CD pip
- [ ] [Anime4k] options
- [ ] Modular (Custom extractors/players, API)
- [ ] Proper error handling
- [ ] Logging and Crash reports
- [ ] Pre-fetching
- [ ] improve [ani-skip](https://github.com/synacktraa/ani-skip) support
- [ ] Use something like opencv to time match a sub from aniworld with a high quality video form another site.
- [ ] Image preview
- [ ] Blacklist detection & bypass
- [ ] Syncplay on Android
- [ ] Mac support
- [ ] IOS support

[Anime4k]: https://github.com/bloc97/Anime4K
[MPV]: https://mpv.io/
[VLC]: https://www.videolan.org/vlc/
[AniWorld.to]: https://aniworld.to
[SerienStream.to]: https://186.2.175.5
[Python]: https://www.python.org/downloads/
[Windows Terminal]: https://apps.microsoft.com/detail/9n0dx20hk701
