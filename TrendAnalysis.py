#Installing the necessary libraries by the following commands in terminl:
#pip install pandas  #for data manipulation
#pip install openpyxl  #for reading excel files
#pip install matplotlib  #for data visualisation

import pandas as pd

# Load data
scopus_df = pd.read_csv('FullScopusSource.csv')
thesaurus_df = pd.read_excel('thesaurus.xlsx')

# Data cleaning
scopus_df.dropna(subset=['Cited by', 'Title', 'Year'], inplace=True)

# Applying the thesaurus for data curing
for index, row in thesaurus_df.iterrows():
    scopus_df.replace(to_replace=row['Label'], value=row['Replace by'], inplace=True)

# Identifying most cited articles
# Sort data by 'Cited by' in descending order
most_cited_articles = scopus_df.sort_values(by='Cited by', ascending=False)
  
#Filtering articles based on concepts
#To filter articles that originally proposed a conceptualization of 
#'usability', 'utility', or 'user-centric', we can use string matching
#in the 'Title' or 'Abstract'or 'Author Keywords'columns. 
concepts = ['usability', 'utility', 'user-centric']
filtered_articles = most_cited_articles[most_cited_articles['Abstract'].str.contains('|'.join(concepts), case=False, na=False)]
filtered_articles = most_cited_articles[most_cited_articles['Title'].str.contains('|'.join(concepts), case=False, na=False)]
filtered_articles = most_cited_articles[most_cited_articles['Author Keywords'].str.contains('|'.join(concepts), case=False, na=False)]

## Analysing citation trends changes over the time
import matplotlib.pyplot as plt
import seaborn as sns

# Group by year and sum citations
citation_trends = scopus_df.groupby('Year')['Cited by'].sum().reset_index()

# Plot
plt.figure(figsize=(10,6))
sns.lineplot(data=citation_trends, x='Year', y='Cited by')
citation_trends.plot(kind='line')
plt.title('Citation Trends Over Time')
plt.xlabel('Year')
plt.ylabel('Total Citations')
plt.grid(True)
plt.show()
