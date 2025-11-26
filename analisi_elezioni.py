import json
from collections import defaultdict
import re

class AnalizzatoreElezioni:
    def __init__(self, file_path='risultati_completi.json'):
        """Carica i dati delle elezioni"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.comuni = data['ris']
        
        # Mappa i presidenti dalle liste
        self.candidati_presidente = self._identifica_presidenti()
    
    def _identifica_presidenti(self):
        """Identifica i candidati presidente dai nomi delle liste"""
        presidenti = {}
        
        # Pattern comuni per identificare i presidenti
        patterns = {
            'CIRIELLI': ['CIRIELLI PRESIDENTE', 'LEGA - CIRIELLI', 'PENSIONATI CONSUMATORI - CIRIELLI',
                        'NOI MODERATI - CIRIELLI', 'GIORGIA MELONI PER CIRIELLI'],
            'FICO': ['ROBERTO FICO PRESIDENTE'],
            'CAMPANILE': ['PER NICOLA CAMPANILE PRESIDENTE'],
            'GRANATO': ['CAMPANIA POPOLARE - GIULIANO GRANATO PRESIDENTE'],
            'BANDECCHI': ['DIMENSIONE BANDECCHI'],
            'MASTELLA': ['MASTELLA NOI DI CENTRO NOI SUD'],
            'ALTRI': ['A TESTA ALTA', 'CASA RIFORMISTA', 'FORZA DEL POPOLO', 'AVANTI CAMPANIA']
        }
        
        # Crea una mappa inversa: nome lista -> presidente
        for presidente, liste_keywords in patterns.items():
            for keyword in liste_keywords:
                presidenti[keyword] = presidente
        
        return presidenti
    
    def _associa_lista_a_presidente(self, nome_lista):
        """Associa una lista al suo candidato presidente"""
        nome_lista_upper = nome_lista.upper()
        
        for keyword, presidente in self.candidati_presidente.items():
            if keyword in nome_lista_upper:
                return presidente
        
        # Se non trova corrispondenza, prova con pattern più generici
        if 'CIRIELLI' in nome_lista_upper:
            return 'CIRIELLI'
        elif 'FICO' in nome_lista_upper:
            return 'FICO'
        elif 'CAMPANILE' in nome_lista_upper:
            return 'CAMPANILE'
        elif 'GRANATO' in nome_lista_upper:
            return 'GRANATO'
        elif 'BANDECCHI' in nome_lista_upper:
            return 'BANDECCHI'
        elif 'MASTELLA' in nome_lista_upper:
            return 'MASTELLA'
        
        return 'ALTRI/NON CLASSIFICATO'
    
    def trova_comune(self, nome_comune):
        """Trova i dati di un comune per nome"""
        nome_comune_upper = nome_comune.upper()
        
        for comune in self.comuni:
            if comune['int']['desc_com'].upper() == nome_comune_upper:
                return comune
        
        # Ricerca parziale se non trova corrispondenza esatta
        risultati = []
        for comune in self.comuni:
            if nome_comune_upper in comune['int']['desc_com'].upper():
                risultati.append(comune)
        
        if len(risultati) == 1:
            return risultati[0]
        elif len(risultati) > 1:
            print(f"⚠️  Trovati {len(risultati)} comuni simili:")
            for i, c in enumerate(risultati, 1):
                print(f"  {i}. {c['int']['desc_com']}")
            return None
        
        return None
    
    def analizza_comune(self, nome_comune):
        """Analizza i risultati elettorali di un comune"""
        comune = self.trova_comune(nome_comune)
        
        if not comune:
            return f"❌ Comune '{nome_comune}' non trovato"
        
        info = comune['int']
        liste = comune['liste']
        candidati = comune['cand']
        
        # Organizza i dati per presidente
        voti_per_presidente = defaultdict(lambda: {
            'voti_lista': 0,
            'voti_preferenze': 0,
            'liste': [],
            'candidati_top': []
        })
        
        # Calcola voti per lista e associa ai presidenti
        for lista in liste:
            presidente = self._associa_lista_a_presidente(lista['desc'])
            
            # Calcola voti lista (somma voti candidati della lista)
            voti_lista = sum(c['voti'] for c in candidati if c['cod_lis'] == lista['cod'])
            
            voti_per_presidente[presidente]['voti_lista'] += voti_lista
            voti_per_presidente[presidente]['liste'].append({
                'nome': lista['desc'],
                'voti': voti_lista
            })
        
        # Trova i candidati più votati per ogni lista/presidente
        for presidente, dati in voti_per_presidente.items():
            # Trova le liste associate a questo presidente
            cod_liste = [l['cod'] for l_item in liste 
                        if self._associa_lista_a_presidente(l_item['desc']) == presidente 
                        for l in [l_item]]
            
            # Trova i top candidati di queste liste
            cand_presidente = [c for c in candidati if c['cod_lis'] in cod_liste and c['voti'] > 0]
            cand_presidente.sort(key=lambda x: x['voti'], reverse=True)
            
            dati['candidati_top'] = cand_presidente[:5]  # Top 5
            dati['voti_preferenze'] = sum(c['voti'] for c in cand_presidente)
        
        # Ordina i presidenti per voti totali
        presidenti_ordinati = sorted(
            voti_per_presidente.items(),
            key=lambda x: x[1]['voti_lista'],
            reverse=True
        )
        
        # Formatta il risultato
        risultato = []
        risultato.append("=" * 80)
        risultato.append(f"ANALISI ELEZIONI REGIONALI - {info['desc_com']}")
        risultato.append("=" * 80)
        risultato.append(f"Provincia: {info['desc_prov']}")
        risultato.append(f"Circoscrizione: {info['desc_circ']}")
        risultato.append(f"Data elezioni: {self._formatta_data(info['dt_ele'])}")
        risultato.append(f"Sezioni: {liste[0]['sez_perv']}/{liste[0]['sez_tot']}")
        risultato.append("")
        
        for i, (presidente, dati) in enumerate(presidenti_ordinati, 1):
            risultato.append("-" * 80)
            risultato.append(f"{i}. CANDIDATO PRESIDENTE: {presidente}")
            risultato.append("-" * 80)
            risultato.append(f"Voti totali liste: {dati['voti_lista']:,}")
            risultato.append(f"Preferenze espresse: {dati['voti_preferenze']:,}")
            risultato.append("")
            risultato.append(f"Liste collegate ({len(dati['liste'])}):")
            for lista in sorted(dati['liste'], key=lambda x: x['voti'], reverse=True):
                risultato.append(f"  • {lista['nome']}: {lista['voti']:,} voti")
            
            if dati['candidati_top']:
                risultato.append("")
                risultato.append(f"Candidati più votati:")
                for j, cand in enumerate(dati['candidati_top'], 1):
                    nome_completo = f"{cand['cogn']} {cand['nome']}"
                    if cand['a_nome']:
                        nome_completo += f" {cand['a_nome']}"
                    risultato.append(f"  {j}. {nome_completo}: {cand['voti']:,} voti")
            risultato.append("")
        
        # Statistiche generali
        risultato.append("=" * 80)
        risultato.append("STATISTICHE GENERALI")
        risultato.append("=" * 80)
        risultato.append(f"Totale candidati presidente: {len(presidenti_ordinati)}")
        risultato.append(f"Totale liste: {len(liste)}")
        risultato.append(f"Totale candidati consiglieri: {len(candidati)}")
        voti_totali = sum(c['voti'] for c in candidati)
        risultato.append(f"Totale preferenze espresse: {voti_totali:,}")
        
        return "\n".join(risultato)
    
    def confronta_comuni(self, *nomi_comuni):
        """Confronta i risultati di più comuni"""
        risultato = []
        risultato.append("=" * 80)
        risultato.append("CONFRONTO TRA COMUNI")
        risultato.append("=" * 80)
        
        dati_comuni = []
        for nome in nomi_comuni:
            comune = self.trova_comune(nome)
            if comune:
                dati_comuni.append(comune)
            else:
                risultato.append(f"⚠️  Comune '{nome}' non trovato")
        
        if not dati_comuni:
            return "\n".join(risultato)
        
        # Aggrega dati per presidente
        voti_aggregati = defaultdict(int)
        
        for comune in dati_comuni:
            risultato.append(f"\n{comune['int']['desc_com']}:")
            
            for lista in comune['liste']:
                presidente = self._associa_lista_a_presidente(lista['desc'])
                voti = sum(c['voti'] for c in comune['cand'] if c['cod_lis'] == lista['cod'])
                voti_aggregati[presidente] += voti
                risultato.append(f"  • {presidente}: {voti:,} voti")
        
        risultato.append("\n" + "=" * 80)
        risultato.append("TOTALE AGGREGATO")
        risultato.append("=" * 80)
        
        for presidente, voti in sorted(voti_aggregati.items(), key=lambda x: x[1], reverse=True):
            risultato.append(f"{presidente}: {voti:,} voti")
        
        return "\n".join(risultato)
    
    def lista_comuni(self, provincia=None):
        """Elenca tutti i comuni disponibili, opzionalmente filtrati per provincia"""
        comuni_list = []
        
        for comune in self.comuni:
            info = comune['int']
            if provincia is None or info['desc_prov'].upper() == provincia.upper():
                comuni_list.append({
                    'nome': info['desc_com'],
                    'provincia': info['desc_prov'],
                    'cod': info['cod_com']
                })
        
        comuni_list.sort(key=lambda x: x['nome'])
        
        risultato = []
        if provincia:
            risultato.append(f"Comuni in provincia di {provincia}:")
        else:
            risultato.append("Tutti i comuni disponibili:")
        risultato.append("")
        
        provincia_corrente = None
        for comune in comuni_list:
            if comune['provincia'] != provincia_corrente:
                provincia_corrente = comune['provincia']
                risultato.append(f"\n{provincia_corrente}:")
            risultato.append(f"  • {comune['nome']}")
        
        return "\n".join(risultato)
    
    def _formatta_data(self, data_num):
        """Formatta una data da formato numerico a stringa"""
        data_str = str(data_num)
        if len(data_str) == 14:
            anno = data_str[0:4]
            mese = data_str[4:6]
            giorno = data_str[6:8]
            return f"{giorno}/{mese}/{anno}"
        return str(data_num)


def main():
    """Funzione principale per uso interattivo"""
    analizzatore = AnalizzatoreElezioni()
    
    print("🗳️  ANALIZZATORE RISULTATI ELEZIONI REGIONALI CAMPANIA 2025")
    print("=" * 80)
    print("\nComandi disponibili:")
    print("  analizza <nome_comune>     - Analizza i risultati di un comune")
    print("  confronta <comune1> <comune2> ... - Confronta più comuni")
    print("  lista [provincia]          - Elenca tutti i comuni (opzionalmente per provincia)")
    print("  esci                       - Termina il programma")
    print("\n" + "=" * 80)
    
    while True:
        try:
            comando = input("\n👉 ").strip()
            
            if not comando:
                continue
            
            parti = comando.split(maxsplit=1)
            cmd = parti[0].lower()
            
            if cmd == 'esci' or cmd == 'exit' or cmd == 'quit':
                print("Arrivederci! 👋")
                break
            
            elif cmd == 'analizza' and len(parti) > 1:
                nome_comune = parti[1]
                print(analizzatore.analizza_comune(nome_comune))
            
            elif cmd == 'confronta' and len(parti) > 1:
                comuni = [c.strip() for c in parti[1].split(',') if c.strip()]
                if len(comuni) < 2:
                    comuni = parti[1].split()
                print(analizzatore.confronta_comuni(*comuni))
            
            elif cmd == 'lista':
                provincia = parti[1] if len(parti) > 1 else None
                print(analizzatore.lista_comuni(provincia))
            
            else:
                print("❌ Comando non riconosciuto. Usa: analizza, confronta, lista, esci")
        
        except KeyboardInterrupt:
            print("\n\nArrivederci! 👋")
            break
        except Exception as e:
            print(f"❌ Errore: {e}")


if __name__ == "__main__":
    main()
