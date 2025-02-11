# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie !"""
)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input("Name of the Smoothie")
st.write("The name on your smoothie will be : ", name_on_order)

# Fetch data from Snowflake
my_dataframe = session.table("smoothies.public.FRUIT_OPTIONS").select(col('FRUIT_NAME'), col(''))
st.dataframe(data=my_dataframe, use_container_width=True)

# Convert Snowpark dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()  # FIXED TYPO

# Show converted dataframe for debugging
#st.dataframe(pd_df)

# Extract list of fruit names for selection
fruit_list = pd_df['FRUIT_NAME'].tolist()  # FIXED MULTISELECT ISSUE



# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,  # FIXED: Pass only fruit names
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ', '  # Proper formatting
        
        # Get 'SEARCH_ON' value for the selected fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Debugging output
        st.write(f"The search value for {fruit_chosen} is {search_on}")

        # Fetch nutrition info
       smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        # Ensure API response is valid before displaying
        if smoothiefroot_response.status_code == 200:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

    st.write("Selected Ingredients: ", ingredients_string)

    # Insert order into Snowflake
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")
