import subprocess
import sys
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"

# (base_url, marker) - marker=None wenn Status-Code reicht
LIST_PLATFORM = {
    "Github":     ("https://github.com/", None),
    "X":          ("https://x.com/", None),
    "YouTube":    ("https://www.youtube.com/@", None),
    "Snapchat":   ("https://www.snapchat.com/add/", None),
    "SoundCloud": ("https://soundcloud.com/", None),
    "Vimeo":      ("https://vimeo.com/", None),
    "Flickr":     ("https://www.flickr.com/people/", None),
    "Mixcloud":   ("https://www.mixcloud.com/", None),
    "GitLab":     ("https://gitlab.com/", None),
    "Codeberg":   ("https://codeberg.org/", None),
    "PyPI":       ("https://pypi.org/user/", None),
    "Dev.to":     ("https://dev.to/", None),
    "Medium":     ("https://medium.com/@", None),
    "Docker Hub": ("https://hub.docker.com/u/", None),
    "Keybase":    ("https://keybase.io/", None),

    "Instagram": ("https://www.instagram.com/", "Sorry, this page isn't available."),
    "Steam":     ("https://steamcommunity.com/id/", "The specified profile could not be found"),
    "Twitch":    ("https://www.twitch.tv/", "that content is unavailable"),
    "Reddit":    ("https://www.reddit.com/user/", "Sorry, nobody on Reddit goes by that name"),

    # noch unverifiziert, mit debug_diff() selbst pruefen
    "Threads":   ("https://www.threads.net/@", "Sorry, this page isn't available."),
    "Last.fm":   ("https://www.last.fm/user/", "Page Not Found"),
    "Pinterest": ("https://www.pinterest.com/", "Page not found"),
    "Telegram":  ("https://t.me/", "If you have Telegram"),  # invertiert: siehe check_current
}


def main() -> int:
    text = "   User exists in ?   "
    length = len(text)
    print("||" + "=" * length + "||")
    print(f"||{text}||")
    print("||" + "=" * length + "||" + "\n")

    try:
        username = input("|| username : ").strip()
    except EOFError:
        print("\n[-] Keine Eingabe erhalten (EOF).")
        return 1

    if not username or " " in username:
        print("[-] Ungueltiger Username.")
        return 1

    check_all(username)
    return 0


def check_all(username: str):
    print(f"\n[...] Checking for : {username}")
    for platform, (base_url, marker) in LIST_PLATFORM.items():
        check_current(platform, base_url, username, marker)

    check_tiktok(username)
    check_bluesky(username)


def fetch(url: str):
    res = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "15", "-A", USER_AGENT, "-w", "\n%{http_code}", url],
        capture_output=True,
        text=True,
        timeout=20
    )
    if res.returncode != 0:
        return None, None, res.stderr.strip() or "Unbekannter curl-Fehler"
    if "\n" not in res.stdout:
        return None, None, "Leere Antwort"
    body, status = res.stdout.rsplit("\n", 1)
    return body, status.strip(), None


def check_current(platform: str, base_url: str, username: str, marker: str = None):
    link = base_url + username
    try:
        body, status, err = fetch(link)
        if err:
            print(f"{platform} : \033[1;31m[ERROR]\033[0m {err}")
            return

        if status == "404":
            print(f"{platform} : \033[1;33m[NOT FOUND]\033[0m")
            return

        if status != "200":
            print(f"{platform} : \033[1;31m[ERROR]\033[0m HTTP {status}")
            return

        # Telegram: Marker steht NUR bei existierendem Account im Body
        if platform == "Telegram":
            if marker in body:
                print(f"{platform} : \033[1;32m[FOUND]\033[0m {link}")
            else:
                print(f"{platform} : \033[1;33m[NOT FOUND]\033[0m")
            return

        if marker is not None and marker in body:
            print(f"{platform} : \033[1;33m[NOT FOUND]\033[0m")
        else:
            print(f"{platform} : \033[1;32m[FOUND]\033[0m {link}")

    except subprocess.TimeoutExpired:
        print(f"{platform} : \033[1;31m[ERROR]\033[0m Anfrage hat zu lange gedauert")


def check_tiktok(username: str):
    link = f"https://www.tiktok.com/@{username}"
    try:
        body, status, err = fetch(link)
        if err:
            print(f"TikTok : \033[1;31m[ERROR]\033[0m {err}")
            return
        if status != "200":
            print(f"TikTok : \033[1;31m[ERROR]\033[0m HTTP {status}")
            return

        if '"statusCode":10202' in body:
            print(f"TikTok : \033[1;33m[NOT FOUND]\033[0m")
        else:
            print(f"TikTok : \033[1;32m[FOUND]\033[0m {link}")
    except subprocess.TimeoutExpired:
        print(f"TikTok : \033[1;31m[ERROR]\033[0m Anfrage hat zu lange gedauert")


def check_bluesky(username: str):
    handle = username if "." in username else f"{username}.bsky.social"
    url = f"https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={handle}"
    try:
        body, status, err = fetch(url)
        if err:
            print(f"Bluesky : \033[1;31m[ERROR]\033[0m {err}")
            return
        if status == "200":
            print(f"Bluesky : \033[1;32m[FOUND]\033[0m https://bsky.app/profile/{handle}")
        else:
            print(f"Bluesky : \033[1;33m[NOT FOUND]\033[0m")
    except subprocess.TimeoutExpired:
        print(f"Bluesky : \033[1;31m[ERROR]\033[0m Anfrage hat zu lange gedauert")


def debug_diff(base_url: str, real_username: str, fake_username: str):
    body_real, status_real, _ = fetch(base_url + real_username)
    body_fake, status_fake, _ = fetch(base_url + fake_username)

    print(f"echt   ({real_username}) status={status_real}")
    print(f"erfunden ({fake_username}) status={status_fake}")

    real_lines = set(re.findall(r'.{0,0}"[a-zA-Z0-9_]{4,}"\s*:\s*"[^"]{0,60}"', body_real or ""))
    fake_lines = set(re.findall(r'.{0,0}"[a-zA-Z0-9_]{4,}"\s*:\s*"[^"]{0,60}"', body_fake or ""))

    print("\nnur bei erfunden vorhanden (mögliche NOT-FOUND-Marker):")
    for line in sorted(fake_lines - real_lines)[:20]:
        print(f"  {line}")

    print("\nnur bei echt vorhanden (mögliche FOUND-Marker):")
    for line in sorted(real_lines - fake_lines)[:20]:
        print(f"  {line}")


if __name__ == "__main__":
    sys.exit(main())