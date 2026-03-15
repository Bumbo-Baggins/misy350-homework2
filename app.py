import streamlit as st
import json
from pathlib import Path
import uuid
import time

st.set_page_config(page_title="Smart Coffee Kiosk", layout="centered")
st.title("Smart Coffee Kiosk System")

if "orders" not in st.session_state:
    st.session_state["orders"] = []

json_file = Path("inventory.json")

if json_file.exists():
    with json_file.open("r", encoding="utf-8") as f:
        inventory = json.load(f)
else:
    inventory = [] 

def save_inventory():
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4)

tab1, tab2, tab3, tab4 = st.tabs([
    "Place Order", 
    "View Inventory", 
    "Restock", 
    "Manage Orders"
])

with tab1:
    st.subheader("Place Order")

    item_names = []
    for item in inventory:
        item_names.append(item["name"])
    
    selected_name = st.selectbox("Select a drink", item_names)

    selected_item = {}
    for item in inventory:
        if item["name"] == selected_name:
            selected_item = item
            break

    quantity = st.number_input("Quantity", min_value=1, step=1)
    customer_name = st.text_input("Customer Name")

    btn_submit = st.button("Submit Order", type="primary")

    if btn_submit:
        if not customer_name:
            st.warning("Customer name is required.")
        else:
            if selected_item["stock"] >= quantity:
                selected_item["stock"] -= quantity
                total_price = selected_item["price"] * quantity
                
                new_order = {
                    "order_id": str(uuid.uuid4()),
                    "customer": customer_name,
                    "item": selected_item["name"],
                    "quantity": quantity,
                    "total": total_price,
                    "status": "Placed"
                }
                
                st.session_state["orders"].append(new_order)
                save_inventory()
                
                st.success("Order Placed Successfully!")
                
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

    search_query = st.text_input("Search item by name", "").lower()

    filtered_items = []
    total_items = 0

    for item in inventory:
        total_items += item["stock"]

        if search_query in item["name"].lower():
            item_display = item.copy()
            if item_display["stock"] < 10:
                item_display["Status"] = "LOW STOCK"
            else:
                item_display["Status"] = "OK"
            
            filtered_items.append(item_display)

    st.metric(label="Total Items in Stock", value=total_items)

    if filtered_items:
        st.dataframe(filtered_items, use_container_width=True)
    else:
        st.info("No matching items found.")

with tab3:
    st.subheader("Restock Items")

    restock_names = []
    for item in inventory:
        restock_names.append(item["name"])

    selected_restock_name = st.selectbox("Select item to restock", restock_names, key="restock_select")

    restock_item = {}
    for item in inventory:
        if item["name"] == selected_restock_name:
            restock_item = item
            break

    current_stock = restock_item.get("stock", 0)
    st.write(f"Current Stock: **{current_stock}**")
    
    added_stock = st.number_input("Amount to add", min_value=1, step=1, key="restock_amount")

    btn_restock = st.button("Update Stock", type="primary", key="restock_btn")

    if btn_restock:
        with st.spinner("Updating inventory..."):
            time.sleep(1) 
            
            restock_item["stock"] += added_stock
            save_inventory()
            
            st.success(f"Successfully added {added_stock} units of {restock_item['name']}!")
            time.sleep(1.5)
            st.rerun()

with tab4:
    st.subheader("Manage Active Orders")

    active_orders = []
    for order in st.session_state["orders"]:
        if order.get("status") != "Cancelled":
            active_orders.append(order)

    if not active_orders:
        st.info("No active orders.")
    else:
        st.dataframe(active_orders, use_container_width=True)

        st.markdown("### Cancel an Order")
        
        order_options = []
        for order in active_orders:
            order_options.append(f"{order['order_id']} - {order['customer']} ({order['item']})")

        selected_order_str = st.selectbox("Select order to cancel", order_options)

        if st.button("Cancel Order", type="primary"):
            with st.spinner("Processing cancellation..."):
                time.sleep(1)

                selected_order = {}
                for order in active_orders:
                    if selected_order_str.startswith(order['order_id']):
                        selected_order = order
                        break

                selected_order["status"] = "Cancelled"

                for item in inventory:
                    if item["name"] == selected_order["item"]:
                        item["stock"] += selected_order["quantity"]
                        break

                save_inventory()

                st.success("Order Cancelled and Stock Refunded")
                time.sleep(1.5)
                st.rerun()