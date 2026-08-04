#!/usr/bin/env python3
"""Safe SimCity 4 DBPF locale inspection and update utilities."""
from __future__ import annotations
import argparse, hashlib, json, struct
from dataclasses import dataclass
from pathlib import Path

LTEXT = 0x2026960B
HEADER_SIZE = 96
INDEX_ENTRY_SIZE = 20


def refpack_decompress(data: bytes) -> bytes:
    expected = None
    if data[:2] == b"\x10\xfb":
        if len(data) < 5: raise ValueError("truncated RefPack header")
        expected = int.from_bytes(data[2:5], "big"); data = data[5:]
    i = 0; out = bytearray()
    while i < len(data):
        first = data[i]; i += 1
        if not first & 0x80:
            if i >= len(data): raise ValueError("truncated short reference")
            second = data[i]; i += 1; literal = first & 3
            out += data[i:i+literal]; i += literal
            ref = len(out)-1-(((first & 0x60) << 3)+second); count = ((first & 0x1c)>>2)+3
        elif not first & 0x40:
            if i+2 > len(data): raise ValueError("truncated long reference")
            second, third = data[i:i+2]; i += 2; literal = second >> 6
            out += data[i:i+literal]; i += literal
            ref = len(out)-1-(((second & 0x3f)<<8)+third); count = (first & 0x3f)+4
        elif not first & 0x20:
            if i+3 > len(data): raise ValueError("truncated very-long reference")
            second, third, fourth = data[i:i+3]; i += 3; literal = first & 3
            out += data[i:i+literal]; i += literal
            distance = (((first & 0x10)>>4)<<16)+(second<<8)+third
            ref = len(out)-1-distance; count = (((first & 0x0c)>>2)<<8)+fourth+5
        else:
            count = ((first & 0x1f)<<2)+4
            if count <= 112:
                out += data[i:i+count]; i += count; continue
            literal = first & 3; out += data[i:i+literal]; break
        if ref < 0: raise ValueError("invalid RefPack back-reference")
        for _ in range(count): out.append(out[ref]); ref += 1
    if expected is not None and len(out) != expected:
        raise ValueError(f"RefPack size mismatch: expected {expected}, got {len(out)}")
    return bytes(out)


def _hash3(data: bytes) -> int: return ((data[0]<<4) ^ (data[1]<<2) ^ data[2]) & 0xffff


def refpack_compress(data: bytes) -> bytes:
    n=len(data); encoded=bytearray(); run=cptr=rptr=0
    table=[-1]*65536; links=[-1]*131072
    while cptr<n:
        boffset=0; blen=2; bcost=2; mlen=min(n-cptr,1028)
        if cptr+2>=n: mlen=0
        if mlen>=3:
            prev=table[_hash3(data[cptr:cptr+3])]; minimum=max(cptr-131071,0)
            while prev>=minimum:
                if cptr+blen<n and prev+blen<n and data[cptr+blen]==data[prev+blen]:
                    length=0
                    while length<mlen and data[cptr+length]==data[prev+length]: length+=1
                    distance=(cptr-1)-prev
                    cost=2 if distance<1024 and length<=10 else (3 if distance<16384 and length<=67 else 4)
                    if length>blen and length-cost>blen-bcost:
                        blen,bcost,boffset=length,cost,distance
                        if blen>=1028: break
                prev=links[prev & 131071]
        if bcost>=blen:
            h=_hash3(data[cptr:cptr+3]) if cptr+2<n else 0
            links[cptr & 131071]=table[h]; table[h]=cptr; run+=1; cptr+=1; continue
        while run>3:
            length=min(112,run & ~3); run-=length
            encoded.append(0xe0+(length>>2)-1); encoded+=data[rptr:rptr+length]; rptr+=length
        if bcost==2:
            encoded.append(((boffset>>8)<<5)+((blen-3)<<2)+run); encoded.append(boffset&255)
        elif bcost==3:
            encoded.append(0x80+blen-4); encoded.append((run<<6)+(boffset>>8)); encoded.append(boffset&255)
        else:
            encoded.append(0xc0+((boffset>>16)<<4)+(((blen-5)>>8)<<2)+run)
            encoded += bytes([(boffset>>8)&255,boffset&255,(blen-5)&255])
        if run: encoded+=data[rptr:rptr+run]; rptr+=run; run=0
        for _ in range(blen):
            if cptr+2<n:
                h=_hash3(data[cptr:cptr+3]); links[cptr & 131071]=table[h]; table[h]=cptr
            cptr+=1
        rptr=cptr
    while run>3:
        length=min(112,run & ~3); run-=length
        encoded.append(0xe0+(length>>2)-1); encoded+=data[rptr:rptr+length]; rptr+=length
    encoded.append(0xfc+run)
    if run: encoded+=data[rptr:rptr+run]
    return b"\x10\xfb"+n.to_bytes(3,"big")+bytes(encoded)

