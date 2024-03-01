#Installing the necessary libraries by the following commands in terminl:
#pip install pandas  #for data manipulation
#pip install openpyxl  #for reading excel files
#pip install matplotlib  #for data visualisation

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

### Load data
scopus_df = pd.read_csv('FullScopusSource.csv')
thesaurus_df = pd.read_excel('thesaurus.xlsx')

### Data cleaning
scopus_df.dropna(subset=['Cited by', 'Title', 'Year'], inplace=True)

# Applying the thesaurus for data curing
for index, row in thesaurus_df.iterrows():
    scopus_df.replace(to_replace=row['Label'], value=row['Replace by'], inplace=True)

### Filtering articles based on concepts
#To filter articles that originally proposed a conceptualization of 
#'usability', 'utility', or 'user-centric', we can use string matching
#in the 'Title' or 'Abstract'or 'Author Keywords'columns. 
concepts = ['usability', 'utility', 'user-centric']

# Create a function that checks the presence of each concept in the 'Title', 'Abstract', and 'Author Keywords' columns 
def identify_concepts(row):
    # Initialize an empty list to store found concepts
    concepts_found = []

    # Iterate through each concept in a predefined list 'concepts'
    for concept in concepts:
        # Check if the concept is present in the 'Title', 'Abstract', or 'Author Keywords' of the row
        # The check is case-insensitive as it converts the text to lower case
        # Using str.lower() to handle NaN values
        if concept in str(row['Title']).lower() or concept in str(row['Abstract']).lower() or concept in str(row['Author Keywords']).lower():
            # If the concept is found, add it to the list 'concepts_found'
            concepts_found.append(concept)

    # Return the found concepts as a string, joined by commas
    return ', '.join(concepts_found)
# Add 'Concepts' column
# Applying the 'identify_concepts' function to each row of the DataFrame
scopus_df['Concepts'] = scopus_df.apply(identify_concepts, axis=1) 

#Filter condition
filter_condition = (
    scopus_df['Abstract'].str.contains('|'.join(concepts), case=False, na=False) |
    scopus_df['Title'].str.contains('|'.join(concepts), case=False, na=False) |
    scopus_df['Author Keywords'].str.contains('|'.join(concepts), case=False, na=False)
)
# Applying filter condition and sorting by 'Cited by' in descending order
filtered_articles = scopus_df[filter_condition].sort_values(by='Cited by', ascending=False)

## Saving the filtered articles 
filtered_articles.to_csv('filtered_articles.csv', index=False)

# Selecting the relevant columns
relevant_columns = filtered_articles[['Title', 'Year', 'Cited by', 'Concepts']]

# Save to CSV
relevant_columns.to_csv('filtered_articles_subset.csv', index=False)


### Analysing citation trends over time
# Group by year and sum citations
citation_trends = scopus_df.groupby('Year')['Cited by'].sum().reset_index()

# Plot
plt.figure(figsize=(10,6))
sns.lineplot(data=citation_trends, x='Year', y='Cited by')
plt.title('Citation Trends Over Time')
plt.xlabel('Year')
plt.ylabel('Total Citations')
plt.grid(True)
plt.show()
