# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """CHOOSE THE FRUITS THAT YOU WANT IN YOUR CUSTOME SMOOTHIE !"""
)

cnx = st.connection("snowflake")
session = cnx.session()

name_on_order = st.text_input("The Name on the Smoothie : ")
st.write("Smoothie Name : ", name_on_order)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True) # st is used to display the said content 

ingredients_list = st.multiselect(
    "CHOOSE UP TO 5 INGREDIENTS",
    my_dataframe,
    max_selections=5 
)

if ingredients_list: 
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit"+fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)


    my_insert_stmt = """ insert into smoothies.public.orders(name_on_order, ingredients)
        values ('""" + name_on_order + """', '""" + ingredients_string + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


