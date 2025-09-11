import pandas as pd
import re
import difflib

df = pd.read_csv("data/imdb_top_1000.csv")

df.dropna(inplace = True)

df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce").astype("Int64")

# Convert rating to float
df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")

# Convert votes to numeric (int if preferred)
df["No_of_Votes"] = pd.to_numeric(df["No_of_Votes"], errors="coerce").astype("Int64")


#5) Normalise the genre column
#Split the Genre string on commas into a list (e.g., "Drama, Romance" → ["Drama","Romance"]).

# Helper to normalize genres
def normalize_genres(genre_str):
    if pd.isna(genre_str):
        return []
    return [g.strip().title() for g in genre_str.split(",")]

# Apply normalization
df["Genre"] = df["Genre"].apply(normalize_genres)

print(df)

def _canon(s: str) -> str:
    """Lowercase and remove non-alphanumeric chars to compare genres reliably."""
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())

# ---------- Build a clean genre vocabulary from your list-typed df['Genre'] ----------
def build_genre_vocab(df, genre_col: str = "Genre"):
    """
    Returns:
      rep_by_canon: dict canonical_genre -> display_form (e.g., 'scifi' -> 'Sci-Fi')
      canon_set: set of canonical genres for quick membership tests
      display_set: set of original display strings (e.g., {'Drama', 'Sci-Fi', ...})
    """
    display_set = set()
    for lst in df[genre_col].dropna():
        for g in lst:
            g = g.strip()
            if g:
                display_set.add(g)

    rep_by_canon = {}
    for g in sorted(display_set):
        c = _canon(g)
        # keep the first nice-looking representative for each canonical key
        rep_by_canon.setdefault(c, g)

    canon_set = set(rep_by_canon.keys())
    return rep_by_canon, canon_set, display_set

rep_by_canon, canon_genres, display_genres = build_genre_vocab(df)

# Optional: print your discovered genres once to see what's available
# print("Known genres:", sorted(display_genres))

# ---------- Suggest nearest genres when there's no exact match ----------
def suggest_genres(user_input: str, rep_by_canon: dict, max_suggestions: int = 3):
    c = _canon(user_input)
    # Compare on canonical keys for robustness (handles spaces/hyphens)
    matches = difflib.get_close_matches(c, rep_by_canon.keys(), n=max_suggestions, cutoff=0.6)
    return [rep_by_canon[m] for m in matches]

# ---------- Prompt & validate: GENRE ----------
def get_valid_genre() -> str | None:
    """
    Loop until a valid genre is entered.
    - Normalizes input ('sci fi' -> 'Sci-Fi')
    - If no exact match, offers nearest suggestions
    - Return None if the user just presses Enter (to skip genre filtering)
    """
    while True:
        raw = input("Enter a genre (e.g., Drama) or press Enter to skip: ").strip()
        if raw == "":
            return None

        # Direct exact (canonical) match
        c = _canon(raw)
        if c in canon_genres:
            return rep_by_canon[c]

        # Token-level fallback (e.g., 'Crime Thriller' -> find 'Crime' or 'Thriller')
        tokens = [t for t in re.split(r"[,\s/]+", raw) if t]
        for t in tokens:
            ct = _canon(t)
            if ct in canon_genres:
                return rep_by_canon[ct]

        # Offer suggestions
        suggestions = suggest_genres(raw, rep_by_canon)
        if suggestions:
            print(f"Genre not found. Did you mean: {', '.join(suggestions)}?")
        else:
            print("Genre not found. Try a common genre (e.g., Drama, Comedy, Action, Sci-Fi).")

# ---------- Prompt & validate: YEAR ----------
def get_valid_year(df, year_col: str = "Released_Year") -> int | None:
    """
    Loop until a valid year is entered.
    - Return None if the user just presses Enter (to skip year filtering)
    """
    years = df[year_col].dropna().astype(int)
    y_min = max(1900, int(years.min())) if not years.empty else 1900
    y_max = int(years.max()) if not years.empty else 2100

    prompt = f"Enter a year between {y_min} and {y_max} or press Enter to skip: "

    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        if raw.isdigit():
            y = int(raw)
            if y_min <= y <= y_max:
                return y
        print(f"Invalid year. Please enter a number between {y_min} and {y_max}.")

# ---------- Example usage in your script ----------
genre = get_valid_genre()
year = get_valid_year(df)
print("Validated inputs ->", {"genre": genre, "year": year})

# ---------- Filter the dataframe ----------
filtered = df.copy()

# If user picked a genre, keep rows where that genre is in the list
if genre:
    filtered = filtered[filtered["Genre"].apply(lambda lst: genre in lst)]

# If user picked a year, keep rows with that year
if year:
    filtered = filtered[filtered["Released_Year"] == year]

# Handle case: no results
if filtered.empty:
    print("No movies found for that filter. Try again!")
else:
    # ---------- Summary stats ----------
    avg_rating = filtered["IMDB_Rating"].mean()
    print(f"\nFound {len(filtered)} films. Average rating: {avg_rating:.2f}\n")

    # ---------- Top 5 films ----------
    top5 = (
        filtered.sort_values(["IMDB_Rating", "No_of_Votes"], ascending=[False, False])
        .head(5)
        .loc[:, ["Series_Title", "Released_Year", "IMDB_Rating", "No_of_Votes"]]
    )

    # ---------- Pretty print ----------
    print("Top 5 films:")
    print(top5.to_string(index=False))
