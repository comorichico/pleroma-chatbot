from mastodon import Mastodon
from dotenv import load_dotenv
import os

load_dotenv()

pleroma_url = os.environ["PLEROMA_URL"]
pleroma_username = os.environ["PLEROMA_USERNAME"]
pleroma_password = os.environ["PLEROMA_PASSWORD"]
cred_file_name = 'clientcred.txt'
app_name = 'poppinwillow'

Mastodon.create_app(
    app_name,
    api_base_url = pleroma_url,
    to_file = cred_file_name
)

mastodon = Mastodon(client_id = cred_file_name,)
mastodon.log_in(
    pleroma_username,
    pleroma_password,
    to_file = cred_file_name
)