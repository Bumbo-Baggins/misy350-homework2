import streamlit as st
import json
from pathlib import Path
import uuid

st.set_page_config(page_title="Smart Coffee Kiosk", layout="centered")
st.title("Smart Coffee Kiosk System")

if "orders" not in st.session_state:
    st.session_state["orders"] = []

# Loading Data 
json_file = Path("inventory.json")

if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    # Default data if file doesn't exist
    inventory = [] 

# Helper function for Saving Data
def save_inventory():
    with open(json_file, "w") as f:
        json.dump(inventory, f, indent=4)

# UI Structure & Navigation
tab1, tab2, tab3, tab4 = st.tabs([
    "Place Order", 
    "View Inventory", 
    "Restock", 
    "Manage Orders"
])

with tab1:
    st.subheader("Place Order")
    # Code for creating orders goes here

with tab2:
    st.subheader("View Inventory")
    # Code for reading inventory goes here

with tab3:
    st.subheader("Restock")
    # Code for updating inventory goes here

with tab4:
    st.subheader("Manage Orders")
    # Code for deleting/canceling orders goes here