#libraries
import kaggle
import zipfile
import pandas as pd
import pymysql
import streamlit as st

# db connection
connection = pymysql.connect(host="127.0.0.1",user="root",password="root",database="project1_oda"
                             ,cursorclass=pymysql.cursors.DictCursor
                             )
cursor = connection.cursor()

# Streamlit app
st.title("Retail Order Data Analysis")
st.header("Business Insights Dashboard")

# Tabs for different insights
tab1, tab2, tab3 = st.tabs(["Key Highlights", "Requested Insights", "Additional Insights"])

with tab1:
    st.subheader("Key Highlights")
    queries_kh={
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
    }
    selected_insight=st.selectbox("select an insight",list(queries_kh.keys()))
    cursor.execute(queries_kh[selected_insight])
    result = cursor.fetchall()
    df = pd.DataFrame(result)
    st.dataframe(df)

with tab2:
    st.subheader("Requested Insights")
    queries_ri={
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
    }
    selected_insight=st.selectbox("select an insight",list(queries_ri.keys()))
    cursor.execute(queries_ri[selected_insight])
    result = cursor.fetchall()
    df = pd.DataFrame(result)
    st.dataframe(df)

with tab3:
    st.subheader("Additional Insights")
    queries_ai={
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
    selected_insight=st.selectbox("select an insight",list(queries_ai.keys()))
    cursor.execute(queries_ai[selected_insight])
    result = cursor.fetchall()
    df = pd.DataFrame(result)
    st.dataframe(df)
