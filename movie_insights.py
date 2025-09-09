import pandas as pd

df = pd.read_csv("data/imdb_top_1000.csv")

df.dropna(inplace = True)

df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce").astype("Int64")

# Convert rating to float
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")

# Convert votes to numeric (int if preferred)
df["No_of_Votes"] = pd.to_numeric(df["No_of_Votes"], errors="coerce").astype("Int64")

print(df)

