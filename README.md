# RSSDownloader

A simple Python script to download `.torrent` files from an RSS Feed. It's do not download the content. History is kept to prevent multiple download of files.

> To bypass a Cloudfare protected RSS, I used [Jackett](https://github.com/Jackett/Jackett) and [FlareSolver](https://github.com/FlareSolverr/FlareSolverr).


## Usage

```shell
pip install -r requirements.txt
python main.py
```

## Configuation

Create a ``config.yaml`` file containing the following :

```yaml
appName: RSSDownloader

config:
  historyFolder: history
  torrentFolder: download
  movieListReferenceSkip: movieListReferenceSkip.txt
  notOlderThan: "Sat, 01 Jan 2022 00:00:00 +0200"
  notOlderThanFormat: "%a, %d %b %Y %H:%M:%S %z"

  rss:
    - name: YggTorrent-Slay3R
      url: https://jackett.myserver.fr/api/v2.0/indexers/yggtorrent/results/torznab/api?apikey=apikey&t=search&cat=102183&q=1080p+x264+Slay3R
    - name: YggTorrent-JiHeFF
      url: https://jackett.myserver.fr/api/v2.0/indexers/yggtorrent/results/torznab/api?apikey=apikey&t=search&cat=102183&q=1080p+x264+JiHeFF
    - name: Science & Vie 
      url: https://jackett.myserver.fr/api/v2.0/indexers/yggtorrent/results/torznab/api?apikey=apikey&t=search&cat=102156&q=Science+%26+Vie+2021
      filter: Science & Vie - (Janvier|Fevrier|Février|Mars|Avril|Mai|Juin|Juillet|Aout|Août|Septembre|Octobe|Novembre|Decembre|Décembre) [0-9]{4} Pdf

```

Folders :

 - historyFolder: download history per feed. 
 - torrentFolder: contain all `.torrent` files downloaded.

Time limit :
- notOlderThan: items older than this will not be grabbed
- notOlderThanFormat: format of item published date

Definition of RSS feeds:

  - name : name to identify the URL RSS feed
  - URL : RSS feed URL
  - filter : filter regex on **title** attribute of each entry
