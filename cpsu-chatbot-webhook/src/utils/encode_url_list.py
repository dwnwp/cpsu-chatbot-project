import urllib.parse


def encode_urls(urls: list[str]) -> list[str]:
  encoded_urls = []

  for url in urls:
    parsed = urllib.parse.urlparse(url)

    encoded_path = urllib.parse.quote(parsed.path)

    encoded_url = urllib.parse.urlunparse(
      parsed._replace(path=encoded_path)
    )

    encoded_urls.append(encoded_url)

  return encoded_urls