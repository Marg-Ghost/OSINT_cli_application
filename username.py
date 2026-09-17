import subprocess
import sys

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
    "TikTok": ("https://www.tiktok.com/@", "Couldn't find this account"),
    "Steam":     ("https://steamcommunity.com/id/", "The specified profile could not be found"),
    "Twitch":    ("https://www.twitch.tv/", "that content is unavailable"),
    "Reddit":    ("https://www.reddit.com/user/", "Sorry, nobody on Reddit goes by that name"),

    "Threads":   ("https://www.threads.net/@", "Sorry, this page isn't available."),  # unverifiziert
    "Bluesky":   ("https://bsky.app/profile/", "Profile not found"),  # unverifiziert
    "Last.fm":   ("https://www.last.fm/user/", "Page Not Found"),  # unverifiziert
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


def check_current(platform: str, base_url: str, username: str, marker: str = None):
    link = base_url + username
    try:
        res = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "15", "-A", USER_AGENT, "-w", "\n%{http_code}", link],
            capture_output=True,
            text=True,
            timeout=20
        )

        if res.returncode != 0:
            detail = res.stderr.strip() or "Unbekannter curl-Fehler"
            print(f"{platform} : \033[1;31m[ERROR]\033[0m {detail}")
            return

        if "\n" not in res.stdout:
            print(f"{platform} : \033[1;31m[ERROR]\033[0m Leere Antwort")
            return

        body, status = res.stdout.rsplit("\n", 1)
        status = status.strip()

        if status == "404":
            print(f"{platform} : \033[1;33m[NOT FOUND]\033[0m")
            return

        if status != "200":
            print(f"{platform} : \033[1;31m[ERROR]\033[0m HTTP {status}")
            return

        if marker is not None and marker in body:
            print(f"{platform} : \033[1;33m[NOT FOUND]\033[0m")
        else:
            print(f"{platform} : \033[1;32m[FOUND]\033[0m {link}")

    except subprocess.TimeoutExpired:
        print(f"{platform} : \033[1;31m[ERROR]\033[0m Anfrage hat zu lange gedauert")


if __name__ == "__main__":
    sys.exit(main())