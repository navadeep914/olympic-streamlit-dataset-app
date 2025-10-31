import streamlit as st
import pandas as pd

# Set page config for a wider layout
st.set_page_config(layout="wide")

st.title("🥇 Olympic Medal Data Analyzer")
st.write("Upload your tab-separated Olympic data file to see the analyses from your notebook.")

# File uploader
uploaded_file = st.file_uploader("Upload your Olympic data file", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        # Load the data as per the notebook's method
        df = pd.read_csv(uploaded_file, sep="\t", header=None)

        # Add correct Olympic headers
        df.columns = [
            "Athlete", "Age", "Country", "Year", "Date", "Sport",
            "Gold", "Silver", "Bronze", "Total"
        ]

        st.success("File uploaded and processed successfully!")

        st.header("Raw Olympic Data (Top 5 Rows)")
        st.dataframe(df.head())

        # --- Sidebar for Navigation ---
        st.sidebar.title("Select Analysis")
        analysis_options = [
            "Athlete with Most Gold Medals",
            "Country with Most Total Medals",
            "Total Medal Count per Year",
            "Medals per Country & Sport",
            "Sport with Most Medals",
            "Consistent Athletes (Multiple Olympics)",
            "Total Medals by Country (All Years)",
            "Medal Percentages (Gold/Silver/Bronze)",
            "Average Age & Age/Medal Correlation",
            "Year with Highest Gold Medals",
            "Top 10 Countries by Total Medals",
            "Country Dominating Swimming",
            "Youngest and Oldest Medal Winners",
            "Athletes with Only Bronze Medals",
            "Athletes in Multiple Sports",
            "Gold Medals by Country and Year (Pivot)"
        ]
        selected_analysis = st.sidebar.selectbox("Choose an analysis to display:", analysis_options)

        # --- Display Selected Analysis ---

        if selected_analysis == "Athlete with Most Gold Medals":
            st.subheader("Athlete with Most Gold Medals")
            top_gold = df[['Athlete','Gold']].sort_values('Gold', ascending=False).head(1)
            st.dataframe(top_gold)

        elif selected_analysis == "Country with Most Total Medals":
            st.subheader("Country with Most Total Medals (Top 5)")
            country_total = df.groupby('Country')['Total'].sum().sort_values(ascending=False)
            st.dataframe(country_total.head())

        elif selected_analysis == "Total Medal Count per Year":
            st.subheader("Total Medal Count per Year")
            medals_per_year = df.groupby('Year')['Total'].sum()
            st.bar_chart(medals_per_year)

        elif selected_analysis == "Medals per Country & Sport":
            st.subheader("Medals per Country & Sport")
            st.info("This can be a large table. Displaying the full grouped data.")
            country_sport = df.groupby(['Country','Sport'])[['Gold','Silver','Bronze']].sum()
            st.dataframe(country_sport)

        elif selected_analysis == "Sport with Most Medals":
            st.subheader("Sport with Most Medals (by Total Medals)")
            sport_total = df.groupby('Sport')['Total'].sum().sort_values(ascending=False)
            st.dataframe(sport_total)

        elif selected_analysis == "Consistent Athletes (Multiple Olympics)":
            st.subheader("Athletes in Multiple Olympics (Won medals in >1 year)")
            ath_years = df.groupby('Athlete')['Year'].nunique().reset_index()
            consistent = ath_years[ath_years['Year'] > 1].sort_values('Year', ascending=False)
            st.dataframe(consistent)

        elif selected_analysis == "Total Medals by Country (All Years)":
            st.subheader("Total Medals by Country (All Years)")
            total_country = df.groupby('Country')['Total'].sum().sort_values(ascending=False)
            st.dataframe(total_country)

        elif selected_analysis == "Medal Percentages (Gold/Silver/Bronze)":
            st.subheader("Overall Medal Percentages")
            totals = df[['Gold','Silver','Bronze']].sum()
            percentages = (totals / totals.sum()) * 100
            st.dataframe(percentages.to_frame(name='Percentage'))

            # Pie chart
            pie_data = pd.DataFrame({
                'Medal Type': totals.index,
                'Count': totals.values
            })
            st.vega_lite_chart(pie_data, {
                'title': 'Medal Distribution',
                'mark': {'type': 'arc', 'outerRadius': 120},
                'encoding': {
                    'theta': {'field': 'Count', 'type': 'quantitative', 'stack': True},
                    'color': {'field': 'Medal Type', 'type': 'nominal', 'title': 'Medal Type'},
                    'tooltip': ['Medal Type', 'Count', {'field': 'Count', 'type': 'quantitative', 'format': '.1%'}]
                }
            }, use_container_width=True)


        elif selected_analysis == "Average Age & Age/Medal Correlation":
            st.subheader("Average Age of Medal Winners")
            avg_age = df['Age'].mean()
            st.metric("Average Age", f"{avg_age:.2f}")

            st.subheader("Age vs. Total Medals (Correlation)")
            corr = df['Age'].corr(df['Total'])
            st.metric("Correlation Coefficient", f"{corr:.4f}")
            st.info("A value close to 0 (like this one) indicates a very weak linear relationship between age and total medals won.")

        elif selected_analysis == "Year with Highest Gold Medals":
            st.subheader("Total Gold Medals by Year")
            gold_year = df.groupby('Year')['Gold'].sum().sort_values(ascending=False)
            st.bar_chart(gold_year)

        elif selected_analysis == "Top 10 Countries by Total Medals":
            st.subheader("Top 10 Countries by Total Medals")
            country_compare = df.groupby('Country')['Total'].sum().sort_values(ascending=False)
            st.dataframe(country_compare.head(10))

        elif selected_analysis == "Country Dominating Swimming":
            st.subheader("Top 5 Countries in Swimming (by Total Medals)")
            # Make sure to catch all swimming-related sports
            swim = df[df['Sport'].str.contains('Swimming|Synchronized Swimming|Diving|Waterpolo', case=False, na=False)]
            swim_country = swim.groupby('Country')['Total'].sum().sort_values(ascending=False)
            st.dataframe(swim_country.head(5))

        elif selected_analysis == "Youngest and Oldest Medal Winners":
            st.subheader("Youngest Medal Winner(s)")
            youngest = df.loc[df['Age']==df['Age'].min(), ['Athlete','Age', 'Country', 'Sport', 'Year']].drop_duplicates()
            st.dataframe(youngest)

            st.subheader("Oldest Medal Winner(s)")
            oldest = df.loc[df['Age']==df['Age'].max(), ['Athlete','Age', 'Country', 'Sport', 'Year']].drop_duplicates()
            st.dataframe(oldest)

        elif selected_analysis == "Athletes with Only Bronze Medals":
            st.subheader("Athletes Who Won Only Bronze Medals")
            only_bronze = df[(df['Bronze']>0) & (df['Gold']==0) & (df['Silver']==0)]
            st.dataframe(only_bronze[['Athlete','Bronze', 'Country', 'Sport', 'Year']].head(100))
            st.info(f"Showing first 100 of {len(only_bronze)} athletes who fit this criteria.")

        elif selected_analysis == "Athletes in Multiple Sports":
            st.subheader("Athletes Who Won Medals in Multiple Sports")
            multi_sport_count = df.groupby('Athlete')['Sport'].nunique()
            multi_sport_athletes = multi_sport_count[multi_sport_count > 1].index
            
            # Get details for these athletes
            multi_sport_details = df[df['Athlete'].isin(multi_sport_athletes)][['Athlete', 'Sport', 'Year', 'Total']].drop_duplicates().sort_values('Athlete')
            st.dataframe(multi_sport_details)

        elif selected_analysis == "Gold Medals by Country and Year (Pivot)":
            st.subheader("Gold Medals by Country and Year")
            gold_pivot = df.pivot_table(index='Country', columns='Year', values='Gold', aggfunc='sum', fill_value=0)
            st.dataframe(gold_pivot)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        st.warning("Please ensure your file is tab-separated (sep='\\t') and has no header row, as per the notebook's code.")

else:
    st.info("Please upload a file to begin analysis.")
    st.subheader("File requirements:")
    st.write("- Must be a **tab-separated** file (e.g., .csv or .txt with tabs as delimiters).")
    st.write("- Must have **no header row**.")
    st.write("- Must have 10 columns in the correct order: `Athlete`, `Age`, `Country`, `Year`, `Date`, `Sport`, `Gold`, `Silver`, `Bronze`, `Total`.")
