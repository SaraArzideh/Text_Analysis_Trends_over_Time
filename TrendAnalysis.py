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
concept_groups = {
    'user-centred': ["user-centered", "user-centred", "user centered", "user-centric", "user centric", "user-centeric"],
    'usability': ["usability", "usabilities"],
    'utility': ["utility", "Utility", "utilities", "Utilities"]
}

# Create a function that checks the presence of each concept in the 'Title', 'Abstract', and 'Author Keywords' columns 
def identify_concepts(row):
    # Initialize an empty list to store found concepts
    concepts_found = set()
    # Iterate through each concept group
    for standard_concept, variations in concept_groups.items():
        # Check each variation in 'Title', 'Abstract', and 'Author Keywords'
        for variation in variations:
            # Using str.lower() to handle case-insensitive and NaN values
            if variation.lower() in str(row['Title']).lower() or variation.lower() in str(row['Abstract']).lower() or variation.lower() in str(row['Author Keywords']).lower():
                concepts_found.add(standard_concept)
                break  # Stop searching after finding one variation of the concept

    # Return the found concepts as a string, joined by commas
    return ', '.join(concepts_found)

## Add 'Concepts' column
# Applying the 'identify_concepts' function to each row of the DataFrame
scopus_df['Concepts'] = scopus_df.apply(identify_concepts, axis=1) 

# Filter condition
filter_condition = (
    scopus_df['Abstract'].str.contains('|'.join(concept_groups), case=False, na=False) |
    scopus_df['Title'].str.contains('|'.join(concept_groups), case=False, na=False) |
    scopus_df['Author Keywords'].str.contains('|'.join(concept_groups), case=False, na=False)
)
# Applying filter condition and sorting by 'Cited by' in descending order
filtered_articles = scopus_df[filter_condition].sort_values(by='Cited by', ascending=False)

## Saving the filtered articles 
filtered_articles.to_csv('filtered_articles.csv', index=False)

# Selecting the relevant columns
relevant_columns = filtered_articles[['Title', 'Year', 'Cited by', 'Concepts', 'Author Keywords','Abstract' ]]

# Save to CSV
relevant_columns.to_csv('filtered_articles_subset.csv', index=False)


### Analysing citation trends over time
# Group by year and sum citations
citation_trends = scopus_df.groupby('Year')['Cited by'].sum().reset_index()

# Plots

# Function to calculate yearly citations for each concept
def yearly_citations_for_concept(concept):
    yearly_citations = scopus_df[scopus_df['Concepts'].str.contains(concept)].groupby('Year')['Cited by'].sum()
    return yearly_citations

# Calculate yearly citations for each concept
user_centred_citations = yearly_citations_for_concept('user-centred')
usability_citations = yearly_citations_for_concept('usability')
utility_citations = yearly_citations_for_concept('utility')

# Plot
plt.figure(figsize=(12, 6))
plt.plot(user_centred_citations.index, user_centred_citations, label='User-Centred')
plt.plot(usability_citations.index, usability_citations, label='Usability')
plt.plot(utility_citations.index, utility_citations, label='Utility')
#sns.lineplot(data=citation_trends, x='Year', y='Cited by')
plt.title('Yearly citations for each concept')
plt.xlabel('Year')
plt.ylabel('Citations')
plt.legend()
plt.show()
