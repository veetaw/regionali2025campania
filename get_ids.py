import json

with open('comuni.json') as f:
    d = json.load(f)

def get_all_ids():
   return [x['cod_ente'] for x in d['enti']]


if __name__ == "__main__":
    a = get_all_ids()
    print(a, len(a), sep="\n")
