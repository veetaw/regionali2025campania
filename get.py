import requests

BASE = "https://eleapi.interno.gov.it/siel/PX/getprefeR/DE/20251123/TE/07/RE/15/PR/072/CM/"

# agropoli: https://eleapi.interno.gov.it/siel/PX/getprefeR/DE/20251123/TE/07/RE/15/PR/072/CM/0020


def get_url(id_c):
    return BASE + str(id_c).rjust(4, '0')

payload = {}
headers = {
  'authority': 'eleapi.interno.gov.it',
  'method': 'GET',
  'path': '/siel/PX/getprefeR/DE/20251123/TE/07/RE/15/PR/072/CM/0010',
  'scheme': 'https',
  'accept': 'application/json, text/plain, */*',
  'accept-encoding': 'gzip, deflate, br, zstd',
  'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
  'dnt': '1',
  'origin': 'https://elezioni.interno.gov.it',
  'priority': 'u=1, i',
  'referer': 'https://elezioni.interno.gov.it/',
  'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
  'Cookie': 'BIGipServerpool-dait=3827199242.48129.0000'
}

import json

with open('comuni.json') as f:
    d = json.load(f)

def get_all_ids():
   return [x['cod_ente'] for x in d['enti']]

import time

if __name__ == "__main__":
    all_comuni = get_all_ids()
    for idcomune in all_comuni:
        r = requests.request("GET", get_url(idcomune), headers=headers, data=payload)
        with open(str(idcomune) + '.json', 'w') as f:
            json.dump(r.text, f)
        time.sleep(2)


