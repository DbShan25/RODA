# RODA
Retail Order Data Analysis

Using Kaggle Api, Python, SQL, Streamlit to analyze and optimize sales performance by identifying key trends, top-performing products, and growth opportunities using a dataset of sales transactions.
Data set is downloaded from: !kaggle datasets download ankitbansal06/retail-orders -f orders.csv
Extracted zip file using python code in Jupyter Notebook.
Used Pandas DataFrame to do the below.
  -Read the extracted file
  -Replace the missing values
  -Standardize the column names for clarity and SQL compatibility
  -Calculating new fields discount , sale price and profit
  -Converting datetime field from text
  -Splitted into 2 different DataFrames, One with Order details and other with location details.
  -Imported the oridinal dataframe and 2 splitted data frame to SQL database creating new Database and required tables.
  -Created a foreign key link to the splitted dataframes.
Queried Key Highlights, Requested Insights and Additional Insights using SQL queries.
Displayed the data in StreamLit UI with Data Table/Chart for the SQL queries.
