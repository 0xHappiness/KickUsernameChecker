import tls_client
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

def check_username_kick(username):
    session = tls_client.Session(
        client_identifier="chrome120",
        random_tls_extension_order=True
    )

    url = "https://kick.com/api/v1/signup/verify/username"
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip",
        "accept-language": "en-US",
        "connection": "Keep-Alive",
        "content-type": "application/json",
        "host": "kick.com",
        "user-agent": "okhttp/4.9.2",
        "x-kick-app-p-os": "android",
        "x-kick-app-p-v": "34",
        "x-kick-app-v": "1.48.0",
    }

    response = session.post(url, headers=headers, json={"username": username})

    if response.text.strip() == "":
        print(f"[AVAILABLE]  '{username}' is available.")
        with open("available.txt", "a") as f:
            f.write(username + "\n")
        return username, True
    else:
        print(f"[TAKEN]      '{username}' is taken.")
        return username, False

def load_usernames_from_file(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] File '{filename}' not found.")
        return []

def main(thread_count):
    usernames = load_usernames_from_file("usernames.txt")
    max_workers = thread_count

    available_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_username_kick, u) for u in usernames]

        for future in as_completed(futures):
            try:
                _, is_available = future.result()
                if is_available:
                    available_count += 1
            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")

    print(f"\nChecked {len(usernames)} usernames, found {available_count} available.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kick.com username availability checker")
    parser.add_argument("-t", "--threads", type=int, default=10,
                        help="Number of concurrent threads (default: 10)")
    args = parser.parse_args()

    main(args.threads)