@dataclass(frozen=True)
class Entry:
    type_id:int; group_id:int; instance_id:int; offset:int; size:int; raw:bytes
    @property
    def key(self): return (self.type_id,self.group_id,self.instance_id)

class DBPF:
    def __init__(self,path:Path,data:bytes):
        if data[:4]!=b"DBPF": raise ValueError(f"not DBPF: {path}")
        self.path=path; self.data=data
        self.count,self.index_offset,self.index_size=struct.unpack_from("<3I",data,36)
        if self.index_size!=self.count*INDEX_ENTRY_SIZE: raise ValueError("unsupported DBPF index")
        self.entries=[]
        for i in range(self.count):
            vals=struct.unpack_from("<5I",data,self.index_offset+i*INDEX_ENTRY_SIZE)
            if vals[3]<HEADER_SIZE or vals[3]+vals[4]>len(data): raise ValueError("invalid DBPF bounds")
            self.entries.append(Entry(*vals,data[vals[3]:vals[3]+vals[4]]))
    @classmethod
    def load(cls,path): return cls(Path(path),Path(path).read_bytes())
    def ltexts(self): return [e for e in self.entries if e.type_id==LTEXT]


def decode_resource(raw:bytes)->bytes:
    return refpack_decompress(raw[4:]) if len(raw)>=6 and raw[4:6]==b"\x10\xfb" else raw


def ltext_text(raw:bytes)->str|None:
    body=decode_resource(raw)
    if len(body)<4: return None
    try: return body[4:].decode("utf-16le").rstrip("\x00")
    except UnicodeDecodeError: return None


