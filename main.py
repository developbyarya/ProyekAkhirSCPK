import streamlit as st
import pandas as pd
import numpy as np
from helper import gaussian_score, split_empasis, count_matches, budget_score, heatmap


# Load the dataset
df = pd.read_csv("dataset/transformed_universities.csv")

# Generate feature
# Taking middle value from ranged columns (no-of-students, expenses_Transformed)
def generate_middle_value(row):
    # Get the minimum and maximum values from the row, by spliting '-'
    min_value, max_value = row.split('-')
    # Convert to float
    min_value = float(min_value.strip())
    max_value = float(max_value.strip())

    # Calculate the middle value
    return (min_value + max_value) / 2

df['no-of-students'] = df["no-of-students"].apply(generate_middle_value)
df['expenses'] = df["expenses_Transformed"].apply(generate_middle_value)
df['no-applicants'] = df["no-applicants"].apply(generate_middle_value)
df = df.drop(columns=["expenses_Transformed"])

# Ensure relevant columns are float
df['no-applicants'] = df['no-applicants'].astype(float)
df['percent-admittance'] = df['percent-admittance'].astype(float)
df['percent-enrolled'] = df['percent-enrolled'].astype(float)

# Avoid divide-by-zero
df['percent-admittance'] = df['percent-admittance'].replace(0, 1e-6)

# Calculate popularity index
df['popularity_index'] = (df['no-applicants'] * df['percent-enrolled']) / df['percent-admittance']

# normalize to 0–100
df['popularity_index'] = 100 * (df['popularity_index'] - df['popularity_index'].min()) / (df['popularity_index'].max() - df['popularity_index'].min())
df['popularity_index'] = df['popularity_index'] + 0.0001

# getting academic emphasis list
academic_emphasis_set = split_empasis(df['academic-emphasis'].unique())




st.title("SPK Memilih Universtitas US")
st.write("Sistem Pendukung Keputusan (SPK) untuk memilih universitas di Amerika menggunakan metode Weighted Product (WP).")
st.header("Dataset Universitas", divider=True)
st.dataframe(df)

df_preprocessed = df.copy()
# df_preprocessed.index = df_preprocessed['instance']

with st.sidebar:
    st.header("Parameter")
    # private or public preference
    public_or_private_pref = st.selectbox("Jenis Universitas", ["Private", "Public"], key="university_type")
    
    df_preprocessed['control'] = (df_preprocessed['control'] == public_or_private_pref.lower()).astype(int) + 1
    # academic emphasis preference
    academic_emphasis_pref = st.multiselect("Emphasis Akademik", academic_emphasis_set, key="academic_emphasis")
    
    df_preprocessed['academic-emphasis_match'] = df_preprocessed['academic-emphasis'].apply(lambda x: count_matches(x, academic_emphasis_pref) + 1) 
    df_preprocessed.drop(columns=['academic-emphasis'], inplace=True)
    # preference for state
    state_pref = st.multiselect("Negara Bagian", df['state'].unique(), key="state")
    df_preprocessed['state'] = df_preprocessed['state'].isin(state_pref).astype(int) + 1
    # preference for budget (expenses)
    budget_pref = st.slider("Berapa budget (expenses) anda (USD)", min_value=0, max_value=100000, value=(0, 50000), key="budget")
    df_preprocessed['within_budget'] = df['expenses'].between(budget_pref[0], budget_pref[1]).astype(int) + 1
    df_preprocessed['budget_score'] = df_preprocessed['expenses'].apply(lambda x: budget_score(x, budget_pref[0], budget_pref[1])) + 0.001
    sat_math_score = st.number_input("Skor SAT Matematika", min_value=0, max_value=800, value=400, step=10, key="sat_math")
    sat_verbal_score = st.number_input("Skor SAT Verbal", min_value=0, max_value=800, value=400, step=10, key="sat_verbal")
    df_preprocessed['sat_total'] = df_preprocessed['sat_verbal'] + df_preprocessed['sat_math']
    user_sat_total = sat_math_score + sat_verbal_score
    df_preprocessed['sat_match_score'] = df_preprocessed['sat_total'].apply(lambda x: gaussian_score(user_sat_total, x))
    df_preprocessed.drop(columns=['sat_verbal', 'sat_math', 'sat_total'], inplace=True)


    # Wight section
    st.header("Bobot Kriteria", divider=True)
    # weight for state (1-5)
    weight_state = st.slider("Bobot Lokasi", min_value=1, max_value=5, value=2, step=1, key="weight_state")
    # weight for control (private / public university) (1-5)
    weight_control = st.slider("Bobot Swasta/Negri", min_value=1, max_value=5, value=2, step=1, key="weight_control")
    # weight for academic emphasis (1-5)
    weight_academic_emphasis = st.slider("Bobot Emphasis Akademik", min_value=1, max_value=5, value=2, step=1, key="weight_academic_emphasis")
    # bobot budget (1-5)
    weight_budget = st.slider("Bobot Budget", min_value=1, max_value=5, value=2, step=1, key="weight_budget")
    # weight untuk SAT skor (1-5)
    weight_sat = st.slider("Bobot SAT Skor", min_value=1, max_value=5, value=2, step=1, key="weight_sat")
    # weight untuk percent - financial aid (1-5)
    weight_financial_aid = st.slider("Bobot Financial Aid", min_value=1, max_value=5, value=2, step=1, key="weight_financial_aid")
    # weight untuk accaptance rate(1-5)
    weight_acceptance_rate = st.slider("Bobot % diterima", min_value=1, max_value=5, value=2, step=1, key="weight_acceptance_rate")
    # weight for popularity (1-5)
    weight_popularity = st.slider("Bobot Popularitas", min_value=1, max_value=5, value=2, step=1, key="weight_popularity")
    # bobot untuk kualitas akademik (1-5)
    weight_academic_quality = st.slider("Bobot Kualitas Akademik", min_value=1, max_value=5, value=2, step=1, key="weight_academic_quality")
    # bobot untuk kualitas sosial (1-5)
    weight_social_quality = st.slider("Bobot Kualitas Sosial", min_value=1, max_value=5, value=2, step=1, key="weight_social_quality")
    # bobot untuk kualitas hidup (1-5)
    weight_life_quality = st.slider("Bobot Kualitas Hidup", min_value=0, max_value=5, value=2, step=1, key="weight_life_quality")

