import pandas as pd
import random
import numpy as np
import time

# ==========================================
# KONFIGURASI GENETIC ALGORITHM
# ==========================================
POPULATION_SIZE = 50    # Jumlah menu dalam satu generasi
GENERATIONS = 100       # Berapa kali evolusi dilakukan
MUTATION_RATE = 0.1     # Kemungkinan menu berubah (variasi)
MEAL_COUNT = 3          # Makan 3x sehari (Pagi, Siang, Malam)

# ==========================================
# 1. LOAD DATA
# ==========================================
def load_data():
    try:
        df = pd.read_csv('nutrition_real_price_full.csv')
        return df
    except FileNotFoundError:
        print("Error: File 'nutrition_real_price_full.csv' tidak ditemukan!")
        exit()

# ==========================================
# 2. GENETIC ALGORITHM ENGINE
# ==========================================

def create_individual(df):
    """Membuat 1 menu harian acak (3 makanan)"""
    return df.sample(MEAL_COUNT).index.tolist()

def calculate_fitness(individual_indices, df, target_budget, target_cal, target_prot):
    """Menghitung seberapa bagus kombinasi menu ini (Fitness Score)"""
    # Ambil data makanan berdasarkan index
    meals = df.loc[individual_indices]
    
    total_price = meals['price'].sum()
    total_cal = meals['calories'].sum()
    total_prot = meals['proteins'].sum()
    
    # Hitung Error (Selisih dari target)
    # Penalty jika over budget
    price_error = 0
    if total_price > target_budget:
        price_error = (total_price - target_budget) * 10  
    else:
        #(semakin murah semakin baik, tapi prioritas nutrisi)
        price_error = 0 

    cal_error = abs(target_cal - total_cal)
    prot_error = abs(target_prot - total_prot) * 10 # Protein seringkali angkanya kecil, jadi kita kali bobotnya
    
    total_error = price_error + cal_error + prot_error
    
    # Fitness adalah kebalikan dari error
    # Ditambah 1 agar tidak pembagian dengan nol.
    return 1 / (total_error + 1)

def crossover(parent1, parent2):
    """Kawin silang: Mengambil sebagian menu ayah dan sebagian menu ibu"""
    crossover_point = random.randint(1, MEAL_COUNT - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    return child

def mutate(individual, df):
    """Mutasi: Mengganti 1 makanan secara acak agar ada variasi"""
    if random.random() < MUTATION_RATE:
        idx_to_change = random.randint(0, MEAL_COUNT - 1)
        new_food = df.sample(1).index[0]
        individual[idx_to_change] = new_food
    return individual

def run_genetic_algorithm(df, budget, cal, prot):
    # 1. Inisialisasi Populasi Awal
    population = [create_individual(df) for _ in range(POPULATION_SIZE)]
    
    print(f"\n[SYSTEM] Memulai evolusi menu selama {GENERATIONS} generasi...")
    
    for gen in range(GENERATIONS):
        # Hitung fitness untuk semua individu
        fitness_scores = [calculate_fitness(ind, df, budget, cal, prot) for ind in population]
        
        # Buat populasi baru (Generasi selanjutnya)
        new_population = []
        
        # Elitisme: Simpan 2 menu terbaik dari generasi sebelumnya tanpa diubah
        sorted_indices = np.argsort(fitness_scores)[::-1]
        new_population.append(population[sorted_indices[0]])
        new_population.append(population[sorted_indices[1]])
        
        # Reproduksi sisa populasi
        while len(new_population) < POPULATION_SIZE:
            # Seleksi orang tua (Tournament Selection sederhana)
            parent1 = population[random.choice(sorted_indices[:10])] # Pilih dari top 10
            parent2 = population[random.choice(sorted_indices[:10])]
            
            # Crossover
            child = crossover(parent1, parent2)
            
            # Mutasi
            child = mutate(child, df)
            
            new_population.append(child)
            
        population = new_population
        
        # Opsional: Print progress tiap 20 generasi
        if gen % 20 == 0:
            best_idx = np.argmax(fitness_scores)
            current_best = fitness_scores[best_idx]
            # print(f"Gen {gen}: Best Fitness {current_best:.5f}")

    # Ambil hasil terbaik di generasi terakhir
    final_fitness = [calculate_fitness(ind, df, budget, cal, prot) for ind in population]
    best_individual_idx = np.argmax(final_fitness)
    best_menu_indices = population[best_individual_idx]
    
    return df.loc[best_menu_indices]

# ==========================================
# 3. INTERFACE TERMINAL (CLI)
# ==========================================
def main():
    df = load_data()
    
    print("="*50)
    print("   APLIKASI OPTIMASI MENU MAKAN (GENETIC ALGO)")
    print("="*50)
    print("Selamat datang! Aplikasi ini akan mencarikan 3 menu harian")
    print("yang sesuai dengan budget dan target gizimu.\n")
    
    try:
        budget_input = int(input("Masukkan Budget Harian (Rp): "))
        cal_input = float(input("Target Kalori (kkal)       : "))
        prot_input = float(input("Target Protein (gram)      : "))
    except ValueError:
        print("\nInput harus berupa angka!")
        return

    start_time = time.time()
    

    result_df = run_genetic_algorithm(df, budget_input, cal_input, prot_input)
    
    end_time = time.time()
    
    print("\n" + "="*50)
    print("HASIL REKOMENDASI MENU TERBAIK")
    print("="*50)
    
    total_price = 0
    total_cal = 0
    total_prot = 0
    
    for i, row in result_df.iterrows():
        print(f"- {row['name']}")
        print(f"  Harga: Rp {row['price']:,} | Kal: {row['calories']} | Prot: {row['proteins']}g")
        total_price += row['price']
        total_cal += row['calories']
        total_prot += row['proteins']
        
    print("-" * 50)
    print(f"TOTAL BIAYA   : Rp {total_price:,} (Budget: Rp {budget_input:,})")
    print(f"TOTAL KALORI  : {total_cal:.1f} kkal (Target: {cal_input})")
    print(f"TOTAL PROTEIN : {total_prot:.1f} g    (Target: {prot_input})")
    print("-" * 50)
    
    if total_price <= budget_input:
        print("STATUS: \033[92mMASUK BUDGET\033[0m") 
    else:
        print(f"STATUS: \033[91mOVER BUDGET (Rp {total_price - budget_input:,})\033[0m")
        
    print(f"Waktu Komputasi: {end_time - start_time:.4f} detik")

if __name__ == "__main__":
    main()