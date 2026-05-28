import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    cale_master = '../../data/processed/eurovision_master_dataset.csv'
    cale_grafice = '../../reports/figures/'
    
    try:
        df = pd.read_csv(cale_master)
    except FileNotFoundError:
        print("Eroare: Nu găsesc fișierul master.")
        return

    # 1. Conversia Numerică (Rămâne obligatorie pentru a evita axele aglomerate)
    coloane_numerice = ['bpm', 'gain', 'place', 'points', 'running_order']
    for col in coloane_numerice:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    os.makedirs(cale_grafice, exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    # ==========================================
    # GRAFICUL 1: BPM vs Punctaj
    # ==========================================
    # Filtrăm DOAR randurile unde bpm și points sunt valide
    df_bpm = df.dropna(subset=['bpm', 'points']).copy()
    print(f"Analizăm BPM: Folosim {len(df_bpm)} piese.")
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_bpm, x='bpm', y='points', alpha=0.6, color='purple', edgecolor='w')
    plt.title('Există un tempo câștigător? (BPM vs. Punctaj Total)', fontsize=14)
    plt.xlabel('Tempo (BPM)', fontsize=12)
    plt.ylabel('Puncte Obținute', fontsize=12)
    # Acum Matplotlib va afișa etichete numerice rare și aerisite pe axa OY automat
    
    plt.tight_layout()
    cale_grafic_1 = os.path.join(cale_grafice, 'bpm_vs_punctaj.png')
    plt.savefig(cale_grafic_1, dpi=300, bbox_inches='tight')
    plt.close()

    # ==========================================
    # GRAFICUL 2: Running Order vs Locul Ocupat
    # ==========================================
    # Filtrăm DOAR randurile unde running_order și place sunt valide
    df_ro = df.dropna(subset=['running_order', 'place']).copy()
    print(f"Analizăm Ordinea de Intrare: Folosim {len(df_ro)} piese.")
    
    plt.figure(figsize=(10, 6))
    sns.regplot(data=df_ro, x='running_order', y='place', 
                scatter_kws={'alpha':0.5, 'color':'#2b8cbe'}, 
                line_kws={'color':'red', 'linewidth': 2})
    plt.title('Avantajul de a cânta mai târziu (Running Order vs. Loc Ocupat)', fontsize=14)
    plt.xlabel('Ordinea de intrare pe scenă', fontsize=12)
    plt.ylabel('Locul Ocupat în Clasament', fontsize=12)
    plt.gca().invert_yaxis() # Inversăm pentru ca Locul 1 să fie sus
    
    plt.tight_layout()
    cale_grafic_2 = os.path.join(cale_grafice, 'running_order_vs_loc.png')
    plt.savefig(cale_grafic_2, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\n✓ Graficele au fost generate și salvate cu succes!")

if __name__ == "__main__":
    run_eda()