from urllib.parse import urljoin

class BaseFetcher:
    def __init__(self, client, company, board_url): self.client, self.company, self.board_url = client, company, board_url
    def fetch(self): raise NotImplementedError
    def link(self, href): return urljoin(self.board_url, href)
