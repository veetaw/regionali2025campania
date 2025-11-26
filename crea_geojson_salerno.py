import json

# Carica il GeoJSON della Campania
with open('campania.geojson', 'r', encoding='utf-8') as f:
    campania_data = json.load(f)

# Carica i risultati elettorali
with open('risultati_completi.json', 'r', encoding='utf-8') as f:
    risultati_data = json.load(f)

# Crea un dizionario dei comuni con risultati elettorali
comuni_risultati = {}
for comune_res in risultati_data['ris']:
    nome_comune = comune_res['int']['desc_com']
    comuni_risultati[nome_comune.upper()] = comune_res

# Filtra solo i comuni della provincia di Salerno (COD_PROV = 65)
# e abbina i risultati elettorali
salerno_features = []

for feature in campania_data:
    if feature['properties']['COD_PROV'] == 65:
        nome_comune = feature['properties']['COMUNE'].upper()
        
        # Cerca il comune nei risultati
        comune_ris = None
        
        # Prova match esatto
        if nome_comune in comuni_risultati:
            comune_ris = comuni_risultati[nome_comune]
        else:
            # Prova match parziale
            for nome_ris in comuni_risultati.keys():
                if nome_comune in nome_ris or nome_ris in nome_comune:
                    comune_ris = comuni_risultati[nome_ris]
                    break
        
        if comune_ris:
            # Aggiungi i dati elettorali alle properties
            feature['properties']['elettorale'] = {
                'cod_com': comune_ris['int']['cod_com'],
                'desc_com': comune_ris['int']['desc_com'],
                'candidati': [],
                'presidenti': {}
            }
            
            # Mappa liste -> presidente
            presidenti_map = {
                'Roberto Fico': [
                    'PARTITO DEMOCRATICO',
                    'MOVIMENTO 5 STELLE',
                    'ALLEANZA VERDI E SINISTRA',
                    'ROBERTO FICO PRESIDENTE',
                    'A TESTA ALTA',
                    'NOI DI CENTRO',
                    'NOI SUD',
                    'MASTELLA',
                    'AVANTI CAMPANIA',
                    'CASA RIFORMISTA'
                ],
                'Edmondo Cirielli': [
                    'FRATELLI D\'ITALIA',
                    'GIORGIA MELONI',
                    'FORZA ITALIA',
                    'PPE FORZA ITALIA',
                    'LEGA',
                    'CIRIELLI PRESIDENTE',
                    'NOI MODERATI',
                    'UNIONE DI CENTRO',
                    'DEMOCRAZIA CRISTIANA',
                    'ROTONDI',
                    'PENSIONATI',
                    'CONSUMATORI'
                ],
                'Giuliano Granato': [
                    'CAMPANIA POPOLARE',
                    'GIULIANO GRANATO'
                ],
                'Nicola Campanile': [
                    'PER NICOLA CAMPANILE',
                    'PER LE PERSONE',
                    'PER LA COMUNITA'
                ],
                'Carlo Arnese': [
                    'FORZA DEL POPOLO'
                ],
                'Stefano Bandecchi': [
                    'DIMENSIONE BANDECCHI',
                    'BANDECCHI'
                ]
            }
            
            # Calcola voti per presidente
            for presidente, keywords in presidenti_map.items():
                voti_presidente = 0
                for lista in comune_ris['liste']:
                    for keyword in keywords:
                        if keyword in lista['desc'].upper():
                            # Somma i voti dei candidati di questa lista
                            voti_lista = sum(c['voti'] for c in comune_ris['cand'] 
                                           if c['cod_lis'] == lista['cod'])
                            voti_presidente += voti_lista
                            break
                
                if voti_presidente > 0:
                    feature['properties']['elettorale']['presidenti'][presidente] = voti_presidente
            
            # Aggiungi tutti i candidati con i loro voti
            for candidato in comune_ris['cand']:
                if candidato['voti'] > 0:  # Solo candidati con voti
                    nome_completo = f"{candidato['cogn']} {candidato['nome']}"
                    if candidato['a_nome']:
                        nome_completo += f" {candidato['a_nome']}"
                    
                    # Trova il nome della lista
                    nome_lista = None
                    for lista in comune_ris['liste']:
                        if lista['cod'] == candidato['cod_lis']:
                            nome_lista = lista['desc']
                            break
                    
                    feature['properties']['elettorale']['candidati'].append({
                        'nome': nome_completo,
                        'voti': candidato['voti'],
                        'lista': nome_lista,
                        'sesso': candidato['sex'],
                        'luogo_nascita': candidato['l_nasc']
                    })
            
            # Ordina i candidati per voti
            feature['properties']['elettorale']['candidati'].sort(
                key=lambda x: x['voti'], 
                reverse=True
            )
        
        salerno_features.append(feature)

# Crea il GeoJSON finale
salerno_geojson = {
    "type": "FeatureCollection",
    "features": salerno_features
}

# Salva il file
with open('salerno_candidati.geojson', 'w', encoding='utf-8') as f:
    json.dump(salerno_geojson, f, ensure_ascii=False, indent=2)

print(f"✓ Creato salerno_candidati.geojson con {len(salerno_features)} comuni")
print(f"✓ Comuni con dati elettorali: {sum(1 for f in salerno_features if 'elettorale' in f['properties'])}")
