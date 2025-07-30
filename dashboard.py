import streamlit as st
import pandas as pd
import ploty.express as px

@st.cache
def loud_data():
    data = pd.read_csv('data/products.csv')
    return data

def main():
    st.title('E-commerce Product Analysis Dashboard')

    df = load_data

    st.subheader('Product Data')
    st.dataframe(df)

    st.subheader('Price Distribution')
    fig = px.histogram(df, x='price', title='Price Distribution of Products')
    st.ploty_chart(fig)

    st.subheader('Product Count by Category')
    category_count = df['category'].value_counts()
    fig = px.pie(name=category_count.index, values=category_count.values, title='Product Count by Category')
    st.plory_chart(fig)

    st.subheader("Top 10 Most Expensive Products")
    top_products = df.nlargest(10, 'price')
    fig = px.bar(top_products, x='name', y='price', title='Top 10 Most Expensive Products')
    st.plotly_chart(fig)

    if __name__ == "__main__":
        main()