# Import necessary packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import hashlib

# Streamlit app title
st.title(":cup_with_straw: Customize Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# ✅ Get Snowflake session safely
try:
    session = get_active_session()
except:
    st.error("❌ Could not establish a Snowflake session. Please check your connection.")
    st.stop()

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

    # ✅ Use SHA-256 hashing (Snowflake-compatible) and store as a STRING
    def snowflake_compatible_hash(text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()  # Store as a hex string

    hash_value = snowflake_compatible_hash(ordered_ingredients)
    st.write("Computed Hash:", hash_value)

    # Display nutrition information for selected fruits
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        st.write(f"The search value for {fruit_chosen} is {search_on}")

        # Fetch nutrition info from external API
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"⚠️ Failed to fetch data for {fruit_chosen}.")

    # ✅ Use parameterized query to prevent SQL injection
    insert_query = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order, hash_ing)
        VALUES (?, ?, ?)
    """
    
    # Display the query (for debugging)
    st.write("Generated SQL Query:", insert_query)

    # Submit order button
    if st.button('Submit Order'):
        session.sql(insert_query, params=(ordered_ingredients, name_on_order, hash_value)).collect()
        st.success(f'Your Smoothie is ordered! **{name_on_order}** ✅')
