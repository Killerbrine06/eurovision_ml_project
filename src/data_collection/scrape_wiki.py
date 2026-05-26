import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import io

def scrape_eurovision_year(year):
    """
    Extrage datele despre semifinalele Eurovision pentru un an specific de pe Wikipedia.
    """
    url = f"https://en.wikipedia.org/wiki/Eurovision_Song_Contest_{year}"
    print(f"[{year}] Accesăm datele de la: {url}")
    
    # Adăugăm un header pentru a nu fi blocați de Wikipedia
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"[{year}] Eroare la accesarea paginii.")
        return None

    # Parsează pagina HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Găsește toate tabelele de pe pagină (clasa 'wikitable' este standard pe Wiki)
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    year_data = []
    
    # Iterăm prin tabele pentru a le găsi pe cele de semifinale
    for idx, table in enumerate(tables):
        # Convertim tabelul HTML într-un DataFrame pandas
        df = pd.read_html(io.StringIO(str(table)))[0]
        
        # Curățăm numele coloanelor (eliminăm spațiile și le facem mici)
        df.columns = [str(c).lower().strip() for c in df.columns]
        
        # Verificăm dacă este un tabel relevant (conține țara și melodia)
        if 'country' in df.columns and 'song' in df.columns:
            # Determinăm stadiul competiției (heurisc simplu: tabelele apar de obicei primele)
            stadiu = "Semifinal" if idx < 2 else "Final"
            
            # Ne interesează doar semifinalele pentru setul nostru de date
            if stadiu == "Semifinal":
                # Adăugăm metadate
                df['anul'] = year
                df['stadiu_competitie'] = f"Semi-final {idx + 1}"
                
                # În funcție de an, coloana de calificare se poate numi 'place', 'result' sau e colorată.
                # Aici preluăm coloanele sigure pentru a construi scheletul
                cols_to_keep = ['anul', 'stadiu_competitie', 'country', 'artist', 'song']
                
                # Evităm erorile dacă o coloană lipsește într-un an specific
                available_cols = [col for col in cols_to_keep if col in df.columns]
                clean_df = df[available_cols].copy()
                
                year_data.append(clean_df)
    
    if year_data:
        # Unim toate tabelele găsite pentru anul respectiv
        final_year_df = pd.concat(year_data, ignore_index=True)
        return final_year_df
    else:
        print(f"[{year}] Nu am putut identifica tabelele corecte.")
        return None

def main():
    # Setăm perioada de analiză (Sistemul cu două semifinale a început în 2008)
    ani_de_extras = range(2008, 2024) 
    toate_datele = []
    
    # Creăm folderul pentru date brute dacă nu există
    os.makedirs('../../data/raw', exist_ok=True)
    
    for an in ani_de_extras:
        # Concursul nu a fost organizat în 2020 din cauza pandemiei
        if an == 2020:
            continue
            
        df_an = scrape_eurovision_year(an)
        if df_an is not None:
            toate_datele.append(df_an)
            
        time.sleep(2)
        
    # Salvăm totul într-un CSV master
    if toate_datele:
        dataset_final = pd.concat(toate_datele, ignore_index=True)
        output_path = '../../data/raw/eurovision_base_data.csv'
        dataset_final.to_csv(output_path, index=False)
        print(f"\nSucces! Am salvat {len(dataset_final)} rânduri în {output_path}")

if __name__ == "__main__":
    main()