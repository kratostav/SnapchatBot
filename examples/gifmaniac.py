import time, tempfile, subprocess, re, schedule
from argparse import ArgumentParser
from snapchat_agents import SnapchatAgent, Snap
from lxml.html import parse

def grab_trending_gif_urls():
    doc = parse("http://giphy.com").getroot()
    els = doc.cssselect(".gif-link img")[:10]
    ret = []
    for el in els:
        ret.append("http:" +re.sub(r"\/([^./])*\.gif", "/giphy.gif", el.attrib['src']))
    return ret

def gif_to_video(url):
    f = tempfile.NamedTemporaryFile(suffix=".mp4", delete = False)
    code = subprocess.Popen(["/bin/sh", "scripts/gif_to_mp4.sh", url, f.name]).wait()
    print code
    return f.name

def is_valid_video(filename):
    return subprocess.Popen(["ffprobe", filename]).wait() == 0

class GIFManiacAgent(SnapchatAgent):
    def run(self):
        def post_gifs():
            urls = grab_trending_gif_urls()
            filenames = map(gif_to_video, urls)

            for filename in filter(is_valid_video, filenames):
                if not is_valid_video(filename): continue
                self.post_story(Snap.from_file(filename))

        post_gifs()
        schedule.every().day.at("10:30").do(post_gifs)

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    parser = ArgumentParser("GIF Maniac Agent")
    parser.add_argument('-u', '--username', required = True, type=str, help = "Username of the account to run the agent on")
    parser.add_argument('-p', '--password', required = True, type=str, help = "Password of the account to run the agent on")

    args = parser.parse_args()

    agent = GIFManiacAgent(args.username, args.password)
    agent.run()
