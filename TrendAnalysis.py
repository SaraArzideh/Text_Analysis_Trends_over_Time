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

# PLOT 1
# Citations of Each of the Three Concepts per Year

# Function to calculate yearly citations for each concept
def yearly_citations_for_concept(concept):
    yearly_citations = scopus_df[scopus_df['Concepts'].str.contains(concept)].groupby('Year')['Cited by'].sum()
    return yearly_citations

# Calculate yearly citations for each concept
user_centred_citations = yearly_citations_for_concept('user-centred')
usability_citations = yearly_citations_for_concept('usability')
utility_citations = yearly_citations_for_concept('utility')

# Plot
sns.set_style(style="whitegrid")
plt.figure(figsize=(14, 7))
plt.rcParams.update({'font.size': 12})   # Adjust font size

plt.plot(user_centred_citations.index, user_centred_citations, label='User-Centred', linewidth=2, color='blue')
plt.plot(usability_citations.index, usability_citations, label='Usability', linewidth=2, color='red')
plt.plot(utility_citations.index, utility_citations, label='Utility', linewidth=2, color='green')

#sns.lineplot(data=citation_trends, x='Year', y='Cited by')
plt.title('Yearly citations for each concept', fontsize=16)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Citations', fontsize=14)
plt.xticks(rotation=45)
plt.legend()
plt.show()

# PLOT 2
# Changing Frequency of Each of the Three Concepts Over the Years

# Function to count occurrences of each concept per year
def count_concept_occurrences(concept):
    yearly_counts = scopus_df[scopus_df['Concepts'].str.contains(concept)].groupby('Year')['Concepts'].count()
    return yearly_counts

# Count occurrences for each concept
user_centred_counts = count_concept_occurrences('user-centred')
usability_counts = count_concept_occurrences('usability')
utility_counts = count_concept_occurrences('utility')

# Plot
sns.set_style(style="whitegrid")
plt.figure(figsize=(14, 7))
plt.rcParams.update({'font.size': 12})   # Adjust font size

plt.plot(user_centred_counts.index, user_centred_counts, label='User-Centred', linewidth=2, color='blue')
plt.plot(usability_counts.index, usability_counts, label='Usability', linewidth=2, color='red')
plt.plot(utility_counts.index, utility_counts, label='Utility', linewidth=2, color='green')

plt.title('Frequency of Each Concept Over the Years', fontsize=14)
plt.xlabel('Year', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.xticks(rotation=45)
plt.legend()
plt.show()

# PLOT 3
## 3D Graph Showing the Changes of Concepts Over the Years and Their Citation Frequencies

from mpl_toolkits.mplot3d import Axes3D

# Prepare data for 3D plot
years = sorted(scopus_df['Year'].unique())
x = range(len(years))

y1 = [yearly_citations_for_concept('user-centred').get(year, 0) for year in years]
y2 = [yearly_citations_for_concept('usability').get(year, 0) for year in years]
y3 = [yearly_citations_for_concept('utility').get(year, 0) for year in years]

# Plot
sns.set_style(style="whitegrid")
fig = plt.figure(figsize=(30, 10))
ax = fig.add_subplot(111, projection='3d')

plt.rcParams.update({'font.size': 10})  # font size

# Plot each concept as a separate line in the 3D space
ax.plot(x, y1, zs=2, zdir='y', label='User-Centred', linewidth=1.5, color='blue')
ax.plot(x, y2, zs=1, zdir='y', label='Usability', linewidth=1.5, color='red')
ax.plot(x, y3, zs=0, zdir='y', label='Utility', linewidth=1.5, color='green')

ax.set_xlabel('', fontsize=10)
ax.set_ylabel('', fontsize=10)
ax.set_zlabel('Citations', fontsize=10)
ax.set_yticks([0, 1, 2])
ax.set_yticklabels(['Utility', 'Usability', 'User-Centred'])

# Handling labels
label_fontsize = 10
display_years = range(0, len(years), 2)  # Adjust years step

ax.set_xticks(display_years)
ax.set_xticklabels([years[i] for i in display_years], rotation=90, fontsize=label_fontsize)

# Set the view angle
ax.view_init(elev=20, azim=120)

plt.title('3D View of Concept Citations Over Time', fontsize=12)
plt.legend()
plt.show()
