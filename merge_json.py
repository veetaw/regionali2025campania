import json
from pathlib import Path

def merge_json_files():
    """Unisce tutti i file JSON in un unico file con una lista"""
    directory = Path('.')
    
    # Trova tutti i file .json (escludi comuni.IGNOREjson)
    json_files = sorted([f for f in directory.glob('*.json') if f.name != 'comuni.IGNOREjson'], 
                       key=lambda x: int(x.stem))
    
    print(f"Trovati {len(json_files)} file JSON da unire\n")
    
    risultati = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                risultati.append(data)
                print(f"✓ Aggiunto {json_file.name}")
        except Exception as e:
            print(f"✗ Errore con {json_file.name}: {e}")
    
    # Crea il file unificato
    output = {"ris": risultati}
    
    output_file = 'risultati_completi.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"File unificato creato: {output_file}")
    print(f"Totale comuni inclusi: {len(risultati)}")

if __name__ == "__main__":
    merge_json_files()