def replace_ltext(raw:bytes,text:str)->bytes:
    body=decode_resource(raw)
    if len(body)<4: raise ValueError("short LTEXT")
    encoded = text.encode("utf-16le")
    # LTEXT stores the UTF-16 code-unit count in the low 24 bits and
    # retains the 0x10 format marker in the fourth byte. Preserve any
    # opaque suffix after the original counted text.
    old_units = int.from_bytes(body[:3], "little")
    old_end = 4 + old_units * 2
    if old_end > len(body): raise ValueError("invalid LTEXT length")
    if len(encoded) // 2 > 0xFFFFFF: raise ValueError("LTEXT string too long")
    suffix = body[old_end:]
    new_body = (len(encoded) // 2).to_bytes(3, "little") + body[3:4] + encoded + suffix
    if len(raw)>=6 and raw[4:6]==b"\x10\xfb":
        stream=refpack_compress(new_body); return len(stream).to_bytes(4,"little")+stream
    return new_body


def repack(db:DBPF,replacements:dict[tuple[int,int,int],str],out:Path)->int:
    # Refuse to rebuild an archive if it contains bytes outside the indexed
    # resources; silently dropping those bytes would be unsafe.
    if db.index_offset + db.index_size != len(db.data):
        raise ValueError("DBPF contains unindexed/trailing data; refusing to repack")
    payloads=[]; changed=0
    for entry in db.entries:
        raw=entry.raw
        if entry.key in replacements:
            raw=replace_ltext(raw,replacements[entry.key]); changed+=1
        payloads.append((entry,raw))
    cursor=HEADER_SIZE; chunks=[]; index=[]
    for entry,raw in payloads:
        chunks.append(raw); index.append((entry.type_id,entry.group_id,entry.instance_id,cursor,len(raw))); cursor+=len(raw)
    index_offset=cursor; index_data=b"".join(struct.pack("<5I",*x) for x in index)
    header=bytearray(db.data[:HEADER_SIZE]); struct.pack_into("<3I",header,36,len(index),index_offset,len(index_data))
    out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(bytes(header)+b"".join(chunks)+index_data)
    return changed

# Only unambiguous common UI terms are changed automatically. Proper names,
# filenames, acronyms, URLs and technical tokens remain untouched.
TRANSLATIONS={
"da":{"Train":"Tog","Subway":"Metro","Road":"Vej","Home":"Hjem","Accept":"Accepter","Cancel":"Annuller","Yes":"Ja","No":"Nej","Water":"Vand","Power":"Strøm","Fire":"Brand","Police":"Politi","School":"Skole","Airport":"Lufthavn","Mayor":"Borgmester","City":"By","Budget":"Budget","Hospital":"Hospital","Library":"Bibliotek","Museum":"Museum","Park":"Park","University":"Universitet"},
"nl":{"Train":"Trein","Subway":"Metro","Road":"Weg","Home":"Thuis","Accept":"Accepteren","Cancel":"Annuleren","Yes":"Ja","No":"Nee","Water":"Water","Power":"Energie","Fire":"Brandweer","Police":"Politie","School":"School","Airport":"Luchthaven","Mayor":"Burgemeester","City":"Stad","Budget":"Begroting","Library":"Bibliotheek","Museum":"Museum","University":"Universiteit"},
"fi":{"Train":"Juna","Subway":"Metro","Road":"Tie","Home":"Koti","Accept":"Hyväksy","Cancel":"Peruuta","Yes":"Kyllä","No":"Ei","Water":"Vesi","Power":"Sähkö","Fire":"Palo","Police":"Poliisi","School":"Koulu","Airport":"Lentokenttä","Mayor":"Pormestari","City":"Kaupunki","Budget":"Budjetti","Library":"Kirjasto","Museum":"Museo","University":"Yliopisto"},
"fr":{"Train":"Train","Subway":"Métro","Road":"Route","Home":"Accueil","Accept":"Accepter","Cancel":"Annuler","Yes":"Oui","No":"Non","Water":"Eau","Power":"Électricité","Fire":"Incendie","Police":"Police","School":"École","Airport":"Aéroport","Mayor":"Maire","City":"Ville","Budget":"Budget","Library":"Bibliothèque","Museum":"Musée","University":"Université"},
"de":{"Train":"Zug","Subway":"U-Bahn","Road":"Straße","Home":"Startseite","Accept":"Akzeptieren","Cancel":"Abbrechen","Yes":"Ja","No":"Nein","Water":"Wasser","Power":"Strom","Fire":"Feuer","Police":"Polizei","School":"Schule","Airport":"Flughafen","Mayor":"Bürgermeister","City":"Stadt","Budget":"Budget","Library":"Bibliothek","Museum":"Museum","University":"Universität"},
"it":{"Train":"Treno","Subway":"Metropolitana","Road":"Strada","Home":"Casa","Accept":"Accetta","Cancel":"Annulla","Yes":"Sì","No":"No","Water":"Acqua","Power":"Elettricità","Fire":"Incendio","Police":"Polizia","School":"Scuola","Airport":"Aeroporto","Mayor":"Sindaco","City":"Città","Budget":"Bilancio","Library":"Biblioteca","Museum":"Museo","University":"Università"},
"no":{"Train":"Tog","Subway":"T-bane","Road":"Vei","Home":"Hjem","Accept":"Godta","Cancel":"Avbryt","Yes":"Ja","No":"Nei","Water":"Vann","Power":"Strøm","Fire":"Brann","Police":"Politi","School":"Skole","Airport":"Flyplass","Mayor":"Ordfører","City":"By","Budget":"Budsjett","Library":"Bibliotek","Museum":"Museum","University":"Universitet"},
"pl":{"Train":"Pociąg","Subway":"Metro","Road":"Droga","Home":"Dom","Accept":"Akceptuj","Cancel":"Anuluj","Yes":"Tak","No":"Nie","Water":"Woda","Power":"Prąd","Fire":"Pożar","Police":"Policja","School":"Szkoła","Airport":"Lotnisko","Mayor":"Burmistrz","City":"Miasto","Budget":"Budżet","Library":"Biblioteka","Museum":"Muzeum","University":"Uniwersytet"},
"pt":{"Train":"Trem","Subway":"Metrô","Road":"Estrada","Home":"Casa","Accept":"Aceitar","Cancel":"Cancelar","Yes":"Sim","No":"Não","Water":"Água","Power":"Energia","Fire":"Incêndio","Police":"Polícia","School":"Escola","Airport":"Aeroporto","Mayor":"Prefeito","City":"Cidade","Budget":"Orçamento","Library":"Biblioteca","Museum":"Museu","University":"Universidade"},
"es":{"Train":"Tren","Subway":"Metro","Road":"Carretera","Home":"Casa","Accept":"Aceptar","Cancel":"Cancelar","Yes":"Sí","No":"No","Water":"Agua","Power":"Electricidad","Fire":"Incendio","Police":"Policía","School":"Escuela","Airport":"Aeropuerto","Mayor":"Alcalde","City":"Ciudad","Budget":"Presupuesto","Library":"Biblioteca","Museum":"Museo","University":"Universidad"},
"sv":{"Train":"Tåg","Subway":"Tunnelbana","Road":"Väg","Home":"Hem","Accept":"Acceptera","Cancel":"Avbryt","Yes":"Ja","No":"Nej","Water":"Vatten","Power":"Elektricitet","Fire":"Brand","Police":"Polis","School":"Skola","Airport":"Flygplats","Mayor":"Borgmästare","City":"Stad","Budget":"Budget","Library":"Bibliotek","Museum":"Museum","University":"Universitet"},
}

# Additional exact UI labels. These are applied only when the target text is
# byte-for-byte equal to the English text for the same TGI; proper names,
# mission titles, filenames, URLs and technical tokens are never guessed.
_EXTRA = {
"da":{"Ambulance":"Ambulance","Bus":"Bus","Credits":"Credits","Downloads":"Downloads","Enter":"Indtast","Error":"Fejl","Export":"Eksportér","Garage":"Garage","Green":"Grøn","Import":"Importér","Jobs":"Job","Land":"Land","Landfill":"Losseplads","Medium":"Mellem","Name":"Navn","Restaurant":"Restaurant","Software":"Software","Special":"Særlig","Speedometer":"Speedometer","Stop":"Stop","Subtotal":"Delsum","Tank":"Tank","Tanker":"Tankvogn","Taxi":"Taxa","Terminal":"Terminal","Terrain":"Terræn","Test":"Test","Total":"I alt","Trailer":"Trailer","Truck":"Lastbil","Volume":"Lydstyrke","Floating Population":"Flydende befolkning"},
"nl":{"Ambulance":"Ambulance","Bus":"Bus","Credits":"Credits","Downloads":"Downloads","Enter":"Enter","Error":"Fout","Export":"Exporteren","Garage":"Garage","Green":"Groen","Import":"Importeren","Jobs":"Banen","Land":"Land","Landfill":"Vuilstortplaats","Medium":"Gemiddeld","Name":"Naam","Restaurant":"Restaurant","Software":"Software","Special":"Speciaal","Speedometer":"Snelheidsmeter","Stop":"Stop","Subtotal":"Subtotaal","Tank":"Tank","Tanker":"Tankwagen","Taxi":"Taxi","Terminal":"Terminal","Terrain":"Terrein","Test":"Test","Total":"Totaal","Trailer":"Aanhanger","Truck":"Vrachtwagen","Volume":"Volume","Floating Population":"Zwevende bevolking"},
"fi":{"Ambulance":"Ambulanssi","Bus":"Bussi","Credits":"Tekijät","Downloads":"Lataukset","Enter":"Enter","Error":"Virhe","Export":"Vie","Garage":"Autotalli","Green":"Vihreä","Import":"Tuo","Jobs":"Työpaikat","Land":"Maa","Landfill":"Kaatopaikka","Medium":"Keskitaso","Name":"Nimi","Restaurant":"Ravintola","Software":"Ohjelmisto","Special":"Erityinen","Speedometer":"Nopeusmittari","Stop":"Pysäytä","Subtotal":"Välisummaa","Tank":"Tankki","Tanker":"Säiliöauto","Taxi":"Taksi","Terminal":"Terminaali","Terrain":"Maasto","Test":"Testi","Total":"Yhteensä","Trailer":"Perävaunu","Truck":"Kuorma-auto","Volume":"Äänenvoimakkuus","Floating Population":"Kelluva väestö"},
"fr":{"Ambulance":"Ambulance","Bus":"Bus","Credits":"Crédits","Downloads":"Téléchargements","Enter":"Entrer","Error":"Erreur","Export":"Exporter","Garage":"Garage","Green":"Vert","Import":"Importer","Jobs":"Emplois","Land":"Terrain","Landfill":"Décharge","Medium":"Moyen","Name":"Nom","Restaurant":"Restaurant","Software":"Logiciel","Special":"Spécial","Speedometer":"Compteur de vitesse","Stop":"Arrêter","Subtotal":"Sous-total","Tank":"Réservoir","Tanker":"Camion-citerne","Taxi":"Taxi","Terminal":"Terminal","Terrain":"Terrain","Test":"Test","Total":"Total","Trailer":"Remorque","Truck":"Camion","Volume":"Volume","Floating Population":"Population flottante"},
"de":{"Ambulance":"Krankenwagen","Bus":"Bus","Credits":"Mitwirkende","Downloads":"Downloads","Enter":"Eingeben","Error":"Fehler","Export":"Exportieren","Garage":"Garage","Green":"Grün","Import":"Importieren","Jobs":"Arbeitsplätze","Land":"Land","Landfill":"Mülldeponie","Medium":"Mittel","Name":"Name","Restaurant":"Restaurant","Software":"Software","Special":"Spezial","Speedometer":"Tachometer","Stop":"Stopp","Subtotal":"Zwischensumme","Tank":"Tank","Tanker":"Tankwagen","Taxi":"Taxi","Terminal":"Terminal","Terrain":"Gelände","Test":"Test","Total":"Gesamt","Trailer":"Anhänger","Truck":"Lastwagen","Volume":"Lautstärke","Floating Population":"Schwebende Bevölkerung"},
"it":{"Ambulance":"Ambulanza","Bus":"Autobus","Credits":"Riconoscimenti","Downloads":"Download","Enter":"Invio","Error":"Errore","Export":"Esporta","Garage":"Garage","Green":"Verde","Import":"Importa","Jobs":"Posti di lavoro","Land":"Terreno","Landfill":"Discarica","Medium":"Medio","Name":"Nome","Restaurant":"Ristorante","Software":"Software","Special":"Speciale","Speedometer":"Tachimetro","Stop":"Stop","Subtotal":"Subtotale","Tank":"Carro armato","Tanker":"Autocisterna","Taxi":"Taxi","Terminal":"Terminale","Terrain":"Terreno","Test":"Test","Total":"Totale","Trailer":"Rimorchio","Truck":"Camion","Volume":"Volume","Floating Population":"Popolazione fluttuante"},
"no":{"Ambulance":"Ambulanse","Bus":"Buss","Credits":"Bidragsytere","Downloads":"Nedlastinger","Enter":"Skriv inn","Error":"Feil","Export":"Eksporter","Garage":"Garasje","Green":"Grønn","Import":"Importer","Jobs":"Jobber","Land":"Land","Landfill":"Fylling","Medium":"Middels","Name":"Navn","Restaurant":"Restaurant","Software":"Programvare","Special":"Spesiell","Speedometer":"Speedometer","Stop":"Stopp","Subtotal":"Delsum","Tank":"Tank","Tanker":"Tankbil","Taxi":"Taxi","Terminal":"Terminal","Terrain":"Terreng","Test":"Test","Total":"Totalt","Trailer":"Tilhenger","Truck":"Lastebil","Volume":"Volum","Floating Population":"Flytende befolkning"},
"pl":{"Ambulance":"Karetka","Bus":"Autobus","Credits":"Twórcy","Downloads":"Pobrane","Enter":"Wprowadź","Error":"Błąd","Export":"Eksportuj","Garage":"Garaż","Green":"Zielony","Import":"Importuj","Jobs":"Miejsca pracy","Land":"Teren","Landfill":"Wysypisko","Medium":"Średni","Name":"Nazwa","Restaurant":"Restauracja","Software":"Oprogramowanie","Special":"Specjalny","Speedometer":"Prędkościomierz","Stop":"Stop","Subtotal":"Suma częściowa","Tank":"Czołg","Tanker":"Cysterna","Taxi":"Taksówka","Terminal":"Terminal","Terrain":"Teren","Test":"Test","Total":"Razem","Trailer":"Przyczepa","Truck":"Ciężarówka","Volume":"Głośność","Floating Population":"Pływająca populacja"},
"pt":{"Ambulance":"Ambulância","Bus":"Ônibus","Credits":"Créditos","Downloads":"Downloads","Enter":"Entrar","Error":"Erro","Export":"Exportar","Garage":"Garagem","Green":"Verde","Import":"Importar","Jobs":"Empregos","Land":"Terreno","Landfill":"Aterro","Medium":"Médio","Name":"Nome","Restaurant":"Restaurante","Software":"Software","Special":"Especial","Speedometer":"Velocímetro","Stop":"Parar","Subtotal":"Subtotal","Tank":"Tanque","Tanker":"Caminhão-tanque","Taxi":"Táxi","Terminal":"Terminal","Terrain":"Terreno","Test":"Teste","Total":"Total","Trailer":"Reboque","Truck":"Caminhão","Volume":"Volume","Floating Population":"População flutuante"},
"es":{"Ambulance":"Ambulancia","Bus":"Autobús","Credits":"Créditos","Downloads":"Descargas","Enter":"Entrar","Error":"Error","Export":"Exportar","Garage":"Garaje","Green":"Verde","Import":"Importar","Jobs":"Empleos","Land":"Terreno","Landfill":"Vertedero","Medium":"Medio","Name":"Nombre","Restaurant":"Restaurante","Software":"Software","Special":"Especial","Speedometer":"Velocímetro","Stop":"Detener","Subtotal":"Subtotal","Tank":"Tanque","Tanker":"Camión cisterna","Taxi":"Taxi","Terminal":"Terminal","Terrain":"Terreno","Test":"Prueba","Total":"Total","Trailer":"Remolque","Truck":"Camión","Volume":"Volumen","Floating Population":"Población flotante"},
"sv":{"Ambulance":"Ambulans","Bus":"Buss","Credits":"Medverkande","Downloads":"Nedladdningar","Enter":"Ange","Error":"Fel","Export":"Exportera","Garage":"Garage","Green":"Grön","Import":"Importera","Jobs":"Arbeten","Land":"Mark","Landfill":"Soptipp","Medium":"Medel","Name":"Namn","Restaurant":"Restaurang","Software":"Programvara","Special":"Special","Speedometer":"Hastighetsmätare","Stop":"Stopp","Subtotal":"Delsumma","Tank":"Tank","Tanker":"Tankbil","Taxi":"Taxi","Terminal":"Terminal","Terrain":"Terräng","Test":"Test","Total":"Totalt","Trailer":"Släpvagn","Truck":"Lastbil","Volume":"Volym","Floating Population":"Flytande befolkning"},
}
for _language, _terms in _EXTRA.items(): TRANSLATIONS[_language].update(_terms)


def compare(english,target):
    e={x.key:ltext_text(x.raw) for x in DBPF.load(english).ltexts()}; t={x.key:ltext_text(x.raw) for x in DBPF.load(target).ltexts()}
    same=[k for k in e if e[k] is not None and k in t and t[k]==e[k]]
    return {"english_ltexts":len(e),"target_ltexts":len(t),"identical_to_english":len(same),"missing_tgi":len([k for k in e if k not in t]),"identical_keys":["".join(f"{x:08x}" for x in k) for k in same]}


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("inspect"); p.add_argument("files",nargs="+")
    p=sub.add_parser("compare"); p.add_argument("english"); p.add_argument("target")
    p=sub.add_parser("translate"); p.add_argument("english"); p.add_argument("target"); p.add_argument("language"); p.add_argument("output")
    p=sub.add_parser("extract"); p.add_argument("file"); p.add_argument("output")
    a=ap.parse_args()
    if a.cmd=="inspect":
        for name in a.files:
            d=DBPF.load(name); print(name,len(d.data),d.count,len(d.ltexts()))
    elif a.cmd=="compare": print(json.dumps(compare(a.english,a.target),ensure_ascii=False))
    elif a.cmd=="extract":
        d=DBPF.load(a.file); data={"path":a.file,"sha256":hashlib.sha256(d.data).hexdigest(),"resources":d.count,"ltexts":{":".join(f"{x:08x}" for x in e.key):ltext_text(e.raw) for e in d.ltexts() if ltext_text(e.raw) is not None}}
        Path(a.output).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    else:
        source=DBPF.load(a.english); target=DBPF.load(a.target); mapping=TRANSLATIONS[a.language]
        english={e.key:ltext_text(e.raw) for e in source.ltexts()}; replacements={}
        for e in target.ltexts():
            text=ltext_text(e.raw)
            if text in mapping and text in english.values() and text==english.get(e.key): replacements[e.key]=mapping[text]
        print(json.dumps({"replacements":len(replacements),"output":a.output},ensure_ascii=False)); repack(target,replacements,Path(a.output))

if __name__=="__main__": main()
