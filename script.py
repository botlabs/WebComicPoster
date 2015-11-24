import praw
import requests
from lxml import html

# Account settings (private)
USERNAME = ""
PASSWORD = ""

# OAuth settings (private)
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Settings
USER_AGENT = "r/theatheistpig comic poster"
AUTH_TOKENS = ["identity", "submit", "read"]
SUBREDDIT = "theatheistpig"
SITE_URL = "http://theatheistpig.com/"
XPATH_IMG_URL = '//div[@class="comic-content"]/p/a/img/@src'
XPATH_TITLE   = '//h1[@class="comic-title"]/a/text()'


def get_access_token():
    response = requests.post("https://www.reddit.com/api/v1/access_token",
      auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
      data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD},
      headers = {"User-Agent": USER_AGENT})
    response = dict(response.json())
    return response["access_token"]

def get_praw():
    r = praw.Reddit(USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    r.set_access_credentials(set(AUTH_TOKENS), get_access_token())
    return r

def main(r):

    open("posted.txt", 'a').close()
    with open("posted.txt") as f:
        posted_photos = f.read().split("\n")

    try:
        home_resp = requests.get(SITE_URL)
        home_tree = html.fromstring(home_resp.text)
        img_url = home_tree.xpath(XPATH_IMG_URL)[0]
        title = home_tree.xpath(XPATH_TITLE)[0]

        if img_url in posted_photos:
            exit("Already posted photo " + img_url)
        else:
            posted_photos.append(img_url + "\n")

        r.submit(SUBREDDIT, title, url=img_url)

        with open("posted.txt", 'w') as f:
            f.write(''.join(i + "\n" for i in posted_photos))


    except praw.errors.OAuthInvalidToken:
        print("Token is invalid, getting new one...")
        r.set_access_credentials(set(AUTH_TOKENS), get_access_token())


if __name__ == "__main__":
    main(get_praw())
