import subprocess
import sys
import json
from urllib.parse import quote

def main() -> int:
    text = "   Have I been Pwned   "
    length = len(text)
    print("||" + "=" * length + "||")
    print(f"||{text}||")
    print("||" + "=" * length + "||"+"\n")

    email_adresse = input("|| Email : ")
    if "@" not in email_adresse or "." not in email_adresse.rsplit("@", 1)[-1]:
        print("[-] Ungültige oder unvollständige E-Mail-Adresse.")
        return
    
    email_pawned_check_xpose(email_adresse)

    return 0

def email_pawned_check_xpose(email: str):
    print(f"\n[...] Checking for : {email}")

    url = f"https://api.xposedornot.com/v1/check-email/{quote(email, safe='')}"

    try:
        res = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "15", "-w", "\n%{http_code}", url],
            capture_output=True, 
            text=True,
            timeout=20
        )

        if res.returncode != 0:
            detail = res.stderr.strip() or "Unbekannter curl-Fehler"
            print(f"[-] API nicht erreichbar: {detail}")
            return

        body, status = res.stdout.rsplit("\n", 1)
        
        if not status.startswith("2"):
            print(f"[-] API-Fehler (HTTP {status}). Kein sicherer CLEAN-Befund.")
            return

        if not body.strip():
            print("[-] API hat keine Daten geliefert. Kein sicherer CLEAN-Befund.")
            return

        data = json.loads(body)

        if data.get("Error") == "Not found":
            print(f"\033[1;32m[CLEAN]\033[0m Keine bekannten Leaks für '{email}' gefunden.")
            return

        if "Error" in data:
            print(f"[-] API konnte '{email}' nicht prüfen: {data['Error']}")
            return

        if "breaches" in data and data["breaches"]:
            breaches = data["breaches"][0]
            print(f"\033[1;31m[PWNED]\033[0m E-Mail in {len(breaches)} Data-Breaches gefunden:\n")
            for b in breaches:
                print(f"  \033[1;33m-\033[0m {b}")
        else:
            print(f"\033[1;32m[CLEAN]\033[0m Keine Leaks gefunden.")

    except (json.JSONDecodeError, ValueError):
        print("[-] Fehler beim Parsen der API-Antwort.")
    except subprocess.TimeoutExpired:
        print("[-] API-Anfrage hat zu lange gedauert. Kein sicherer CLEAN-Befund.")
    except Exception as e:
        print(f"[-] Verbindungsfehler: {e}")

if __name__ == "__main__":
    main()