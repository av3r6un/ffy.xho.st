from dataclasses import asdict, dataclass
from typing import List


class YtFormat:
  filesize: int = None
  id: str = None
  note: str = None
  quality: int = None
  url: str = None
  ext: str = None
  vcodec: str = None
  acodec: str = None
  abr: float = None
  vbr: float = None
  quality: float = None
  resolution: str = None
  
  def __init__(self, filesize_approx, format_id, quality, format_note, url, ext, vcodec, acodec, abr, vbr, **kwargs) -> None:
    self.filesize = filesize_approx
    self.id = format_id
    self.note = format_note
    self.quality = quality
    self.url = url
    self.ext = ext
    self.vcodec = None if vcodec == "none" else vcodec
    self.acodec = None if acodec == "none" else acodec
    self.abr = abr
    self.vbr = vbr
    self.height = kwargs.get('height')
    self.width = kwargs.get('width')
    self.fps = kwargs.get('fps')
    self.tbr = kwargs.get('tbr')
    self.asr = kwargs.get('asr')
    self.audio_channels = kwargs.get('audio_channels')
    self.http_headers = kwargs.get('http_headers') or {}
  
  def __str__(self):
    return f'ID: {self.id} | {self.note} | {int(self.filesize / 1024 / 1024)}MB | {self.quality}'
  
  @property
  def json(self):
    return dict(
      id=self.id,
      note=self.note,
      extension=self.ext,
      filesize=self.filesize,
      codec=self.vcodec if self.vcodec else self.acodec,
    )

  @property
  def detailed(self):
    media_type = 'video' if self.vcodec else 'audio'
    extension = 'mp4' if self.ext == 'm4a' else self.ext
    return dict(
      id=self.id,
      type=media_type,
      frameRate=self.fps,
      quality=self.note,
      mimeType=f'{media_type}/{extension}',
      codecs=self.vcodec if self.vcodec else self.acodec,
      bandwidth=max(1, round((self.tbr or self.vbr or self.abr or 1) * 1000)),
      width=self.width,
      height=self.height,
      audioSamplingRate=self.asr,
      audioChannels=self.audio_channels,
    )


class YtFormats(List[YtFormat]):
  def __init__(self, *args):
    for arg in args:
      self.append(YtFormat(**arg))
  
  def __getitem__(self, id):
    for item in self:
      if item.id == id:
        return item
    return None
  
  @property
  def videos(self):
    return [a.detailed for a in self if a.vcodec and not a.acodec and a.ext == 'mp4']
  
  @property
  def json(self):
    return [a.json for a in self if a.vcodec and not a.acodec and a.ext == 'mp4']


class YtChannel:
  name: str
  uploader_id: str
  uploader_url: str
  followers: int = 0
  verified: bool = False
  
  def __init__(self, channel, **kwargs) -> None:
    self.name = channel
    self.uploader_id = kwargs.get('uploader_id')
    self.uploader_url = kwargs.get('uploader_url')
    self.followers = kwargs.get('channel_follower_count')
    self.verified = kwargs.get('channel_is_verified')

  @property
  def json(self):
    return dict(name=self.name, uploader_url=self.uploader_url, followers=self.followers, verified=self.verified)


@dataclass
class YtChapter:
  start_time: int
  title: str
  end_time: int
  
  @property
  def json(self):
    return asdict(self)


class YtChapters(List[YtChapter]):
  def __init__(self, *args):
    for arg in args:
      self.append(YtChapter(**arg))
  
  @property
  def json(self):
    return [a.json for a in self]


class YtMedia:
  id: str
  formats: YtFormats
  title: str
  thumbnail: str
  categories: list = []
  duration: int
  likes: int
  views: int
  channel: YtChannel
  uploaded: int
  language: str = None
  description: str = None
  chapters: YtChapters | None = None

  def __init__(self, id, title, formats, thumbnails, duration, categories, chapters,
    like_count, view_count, channel, uploader_id, timestamp, fulltitle, **kwargs
  ):
    self.id = id
    self.thumbnails = thumbnails
    self.title = fulltitle or title
    self.formats = self._create_formats(formats)
    self.description = kwargs.get('description')
    self.categories = categories
    self.duration = duration
    self.likes = like_count
    self.views = view_count
    self.uploaded = timestamp
    self.language = kwargs.get('language')
    self.channel = YtChannel(channel, uploader_id=uploader_id, **kwargs)
    self.chapters = YtChapters(*chapters) if chapters else None

  @property
  def highest_thumbnail(self):
    return max(
      (t for t in self.thumbnails if 'resolution' in t),
      key=lambda t: (t['width'], t['height']), default=None
    )['url']

  @property
  def json(self):
    resp = dict(
      id=self.id, thumbnail=self.highest_thumbnail, title=self.title, description=self.description,
      categories=self.categories, duration=self.duration, likes=self.likes, views=self.views,
      uploaded=self.uploaded, channel=self.channel.json, chapters=self.chapters.json if self.chapters else None, language=self.language
    )
    return resp

  @staticmethod
  def _create_formats(formats):
    fmts = []
    for format in formats:
      if format.get('filesize_approx', None) \
        and format.get('quality', None)\
          and format.get('resolution', None):
        fmts.append(format)
    return YtFormats(*fmts)
