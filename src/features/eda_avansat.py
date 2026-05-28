import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_final_visualizations():
    cale_master = '../../data/processed/eurovision_master_dataset.csv'
    cale_grafice = '../../reports/figures/'
    os.makedirs(cale_grafice, exist_ok=True)
    
    try:
        df = pd.read_csv(cale_master)
    except FileNotFoundError:
        print("Eroare: Nu găsesc fișierul master.")
        return

    # Forțăm conversia numerică
    coloane_numerice = ['bpm', 'place', 'points', 'running_order']
    for col in coloane_numerice:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    sns.set_theme(style="whitegrid")
    perioada_text = "Edițiile 2004-2023 (fără 2020)"
    
    # Setări pentru caseta de text (Text Box)
    props_caseta = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='gray')

    # ==========================================
    # GRAFICUL 1: BPM vs Punctaj
    # ==========================================
    df_bpm = df.dropna(subset=['bpm', 'points']).copy()
    cov_bpm = df_bpm['bpm'].cov(df_bpm['points'])
    corr_bpm = df_bpm['bpm'].corr(df_bpm['points'])
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_bpm, x='bpm', y='points', alpha=0.6, color='purple', edgecolor='w')
    
    plt.title(f'Există un tempo câștigător? (BPM vs. Punctaj)', fontsize=14, pad=15)
    plt.xlabel('Tempo (BPM)', fontsize=12)
    plt.ylabel('Puncte Obținute', fontsize=12)
    
    # Adăugăm caseta cu statistici în colțul din dreapta-sus
    text_bpm = f"{perioada_text}\nCovarianța: {cov_bpm:.2f}\nCorelația (r): {corr_bpm:.2f}"
    plt.gca().text(0.95, 0.95, text_bpm, transform=plt.gca().transAxes, fontsize=10,
                   verticalalignment='top', horizontalalignment='right', bbox=props_caseta)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cale_grafice, 'bpm_vs_punctaj.png'), dpi=300)
    plt.close()

    # ==========================================
    # GRAFICUL 2: Running Order vs Locul Ocupat
    # ==========================================
    df_ro = df.dropna(subset=['running_order', 'place']).copy()
    cov_ro = df_ro['running_order'].cov(df_ro['place'])
    corr_ro = df_ro['running_order'].corr(df_ro['place'])
    
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_ro, x='running_order', y='place', 
                scatter_kws={'alpha':0.5, 'color':'#2b8cbe'}, 
                line_kws={'color':'red', 'linewidth': 2})
    
    plt.title(f'Avantajul de a cânta mai târziu (Running Order vs. Loc Ocupat)', fontsize=14, pad=15)
    plt.xlabel('Ordinea de intrare pe scenă', fontsize=12)
    plt.ylabel('Locul Ocupat în Clasament', fontsize=12)
    plt.gca().invert_yaxis() # Inversăm axa: Locul 1 este cel mai bun (sus)
    
    # Adăugăm caseta (o punem jos în stânga ca să nu se suprapună cu linia de trend care urcă)
    text_ro = f"{perioada_text}\nCovarianța: {cov_ro:.2f}\nCorelația (r): {corr_ro:.2f}"
    plt.gca().text(0.05, 0.05, text_ro, transform=plt.gca().transAxes, fontsize=10,
                   verticalalignment='bottom', horizontalalignment='left', bbox=props_caseta)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cale_grafice, 'running_order_vs_loc.png'), dpi=300)
    plt.close()

    # ==========================================
    # GRAFICUL 3: Regiuni Geopolitice vs Punctaj
    # ==========================================
    df_geo = df.dropna(subset=['region', 'points']).copy()
    ordine_regiuni = df_geo.groupby('region')['points'].median().sort_values(ascending=False).index
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_geo, x='region', y='points', order=ordine_regiuni, palette='viridis')
    
    plt.title(f'Avantajul Geopolitic: Distribuția Punctajelor pe Regiuni', fontsize=14, pad=15)
    plt.xlabel('Bloc Geopolitic', fontsize=12)
    plt.ylabel('Puncte Obținute', fontsize=12)
    plt.xticks(rotation=45)
    
    # Adăugăm doar perioada pe acest grafic (covarianța nu se aplică la categorii de text)
    plt.gca().text(0.95, 0.95, perioada_text, transform=plt.gca().transAxes, fontsize=10,
                   verticalalignment='top', horizontalalignment='right', bbox=props_caseta)
    
    plt.tight_layout()
    plt.savefig(os.path.join(cale_grafice, 'regiuni_vs_punctaj.png'), dpi=300)
    plt.close()
    
    print("✓ Toate cele 3 grafice finale, adnotate matematic, au fost generate cu succes!")

if __name__ == "__main__":
    run_final_visualizations()