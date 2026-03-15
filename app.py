import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

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

    # 1. Select Item
    item_names = []
    for item in inventory:
        item_names.append(item["name"])
    
    selected_name = st.selectbox("Select a drink", item_names)

    # Match the selected name back to the dictionary
    selected_item = {}
    for item in inventory:
        if item["name"] == selected_name:
            selected_item = item
            break

    # 2. Quantity
    quantity = st.number_input("Quantity", min_value=1, step=1)

    # 3. Customer Name
    customer_name = st.text_input("Customer Name")

    # 4. Action
    btn_submit = st.button("Submit Order", type="primary")

    if btn_submit:
        if not customer_name:
            st.warning("Customer name is required.")
        else:
            if selected_item["stock"] >= quantity:
                # Reduce stock
                selected_item["stock"] -= quantity
                
                # Calculate total price
                total_price = selected_item["price"] * quantity
                
                # Create order dictionary
                new_order = {
                    "order_id": str(uuid.uuid4()),
                    "customer": customer_name,
                    "item": selected_item["name"],
                    "quantity": quantity,
                    "total": total_price,
                    "status": "Placed"
                }
                
                # Append to orders list
                st.session_state["orders"].append(new_order)
                
                # Save the updated inventory back to JSON
                save_inventory()
                
                # Show success message
                st.success("Order Placed Successfully!")
                
                # Receipt display
                with st.expander("Receipt Details", expanded=True):
                    st.write(f"**Order ID:** {new_order['order_id']}")
                    st.write(f"**Customer Name:** {new_order['customer']}")
                    st.write(f"**Item:** {new_order['item']} (Qty: {new_order['quantity']})")
                    st.write(f"**Total:** ${new_order['total']:.2f}")
                    st.write(f"**Status:** {new_order['status']}")
            else:
                st.error("Out of Stock")

with tab2:
    st.subheader("View & Search Inventory")

    # 1. Search input
    search_query = st.text_input("Search item by name", "").lower()

    filtered_items = []
    total_items = 0

    # Filter inventory and calculate totals
    for item in inventory:
        total_items += item["stock"]

        if search_query in item["name"].lower():
            # Bonus: Highlight low stock
            item_display = item.copy()
            if item_display["stock"] < 10:
                item_display["Status"] = "LOW STOCK"
            else:
                item_display["Status"] = "OK"
            
            filtered_items.append(item_display)

    # 2. Metrics display
    st.metric(label="Total Items in Stock", value=total_items)

    # 3. Display inventory table
    if filtered_items:
        st.dataframe(filtered_items, use_container_width=True)
    else:
        st.info("No matching items found.")

with tab3:
    st.subheader("Restock Items")

    # 1. Selection
    item_titles = []
    for item in inventory:
        item_titles.append(item["name"])

    selected_restock_name = st.selectbox("Select item to restock", item_titles, key="restock_select")

    restock_item = {}
    for item in inventory:
        if item["name"] == selected_restock_name:
            restock_item = item
            break

    # 2. New Stock Input
    current_stock = restock_item.get("stock", 0)
    st.write(f"Current Stock: **{current_stock}**")
    
    added_stock = st.number_input("Amount to add", min_value=1, step=1, key="restock_amount")

    # 3. Action
    btn_restock = st.button("Update Stock", type="primary", key="restock_btn")

    if btn_restock:
        with st.spinner("Updating inventory..."):
            time.sleep(1) 
            
            # Update the item's stock
            restock_item["stock"] += added_stock
            
            # Save to JSON
            save_inventory()
            
            st.success(f"Successfully added {added_stock} units of {restock_item['name']}!")
            time.sleep(1.5)
            st.rerun()

with tab4:
    st.subheader("Manage Active Orders")

    # 1. View Orders
    active_orders = []
    for order in st.session_state["orders"]:
        if order.get("status") != "Cancelled":
            active_orders.append(order)

    if not active_orders:
        st.info("No active orders.")
    else:
        st.dataframe(active_orders, use_container_width=True)

        st.markdown("### Cancel an Order")
        
        # 2. Selection
        order_options = []
        for order in active_orders:
            order_options.append(f"{order['order_id']} - {order['customer']} ({order['item']})")

        selected_order_str = st.selectbox("Select order to cancel", order_options)

        # 3. Action
        if st.button("Cancel Order", type="primary"):
            with st.spinner("Processing cancellation..."):
                time.sleep(1)
                
                # Find the specific order dictionary
                selected_order = {}
                for order in active_orders:
                    if selected_order_str.startswith(order['order_id']):
                        selected_order = order
                        break

                # Change status to Cancelled
                selected_order["status"] = "Cancelled"

                # Refund stock to inventory
                for item in inventory:
                    if item["name"] == selected_order["item"]:
                        item["stock"] += selected_order["quantity"]
                        break

                # Save updated inventory to JSON
                save_inventory()

                st.success("Order Cancelled and Stock Refunded")
                time.sleep(1.5)
                st.rerun()

    