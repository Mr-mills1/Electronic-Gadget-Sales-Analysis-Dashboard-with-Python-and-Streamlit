# import the libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# load the files 
@st.cache_data
def load_data(files):
    # read and concatenate CSV files
    dfs = [pd.read_csv(f) for f in files]
    df = pd.concat(dfs, ignore_index=True)
    # drop fully empty rows
    df.dropna(how='all', inplace=True)
    # remove duplicate header rows that appear in CSVs
    if 'Quantity Ordered' in df.columns:
        df = df[df['Quantity Ordered'].astype(str).str.isdigit()]
        df['Quantity Ordered'] = df['Quantity Ordered'].astype(int)
    if 'Price Each' in df.columns:
        df = df[df['Price Each'].astype(str).str.replace(',','').str.isdigit()]
        df['Price Each'] = df['Price Each'].astype(float)
    # parse dates
    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    # derived columns or create olumns
    df['Month'] = df['Order Date'].dt.month_name()
    df['Day'] = df['Order Date'].dt.day_name()
    df['Order Time'] = df['Order Date'].dt.time
    df['Amount'] = (df['Quantity Ordered'] * df['Price Each']).round(2)
    # extract city from address (assumes format '123 Some St, City, State ZIP')
    df['City'] = df['Purchase Address'].astype(str).apply(lambda x: x.split(',')[-2].strip() if ',' in x else x)
    return df

# create title and dashboard heading
def main():
    st.set_page_config(page_title='Electronics Sales Dashboard', layout='wide')
    st.title('Electronics Gadget Sales Analysis')

    # files found in workspace (same names as in the notebook)
    files = [
        'Sales_April_2019.csv',
        'Sales_August_2019.csv',
        'Sales_December_2019.csv',
        'Sales_February_2019.csv',
        'Sales_January_2019.csv',
        'Sales_July_2019.csv',
        'Sales_June_2019.csv',
        'Sales_March_2019.csv',
        'Sales_May_2019.csv',
        'Sales_November_2019.csv',
        'Sales_October_2019.csv',
        'Sales_September_2019.csv'
    ]
# load files in streamlit
    df = load_data(files)

    # Add Sidebar filters to the left
    st.sidebar.header('Filters Pane')
    months = ['All'] + sorted(df['Month'].dropna().unique(), key=lambda x: pd.to_datetime(x, format='%B').month)
    month_sel = st.sidebar.selectbox('Month', months)
    cities = ['All'] + sorted(df['City'].dropna().unique())
    city_sel = st.sidebar.selectbox('City', cities)
    products = ['All'] + sorted(df['Product'].dropna().unique())
    product_sel = st.sidebar.selectbox('Product', products)

    # apply filters
    mask = pd.Series(True, index=df.index)
    if month_sel != 'All':
        mask &= df['Month'] == month_sel
    if city_sel != 'All':
        mask &= df['City'] == city_sel
    if product_sel != 'All':
        mask &= df['Product'] == product_sel
    df_f = df[mask]

    # Key metrics or KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total Products', int(df_f['Product'].nunique()))
    with col2:
        st.metric('Number of Cities', int(df_f['City'].nunique()))
    with col3:
        st.metric('Quantity Ordered', int(df_f['Quantity Ordered'].sum()))
    with col4:
        st.metric('Revenue', f"${df_f['Amount'].sum():,.2f}")
# add a markdown text
    st.markdown('---')

    # Monthly sales trend
    mon = df_f.groupby('Month')['Amount'].sum().reindex(
        ['January','February','March','April','May','June','July','August','September','October','November','December']
    ).fillna(0)
    fig_mon = px.bar(x=mon.index, y=mon.values, labels={'x':'Month','y':'Total Amount'}, title='Monthly Sales Trend')
    st.plotly_chart(fig_mon, use_container_width=True)

    # Weekly trend
    weekly = df_f.groupby('Day')['Amount'].sum().reindex(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    ).fillna(0)
    fig_week = px.line(x=weekly.index, y=weekly.values, labels={'x':'Day','y':'Total Amount'}, title='Weekly Sales Trend', markers=True)
    st.plotly_chart(fig_week, use_container_width=True)

    # Product performance
    per = df_f.groupby('Product')[['Amount','Quantity Ordered']].sum().sort_values(by='Quantity Ordered', ascending=False)
    if not per.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=per.index, y=per['Amount'], name='Amount', marker_color='green'))
        fig.add_trace(go.Bar(x=per.index, y=per['Quantity Ordered'], name='Quantity Ordered', marker_color='red'))
        fig.update_layout(barmode='group', title='Product Sales Performance', xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Sales by city
    city_tbl = df_f.groupby(['City','Product'])['Amount'].sum().unstack(fill_value=0)
    if not city_tbl.empty:
        st.subheader('Sales by City and Product')
        st.dataframe(city_tbl.style.format('${:,.2f}'))

    # show raw data
    st.markdown('---')
    st.subheader('Raw Data (filtered)')
    st.dataframe(df_f.reset_index(drop=True))

    # provide a download button for filtered data
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button('Download filtered CSV', csv, file_name='filtered_sales.csv', mime='text/csv')


# if __name__ == '__main__':
#     main()
