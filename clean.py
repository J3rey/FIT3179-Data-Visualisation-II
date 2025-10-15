import pandas as pd

# Load your dataset
df = pd.read_csv("athletes.csv")

# Count how many athletes are from each country
country_counts = df['country'].value_counts().reset_index()

# Rename columns for clarity
country_counts.columns = ['Country', 'Number_of_Athletes']

# Sort from highest to lowest
country_counts = country_counts.sort_values(by='Number_of_Athletes', ascending=False)

# Display top 10 countries
print(country_counts.head(10))

# Optionally export to CSV
country_counts.to_csv("country_athlete_counts.csv", index=False)
