import json
import os
from pathlib import Path

def unescape_json_file(filepath):
    """Legge un file JSON escaped e lo salva in formato corretto"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rimuove le virgolette iniziali e finali se presenti
        content = content.strip()
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        
        # Fa l'unescape della stringa JSON
        unescaped = content.encode('utf-8').decode('unicode_escape')
        
        # Verifica che sia un JSON valido
        json_data = json.loads(unescaped)
        
        # Salva il file con indentazione corretta
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    # Directory corrente
    directory = Path('.')
    
    # Trova tutti i file .json (escludi comuni.IGNOREjson)
    json_files = [f for f in directory.glob('*.json') if f.name != 'comuni.IGNOREjson']
    
    print(f"Trovati {len(json_files)} file JSON da processare\n")
    
    successi = 0
    errori = 0
    
    for json_file in sorted(json_files):
        success, error = unescape_json_file(json_file)
        if success:
            print(f"✓ {json_file.name}")
            successi += 1
        else:
            print(f"✗ {json_file.name}: {error}")
            errori += 1
    
    print(f"\n{'='*50}")
    print(f"Completato!")
    print(f"Successi: {successi}")
    print(f"Errori: {errori}")

if __name__ == "__main__":
    main()
