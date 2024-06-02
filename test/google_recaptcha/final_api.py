from base64 import urlsafe_b64encode
from httpx import Client
from json import loads


def extract_init_args(html: str) -> str:
    start = html.find('recaptcha.anchor.Main.init("')
    if start != -1:
        start += len('recaptcha.anchor.Main.init("')
        end = html.find('");', start)
        return html[start:end]


def init_args_to_dict(init_args: str) -> dict:
    return loads(init_args.encode().decode('unicode_escape'))


def extract_token(html: str) -> str:
    start = html.find('id="recaptcha-token"')
    if start != -1:
        start = html.find('value="', start) + len('value="')
        end = html.find('"', start)
        return html[start:end]


def get_anchor_url(site_key: str, domain: str) -> str:
    co = urlsafe_b64encode(f"https://{domain}".encode()).decode().rstrip('=')
    return f"https://www.google.com/recaptcha/api2/anchor?k={site_key}&co={co}"


def get_recaptcha_token(site_key: str, domain: str) -> str:
    with Client() as client:
        response = client.get(get_anchor_url(site_key, domain))
        html = response.text
        init_args = extract_init_args(html)
        token = extract_token(html)
        print(init_args_to_dict(init_args))
        return token



"""
class AnchorURL:
    def __init__(self, site_key: str, domain: str):
        self.site_key = site_key
        self.domain = domain
        self.url = get_anchor_url(site_key, domain)
        
    



    
    @classmethod
    async def from_youtube(
            cls,
            ctx: commands.Context,
            search: str,
            logger: Logger,
            guild_data: GuildData,
            *,
            loop=None
    ):
    """






get_recaptcha_token("6Ldd07ogAAAAACktG1QNsMTcUWuwcwtkneCnPDOL", "bs.to")
