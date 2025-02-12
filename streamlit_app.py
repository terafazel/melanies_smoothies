# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# User input for smoothie name
name_on_order = st.text_input("Name of the Smoothie")
st.write("The name on your smoothie will be:", name_on_order)

# Fetch data from Snowflake
my_dataframe = session.table("smoothies.public.FRUIT_OPTIONS").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Extract list of fruit names for selection
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,
)

if ingredients_list:
    # ✅ Sort, lowercase, and format ingredients correctly for hashing
    ordered_ingredients = ", ".join(sorted(ingredients_list)).strip().lower()
    
    # Display selected ingredients
    st.write("Selected Ingredients:", ordered_ingredients)

    # ✅ Compute HASH using Snowflake SQL for consistency
    hash_query = session.sql(f"SELECT SHA2('{ordered_ingredients}', 256)").collect()
    hash_value = hash_query[0][0] if hash_query else None

    st.write("Computed Hash (Snowflake-generated):", hash_value)

    # Nutrition information
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        st.write(f"The search value for {fruit_chosen} is {search_on}")

        # Fetch nutrition info
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

    # Insert order into Snowflake
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, hash_ing)
        VALUES (?, ?, ?)
    """
    
    # ✅ Use parameterized query to prevent SQL injection
    session.sql(my_insert_stmt, [ordered_ingredients, name_on_order.lower(), hash_value]).collect()
    
    st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")
