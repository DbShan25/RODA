#libraries
import kaggle
import zipfile
import pandas as pd
import pymysql
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

# sql database connection function
def get_data(query):
    engine = create_engine("mysql+pymysql://root:root@127.0.0.1/project1_oda")
    df = pd.read_sql_query(query, engine)
    return df

# queries categorized into 3 different sections
queries = {
    "Key Highlights": {
        "Top-Selling Product": """select product_id, sum(selling_price) as revenue
        from df_orders group by product_id order by revenue desc limit 1;""",

        "Year-Over-Year (YoY) Sales Trends":"""select year(order_date) as year, 
        sum(selling_price) as total_revenue, sum(profit) as total_profit
        from df_orders group by year order by year;""",

        "Month-Over-Month (MoM) Sales Trends":"""with year_comparison as (
        select year(order_date) as year, month(order_date) as month, 
        sum(selling_price) as total_revenue, sum(profit) as total_profit
        from df_orders group by year, month )
        select month,
        sum(case when year=2022 then total_revenue else 0 end) as revenue_2022,
        sum(case when year=2023 then total_revenue else 0 end) as revenue_2023,
        sum(case when year=2022 then total_profit else 0 end) as profit_2022,
        sum(case when year=2023 then total_profit else 0 end) as profit_2023
        from year_comparison group by month order by month;"""
    },
    "Requested Insights": {
        "1. Top 10 highest revenue generating products": """select product_id, sum(selling_price) as revenue
        from df_orders group by product_id order by revenue desc limit 10 ;""",

        "2. Top 5 cities with the highest profit margins": """select ld.city, 
        sum(od.profit)/sum(od.selling_price)*100 as profit_margin
        from df_order_details od join df_location_details ld on ld.l_id=od.l_id
        group by ld.city order by profit_margin desc limit 5;""",

        "3. Total discount given for each category": """select category, sum(discount_price) as total_discount
        from df_orders group by category order by total_discount ;""",

        "4. Average sale price per product category": """select category, avg(selling_price) as avg_sale_price
        from df_orders group by category order by avg_sale_price;""",

        "5. Region with the highest average sale price": """select ld.region, 
        avg(od.selling_price) as avg_sale_price from df_location_details ld
        join df_order_details od on od.l_id=ld.l_id group by ld.region
        order by avg_sale_price desc limit 1;""",

        "6. Total profit per category": """select category, sum(profit) as total_profit
        from df_orders group by category order by total_profit;""",

        "7. Top 3 segments with the highest quantity of orders": """select segment, 
        sum(quantity) as total_quantity_of_orders from df_orders
        group by segment order by total_quantity_of_orders desc limit 3;""",

        "8. Average discount percentage given per region": """select ld.region, 
        avg(od.discount_percent) as avg_discount_percent from df_order_details od
        join df_location_details ld on ld.l_id=od.l_id group by ld.region order by avg_discount_percent;""",

        "9. Product category with the highest total profit": """select category, sum(profit) as total_profit
        from df_orders group by category order by total_profit desc limit 1;;""",
         
        "10. Total revenue generated per year": """select year(order_date) as year, 
        sum(selling_price) as total_revenue from df_orders group by year order by total_revenue;"""
    },
    "Additional Insights": {
        "1. Best-Selling Product in Each Category": """with rank_by_products as (select category, product_id, 
        SUM(quantity) AS total_quantity,
        rank() over (partition by category order by SUM(quantity) desc) as product_rank
        from df_order_details group by category, product_id) 
        select category, product_id, total_quantity from rank_by_products where product_rank=1;""",

        "2. Most Discounted Product Per Category": """with rank_by_products as(select category, product_id, 
        max(discount_price) AS max_discount,
        rank() over (partition by category order by max(discount_price) desc) as product_rank
        from df_order_details group by category, product_id)
        select category, product_id,max_discount from rank_by_products where product_rank=1;""",

        "3. Sales Growth of Each Category (Year-over-Year)": """with year_comparison as (select category, 
        year(order_date) as year, sum(selling_price) as total_sales
        from df_orders group by category, year)
        select category,
        sum(case when year=2022 then total_sales else 0 end) as sales_2022,
        sum(case when year=2023 then total_sales else 0 end) as sales_2023
        from year_comparison group by category order by category;""",

        "4. Most Profitable Customer Segment":"""select segment, sum(profit) as total_profit
        from df_orders group by segment order by total_profit desc limit 1;""",

        "5. Region with the Highest Total Discount":"""select ld.region, sum(od.discount_price) as total_discount
        from df_order_details od join df_location_details ld on ld.l_id = od.l_id
        group by ld.region order by total_discount desc limit 1;""",

        "6. Most Profitable Region":"""select ld.region, sum(od.profit) as total_profit
        from df_order_details od join df_location_details ld on ld.l_id = od.l_id
        group by ld.region order by total_profit desc limit 1;""",

        "7. Best Time for Sales (Month-wise)":"""select month(order_date) as month, 
        sum(selling_price) as total_sales from df_orders group by month
        order by total_sales desc limit 1;""",

        "8. Top 3 Products with the Highest Profit Margins":"""select product_id, 
        sum(profit) / sum(selling_price) * 100 as profit_margin
        from df_order_details group by product_id order by profit_margin desc limit 3;""",

        "9. Most Ordered Product in Each Region":"""with ranked_products as (select ld.region, od.product_id, 
        sum(od.quantity) as total_quantity,
        rank() over (partition by ld.region order by sum(od.quantity) desc) as product_rank
        from df_order_details od join df_location_details ld on ld.l_id = od.l_id
        group by ld.region, od.product_id)
        select region, product_id, total_quantity from ranked_products where product_rank = 1;""",

        "10. Subcategory with the Highest Profit Margin":"""select  sub_category, 
        sum(profit) / sum(selling_price) * 100 as profit_margin
        from df_orders group by sub_category order by profit_margin desc limit 1;"""
    }
}

