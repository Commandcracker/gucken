# AniTUI

Anime Terminal User Interface

---

## Description

AniTUI is a Terminal User Interface which allows you to browse and watch your favorite anime's with style. 

## Usage

Search
![Search](.README/Search.png)
and watch
![Watch](.README/Watch.png)

## Installation

soon tm

## Features

- [x] Browsing
  - [x] Descriptions
- [x] Watching
  - [x] Automatically start next episode
  - [MPV] only
    - [X] [ani-skip](https://github.com/synacktraa/ani-skip) support (very WIP)
    - [ ] Remember watch time (WIP)
- [ ] Downloading

## Provider

List of supported Anime sites

- [x] [AniWorld.to] & [SerienStream.to]
  - [ ] Filme
  - [ ] Language Selection
  - [x] Automatically use working provider
    - [x] Streamtape
    - [x] VEO
    - [x] Vidoza
    - [x] Doodstream (only for mpv, because of http header)
- [ ] [bs.to](https://bs.to/)
- [ ] [www3.streamcloud.info](https://www3.streamcloud.info/)
- [ ] [www.crunchyroll.com](https://www.crunchyroll.com)
- [ ] Add some from [International Piracy Sites German](https://fmhy.net/non-english#german-deutsch)

## Player

List of supported video players

- [x] [MPV] (most features, recommended)
- [x] [VLC]
- [ ] ffplay
- Windows
  - [x] wmplayer.exe (fallback on Windows)
- Android
  - [ ] [mpv-android](https://github.com/mpv-android/mpv-android)
  - [ ] [VLC]
  - [ ] Choose
- Linux (Flatpack)
  -  [ ] [MPV](https://flathub.org/apps/io.mpv.Mpv)

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
- [ ] Discord Presence
- [ ] Tracker support
  - [ ] [MyAnimeList](https://myanimelist.net/)
  - [ ] [AniList](https://anilist.co/)
  - [ ] [AniWorld.to] & [SerienStream.to]
- [ ] [MPV] screen selection
- [ ] Settings (Save)
- [ ] [MPV] custom args
- [ ] Option for full screen
- [ ] Theme (Dark/Light and Colors)
- [ ] Installation helper
  - [ ] [MPV]
    - [ ] [Anime4k]
  - [ ] python
    - [ ] requirements (venv)
  - [ ] [VLC]
  - [ ] git (for automatic updating)
- [ ] CLI flags
- [ ] Testing (Windows, Linux)
- [ ] Windows, Linux Support
- [ ] [Anime4k] options
- [ ] Modular (Custom extractors, API)
- [ ] Proper error handling
- [ ] Logging and Crash reports
- [ ] Pre-fetching
- [ ] improve [ani-skip](https://github.com/synacktraa/ani-skip) support
- [ ] Support [Syncplay](https://github.com/Syncplay/syncplay)
- [ ] Use something like opencv to time match a sub from aniworld with a high quality video form another site.

[Anime4k]: https://github.com/bloc97/Anime4K
[MPV]: https://mpv.io/
[VLC]: https://www.videolan.org/vlc/
[AniWorld.to]: https://aniworld.to
[SerienStream.to]: https://186.2.175.5
