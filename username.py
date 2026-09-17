import subprocess


def main() -> int:
    text = "   User exists in ?   "
    length = len(text)
    print("||" + "=" * length + "||")
    print(f"||{text}||")
    print("||" + "=" * length + "||"+"\n")

    username = input("|| username : ")
    
    check_all(username)

    return 0

def check_all (username : str):
    print(f"\n[...] Checking for : {username}")
    list_platform = {
        "Github": "https://github.com/",
        "Reddit": "https://www.reddit.com/user/",
        "Instagram": "https://www.instagram.com/",
        "TikTok": "https://www.tiktok.com/@",
        "X": "https://x.com/",
        "Steam": "https://steamcommunity.com/id/",
        "Facebook": "https://www.facebook.com/",
        "LinkedIn": "https://www.linkedin.com/in/",
        "YouTube": "https://www.youtube.com/@",
        "Snapchat": "https://www.snapchat.com/add/",
        "Threads": "https://www.threads.net/@",
        "Bluesky": "https://bsky.app/profile/",
        "Pinterest": "https://www.pinterest.com/",
        "Twitch": "https://www.twitch.tv/",
        "Telegram": "https://t.me/",
        "SoundCloud": "https://soundcloud.com/",
        "Vimeo": "https://vimeo.com/",
        "Flickr": "https://www.flickr.com/people/",
        "Last.fm": "https://www.last.fm/user/",
        "Mixcloud": "https://www.mixcloud.com/",
    }

    for platform, base_url in list_platform.items():
        check_current(platform, base_url, username)

def check_current(platform: str, base_url: str, username: str):
    link = base_url + username
    try:
        res = subprocess.run(
                    ["curl", "-sS", "-L", "--max-time", "15", "-w", "\n%{http_code}", link],
                    capture_output=True, 
                    text=True,
                    timeout=20
                )

        if res.returncode != 0:
            detail = res.stderr.strip() or "Unbekannter curl-Fehler"
            print(f"{platform} : \033[1;31m[ERROR]\033[0m {detail}")
            return

        _, status = res.stdout.rsplit("\n", 1)
        if status == "200":
            print(f"{platform} : \033[1;32m[FOUND]\033[0m {link}")
        elif status == "404":
            print(f"{platform} : \033[1;33m[NOT FOUND]\033[0m")
        else:
            print(f"{platform} : \033[1;31m[ERROR]\033[0m HTTP {status}")
    except subprocess.TimeoutExpired:
        print(f"{platform} : \033[1;31m[ERROR]\033[0m Anfrage hat zu lange gedauert")

if __name__ == "__main__":
    main()