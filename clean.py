import pandas as pd

# Load the CSV file
file_path = "medallists.csv"  # change path if needed
df = pd.read_csv(file_path)

# Group and count medals by country
medal_counts = (
    df.groupby(['country_long', 'country_code', 'medal_type'])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# Rename columns for clarity
medal_counts.columns.name = None
medal_counts = medal_counts.rename(columns={
    'country_long': 'Country',
    'country_code': 'Code',
    'Gold Medal': 'Gold',
    'Silver Medal': 'Silver',
    'Bronze Medal': 'Bronze'
})

# Add total medal count
medal_counts['Total Medals'] = medal_counts[['Gold', 'Silver', 'Bronze']].sum(axis=1)

# Reorder columns
medal_counts = medal_counts[['Country', 'Code', 'Total Medals', 'Gold', 'Silver', 'Bronze']]

# Display the first few rows
print(medal_counts.head(10))

# Optional: save to CSV
medal_counts.to_csv("cleaned_medals.csv", index=False)
