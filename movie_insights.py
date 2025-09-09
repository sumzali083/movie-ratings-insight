import pandas as pd

df = pd.read_csv("data/imdb_top_1000.csv")

df.dropna(inplace = True)

df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce").astype("Int64")

# Convert rating to float
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")

# Convert votes to numeric (int if preferred)
df["No_of_Votes"] = pd.to_numeric(df["No_of_Votes"], errors="coerce").astype("Int64")



#5) Normalise the genre column
#Split the Genre string on commas into a list (e.g., "Drama, Romance" → ["Drama","Romance"]).
#Create a helper that:
#Trims spaces.
#Standardises casing (e.g., title-case).
#This lets you test membership (“contains ‘Drama’?”) reliably.

# Helper to normalize genres
def normalize_genres(genre_str):
    if pd.isna(genre_str):
        return []
    return [g.strip().title() for g in genre_str.split(",")]

# Apply normalization
df["Genre"] = df["Genre"].apply(normalize_genres)

print(df)
