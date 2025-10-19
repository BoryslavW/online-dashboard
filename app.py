import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io  # For in-memory file handling

# Streamlit app title and file uploader
st.title("Company Data Analyzer")
st.markdown("Upload a CSV file with columns: company_name, focus, sector, region, size.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)

    # Your cleaning logic
    df = df.drop_duplicates(subset=['company_name'])

    df.fillna({
        'focus': 'Unknown',
        'sector': 'Unknown',
        'region': 'Unknown',
        'size': 'Unknown'
    }, inplace=True)
    df = df.dropna(how='all', subset=['sector', 'region', 'size'])

    for col in ['focus', 'sector', 'region', 'size']:
        df[col] = df[col].astype(str).str.lower().str.strip()

    valid_sizes = ['1-10', '11-50', '51-200', '201-500', '501-1k', 'unknown']
    df['size'] = df['size'].apply(lambda x: x if x in valid_sizes else 'unknown')

    def categorize_size(size):
        if size in ['1-10', '11-50']:
            return 'Small'
        elif size in ['51-200', '201-500']:
            return 'Medium'
        elif size in ['501-1k']:
            return 'Large'
        else:
            return 'Unknown'

    df['size_category'] = df['size'].apply(categorize_size)

    df['country'] = df['region'].apply(lambda x: x.split(',')[-1].strip() if ',' in x else x)

    # Analysis
    sector_counts = df['sector'].value_counts().reset_index(name='count').head(10)
    region_counts = df['region'].value_counts().reset_index(name='count').head(10)
    size_dist = df['size_category'].value_counts().reset_index(name='count')

    # Display summary stats
    st.subheader("Summary Stats")
    st.dataframe(df.describe(include='all'))

    # Display tables
    st.subheader("Top 10 Sectors by Company Count")
    st.dataframe(sector_counts)

    st.subheader("Region Counts")
    st.dataframe(region_counts)

    # Generate and display plots (using Streamlit's image display)
    st.subheader("Visualizations")

    # Top 10 Sectors Bar Plot
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='count', y='sector', data=sector_counts, ax=ax1)
    ax1.set_title('Top 10 Sectors by Company Count')
    ax1.set_xlabel('Count')
    ax1.set_ylabel('Sector')
    plt.tight_layout()
    st.pyplot(fig1)

    # Top 5 Countries Pie Chart
    country_counts = df['country'].value_counts().head(5)
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.pie(country_counts, labels=country_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Top 5 Countries Distribution')
    plt.tight_layout()
    st.pyplot(fig2)

    # Size Category Histogram
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    sns.histplot(df['size_category'], kde=False, ax=ax3)
    ax3.set_title('Company Size Category Distribution')
    ax3.set_xlabel('Size Category')
    ax3.set_ylabel('Count')
    plt.tight_layout()
    st.pyplot(fig3)

    # Save and offer download for cleaned CSV
    cleaned_csv = io.StringIO()
    df.to_csv(cleaned_csv, index=False)
    st.download_button(
        label="Download Cleaned CSV",
        data=cleaned_csv.getvalue(),
        file_name="cleaned_company_data.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload a CSV file to analyze.")