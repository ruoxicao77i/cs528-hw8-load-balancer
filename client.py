import argparse
import requests
import time
import random
from datetime import datetime
from collections import Counter
import csv

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--domain", type=str, default="localhost",
                        help="Domain to make requests to")
    parser.add_argument("-b", "--bucket", type=str, default="none",
                        help="Cloud bucket containing your files. Use none if running local")
    parser.add_argument("-w", "--webdir", type=str, default="none",
                        help="Directory containing your files. Use none if you did not make one")
    # parser.add_argument("-n", "--num_requests", type=int, default=100,
    #                     help="Number of requests to make")
    parser.add_argument("-i", "--index", type=int, default=9999,
                        help="Maximum existing file index")
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help="Server Port")
    parser.add_argument("-f", "--follow", action="store_true",
                        help="Follow Redirects")
    parser.add_argument("-s", "--ssl", action="store_true",
                        help="Use HTTPS")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print the responses from the server on stdout")
    parser.add_argument("-r", "--random", type=int, default=0,
                        help="Initial random seed")
    parser.add_argument("-t", "--timeout", type=float, default=10,
                        help="Timeout in seconds for requests")
    parser.add_argument("-o", "--output", type=str, default="client_log.csv",
                        help="CSV file to write results to")

    return parser.parse_args()

def build_base_url(args):
    scheme = "https" if args.ssl else "http"
    url = f"{scheme}://{args.domain}:{args.port}"
    if args.bucket != "none":
        url += "/" +args.bucket
    if args.webdir != "none":
        url += "/" + args.webdir
    return url

if __name__ == "__main__":
    args = parse_args()
    random.seed(args.random)
    base_url = build_base_url(args)

    zone_counts = Counter()
    error_count = 0
    total = 0

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "url", "status", "zone", "error"])

        try:
            while True:
                seq = random.randint(0, args.index)
                url = f"{base_url}/{seq}.html"
                ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                total += 1

                try:
                    r = requests.get(url, timeout=args.timeout, allow_redirects=args.follow)
                    zone = r.headers.get("X-Server-Zone", "unknown")
                    zone_counts[zone] += 1
                    print(f"[{ts}]{r.status_code} zone={zone} {url}")
                    if args.verbose:
                        print(r.text[:200])
                    writer.writerow([ts, url, r.status_code, zone, ""])
                except requests.exceptions.RequestException as e:
                    error_count += 1
                    print(f"[{ts}] ERROR {type(e).__name__} {url}")
                    writer.writerow([ts, url, "", "", type(e).__name__])

                f.flush()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n===== Summary =====")
            print(f"Total requests: {total}")
            print(f"Errors: {error_count}")
            ok = sum(zone_counts.values())
            for zone, count in zone_counts.items():
                pct = count / ok * 100 if ok else 0
                print(f"{zone}: {count} ({pct:.1f}%)")
        
        