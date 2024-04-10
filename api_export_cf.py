import requests
import sys

def get_all_zones(auth_email, auth_key):
    zones = []
    page = 1
    while True:
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones?page={page}",
            headers={"X-Auth-Key": auth_key, "X-Auth-Email": auth_email}
        )
        data = response.json()
        if 'result' not in data or not data['result']:
            break
        zones.extend(data['result'])
        page += 1
    return zones

def get_dns_records_for_zone(zone_id, auth_email, auth_key):
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
        headers={"X-Auth-Key": auth_key, "X-Auth-Email": auth_email}
    )
    data = response.json()
    return data.get('result', [])

def main():
    auth_email = "ENTER_ACCOUNT_EMAIL"
    auth_key = " ENTER_Global_API_Key"

    # File opening for results record
    with open("cloudflare_dns_records.csv", "w") as f:
        f.write("Domain,A,CNAME,MX,TXT,Other\n")

    zones = get_all_zones(auth_email, auth_key)
    total_zones = len(zones)
    for i, zone in enumerate(zones, start=1):
        zone_name = zone['name']
        sys.stdout.write(f"\rProcessing zone {i}/{total_zones}: {zone_name} {'.' * (i % 4)}")
        sys.stdout.flush()

        zone_id = zone['id']
        dns_records = get_dns_records_for_zone(zone_id, auth_email, auth_key)

        a_records = [(record['name'], record['content']) for record in dns_records if record['type'] == 'A']
        cnames = [(record['name'], record['content']) for record in dns_records if record['type'] == 'CNAME']
        mx_records = [record['content'] for record in dns_records if record['type'] == 'MX']
        txt_records = [record['content'] for record in dns_records if record['type'] == 'TXT']
        other_records = [(record['type'], record['content']) for record in dns_records if record['type'] not in ['A', 'CNAME', 'MX', 'TXT']]

        with open("cloudflare_dns_records.csv", "a") as f:
            f.write(f"{zone_name},")
            f.write(','.join([f"{a[0]}:{a[1]}" for a in a_records]) + ",")
            f.write(','.join([f"{cname[0]}:{cname[1]}" for cname in cnames]) + ",")
            f.write(','.join(mx_records) + ",")
            f.write(','.join(txt_records) + ",")
            f.write(','.join([f"{other[0]}:{other[1]}" for other in other_records]))
            f.write("\n")

    print("\nDone. Results saved in cloudflare_dns_records.csv")

if __name__ == "__main__":
    main()
