# Import necessary packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")

# Get the active Snowflake session
session = get_active_session()

# Fetch all unfilled (ORDER_FILLED = FALSE) orders
pending_orders = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == False).collect()

# Show pending orders in a table
if pending_orders:
    st.write("### Pending Orders")
    editable_df = st.data_editor(pending_orders)

    # Select an order to mark as completed
    selected_order = st.selectbox("Select an order to mark as filled:", [row["NAME_ON_ORDER"] for row in pending_orders])

    if selected_order:
        if st.button("Mark as Completed ✅"):
            session.sql("""
                UPDATE smoothies.public.orders 
                SET ORDER_FILLED = TRUE 
                WHERE NAME_ON_ORDER = ?
            """, [selected_order]).collect()

            st.success(f"Order for **{selected_order}** marked as completed!")
            st.rerun()  # Correct function for rerunning the app
else:
    st.write("✅ No pending orders! The kitchen is all caught up.")