kolom_tidak_terpakai = [
    "no-applicants",
    "percent-enrolled",
    "no-of-students",
    "expenses",
]
# Ganti nilai 0 ke -1


df_preprocessed = df_preprocessed.drop(columns=kolom_tidak_terpakai)

bobot = {
    "state": weight_state,
    "control": weight_control,
    "financial_aid": weight_financial_aid,
    "percent-admittance": weight_acceptance_rate,
    "kualias-akademik": weight_academic_quality,
    "kualitas-sosial": weight_social_quality,
    "kualitas-hidup": weight_life_quality,
    "popularity_index": weight_popularity,
    "emphasis_match": weight_academic_emphasis,
    "within_budget": weight_budget,
    "budget_score": weight_budget,
    "sat_score": weight_sat,
}

kolom_terpakai = [
    "state", "control", "percent-financial-aid", "percent-admittance",
    "academics", "social", "quality-of-life",
    "popularity_index", "academic-emphasis_match", "within_budget", "budget_score",
    "sat_match_score",
]



bobot_df = pd.DataFrame(bobot, index=[0])

st.header("Preprocessed Dataset", divider=True)
st.dataframe(df_preprocessed)

st.header("Bobot Kriteria", divider=True)
st.dataframe(bobot_df)

st.header("Bobot Ternormalisasi", divider=True)
# Normalizing weights
bobot_norm_df = bobot_df.copy()

bobot_norm_df = bobot_df / bobot_df.sum(axis=1)[0]
st.dataframe(bobot_norm_df)

st.header("Hasil Perhitungan", divider=True)
# Calculate the weighted product score
result_df = df.copy()
perhitung_df = df_preprocessed[kolom_terpakai]
result_df["WP Score"] = np.prod(perhitung_df.values ** bobot_norm_df.values, axis=1).astype(float)
# select top n higest rank
n_rank = st.number_input("Jumlah alternatif terbaik:", min_value=1, max_value=30, value=5)
top_n = result_df.sort_values(by=["WP Score"], ascending=False)
st.dataframe(top_n[['instance', 'state', 'control', 'WP Score']].head(n_rank))

st.header("Visualisasi Peta Panas", divider=True)
st.subheader("Skor SAT Total per Negara Bagian", divider=True)
df['sat_total'] = df['sat_verbal'] + df['sat_math']
# st.dataframe(df[['state', 'sat_total']].drop_duplicates().set_index('state'))
st.plotly_chart(heatmap(df, 'sat_total'), use_container_width=True)
st.subheader("Skor Popularitas per Negara Bagian", divider=True)
st.plotly_chart(heatmap(df, 'popularity_index'), use_container_width=True)
st.subheader("Rata-rata expenses per Negara Bagian", divider=True)
st.plotly_chart(heatmap(df, 'expenses'), use_container_width=True)