import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# Streamlit App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

# Snowflake Connection Parameters
connection_params = {
account = "QOMIVUF-VZB86613"
user = "SHAKIB"
password = "Kshazam26@"
role = "SYSADMIN"
warehouse = "COMPUTE_WH"
database = "SMOOTHIES"
schema = "PUBLIC"
}

# Establishing Snowflake Session
try:
    session = Session.builder.configs(connection_params).create()
    st.success("✅ Connected to Snowflake successfully!")
except Exception as e:
    st.error(f"❌ Snowflake connection failed: {e}")
    st.stop()

# Fetch fruit options from Snowflake
try:
    my_dataframe = session.table("smoothies.public.FRUIT_OPTIONS").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# Get fruit list for selection
fruit_list = pd_df['FRUIT_NAME'].tolist()

# User input for smoothie name
name_on_order = st.text_input("Name of the Smoothie")

# Multi-select for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients", fruit_list)

# Order Processing
if ingredients_list:
    ordered_ingredients = ", ".join(sorted(ingredients_list)).strip().lower()
    st.write("Selected Ingredients:", ordered_ingredients)

    # Submit Order Button
    if st.button('Submit Order'):
        try:
            session.sql(f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ordered_ingredients}', '{name_on_order}')
            """).collect()
            st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")
        except Exception as e:
            st.error(f"❌ Order submission failed: {e}")