# Function to customize graphs based on the selected query
def create_custom_chart(df, selected_insight):

    if selected_insight in ["Year-Over-Year (YoY) Sales Trends"]:
        # Create a grouped bar chart to compare Revenue & Profit YoY
        fig = px.bar(df, x="year", y=["total_revenue", "total_profit"],
                    title="Year-Over-Year (YoY) Sales Trends",
                    labels={"year": "Year", "value": "Amount ($)"},
                    barmode="group",
                    text_auto=True,
                    color_discrete_map={"total_revenue": "blue", "total_profit": "red"})

        # Improve layout
        fig.update_layout(xaxis_title="Year", yaxis_title="Amount ($)", legend_title="Metric")

        # Display the graph in Streamlit
        st.plotly_chart(fig)

    elif selected_insight in ["Month-Over-Month (MoM) Sales Trends"]:
        # Convert month numbers to month names for better readability
        df["month"] = pd.to_datetime(df["month"], format='%m').dt.strftime('%b')

        # Create visualization
        fig1 = px.line(df, x="month", y=["revenue_2022", "revenue_2023"],
                      markers=True, title="Monthly Revenue Comparison (2022 vs 2023)")
        fig1.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)", legend_title="Year")

        fig2 = px.line(df, x="month", y=["profit_2022", "profit_2023"],
                       markers=True, title="Monthly Profit Comparison (2022 vs 2023)")
        fig2.update_layout(xaxis_title="Month", yaxis_title="Profit ($)", legend_title="Year")

        # Display in Streamlit
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)

    elif selected_insight in ["3. Total discount given for each category", 
    "4. Average sale price per product category","6. Total profit per category",
    "7. Top 3 segments with the highest quantity of orders"]:
        # Pie Chart
        fig = px.pie(df, names=df.columns[0], values=df.columns[1], 
                     title=f"{selected_insight} Distribution")
        st.plotly_chart(fig)

    elif selected_insight in ["1. Top 10 highest revenue generating products",
    "2. Top 5 cities with the highest profit margins",
    "8. Average discount percentage given per region"]:
        #Bar Chart
        fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
                     title=f"{selected_insight} Trend", text_auto=True)
        st.plotly_chart(fig)

    #else:
        #st.warning(f"")

# Streamlit app
st.set_page_config(page_title="Retail Order Data Analysis", layout="wide")
st.title("Retail Order Data Analysis")
st.header("Business Insights Dashboard")

# Tabs for different insights
tab1, tab2, tab3 = st.tabs(["Key Highlights", "Requested Insights", "Additional Insights"])

# Function to display insights with customized graphs
def display_insights(di):
    selected_insight = st.selectbox("Select an Insight", list(queries[di].keys()))
    
    if selected_insight:
        st.subheader(selected_insight)
        df = get_data(queries[di][selected_insight])
        st.dataframe(df)
        
        # Display a customized graph based on the selected query
        create_custom_chart(df, selected_insight)

# Assign each tab to its respective category
with tab1:
    st.subheader("Key Highlights")
    display_insights("Key Highlights")

with tab2:
    st.subheader("Requested Insights")
    display_insights("Requested Insights")

with tab3:
    st.subheader("Additional Insights")
    display_insights("Additional Insights")
