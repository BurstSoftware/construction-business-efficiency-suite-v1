import streamlit as st
import pandas as pd
import qrcode
from PIL import Image
import io
import base64
from datetime import datetime
import os

# Set page configuration
st.set_page_config(page_title="Construction Business Efficiency Suite", layout="wide")

# Initialize session state for data persistence
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'contractors' not in st.session_state:
    st.session_state.contractors = []
if 'receipts' not in st.session_state:
    st.session_state.receipts = []
if 'invoices' not in st.session_state:
    st.session_state.invoices = []

# Sidebar for navigation
st.sidebar.title("Construction Suite")
app_mode = st.sidebar.selectbox("Select Module", [
    "Project Cost Estimator",
    "Contractor Management",
    "Invoice Generator",
    "Receipts Input",
    "QR Code Generator"
])

# Title
st.title("Construction Business Efficiency Suite")

# Helper functions
def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file.name
    return None

def generate_qr_code(data, filename="qr_code.png"):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)
    return filename

def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

# Module 1: Project Cost Estimator
if app_mode == "Project Cost Estimator":
    st.header("Comprehensive Project Cost Estimator")
    trade = st.selectbox("Select Trade", ["Plumbing", "Roofing", "Landscaping"])
    
    with st.form("cost_estimator_form"):
        st.subheader(f"{trade} Project Cost Estimator")
        project_name = st.text_input("Project Name")
        material_cost = st.number_input("Material Cost ($)", min_value=0.0, step=100.0)
        labor_cost = st.number_input("Labor Cost ($)", min_value=0.0, step=100.0)
        overhead_cost = st.number_input("Overhead Cost ($)", min_value=0.0, step=50.0)
        region = st.selectbox("Region", ["East Coast", "West Coast", "Midwest"])
        submitted = st.form_submit_button("Calculate Total Cost")
        
        if submitted:
            total_cost = material_cost + labor_cost + overhead_cost
            if region == "East Coast":
                total_cost *= 1.1  # Regional adjustment
            elif region == "West Coast":
                total_cost *= 1.15
            else:
                total_cost *= 1.05
            st.success(f"Total Estimated Cost for {project_name}: ${total_cost:,.2f}")
            st.session_state.projects.append({
                "Project Name": project_name,
                "Trade": trade,
                "Material Cost": material_cost,
                "Labor Cost": labor_cost,
                "Overhead Cost": overhead_cost,
                "Region": region,
                "Total Cost": total_cost
            })
    
    # Display projects
    if st.session_state.projects:
        st.subheader("Saved Projects")
        projects_df = pd.DataFrame(st.session_state.projects)
        st.dataframe(projects_df)
        csv = projects_df.to_csv(index=False)
        st.download_button("Download Projects", csv, "projects.csv", "text/csv")

# Module 2: Contractor Management
elif app_mode == "Contractor Management":
    st.header("Contractor Management Tool")
    
    with st.form("contractor_form"):
        st.subheader("Add Contractor")
        contractor_name = st.text_input("Contractor Name")
        trade = st.selectbox("Trade", ["Plumbing", "Roofing", "Landscaping"])
        contact = st.text_input("Contact Info")
        schedule = st.date_input("Schedule Date")
        payment = st.number_input("Payment Amount ($)", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("Add Contractor")
        
        if submitted:
            st.session_state.contractors.append({
                "Name": contractor_name,
                "Trade": trade,
                "Contact": contact,
                "Schedule": schedule,
                "Payment": payment
            })
            st.success(f"Contractor {contractor_name} added!")
    
    # Display contractors
    if st.session_state.contractors:
        st.subheader("Contractor List")
        contractors_df = pd.DataFrame(st.session_state.contractors)
        st.dataframe(contractors_df)
        csv = contractors_df.to_csv(index=False)
        st.download_button("Download Contractors", csv, "contractors.csv", "text/csv")

# Module 3: Invoice Generator
elif app_mode == "Invoice Generator":
    st.header("Simple Invoice Generator")
    
    # Select project to generate invoice
    project_names = [p["Project Name"] for p in st.session_state.projects]
    selected_project = st.selectbox("Select Project", project_names)
    
    if selected_project:
        project = next(p for p in st.session_state.projects if p["Project Name"] == selected_project)
        with st.form("invoice_form"):
            st.subheader(f"Generate Invoice for {selected_project}")
            client_name = st.text_input("Client Name")
            client_email = st.text_input("Client Email")
            due_date = st.date_input("Due Date")
            submitted = st.form_submit_button("Generate Invoice")
            
            if submitted:
                invoice = {
                    "Invoice ID": f"INV-{len(st.session_state.invoices) + 1}",
                    "Project Name": selected_project,
                    "Client Name": client_name,
                    "Client Email": client_email,
                    "Total Amount": project["Total Cost"],
                    "Due Date": due_date,
                    "Date Created": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.invoices.append(invoice)
                st.success(f"Invoice {invoice['Invoice ID']} generated!")
                
                # Display invoice details
                st.write("**Invoice Details**")
                st.write(f"Invoice ID: {invoice['Invoice ID']}")
                st.write(f"Project: {selected_project}")
                st.write(f"Client: {client_name} ({client_email})")
                st.write(f"Total Amount: ${project['Total Cost']:,.2f}")
                st.write(f"Due Date: {due_date}")
                
                # Generate QR code for payment link
                payment_link = f"https://example.com/pay/{invoice['Invoice ID']}"
                qr_filename = generate_qr_code(payment_link)
                st.image(qr_filename, caption="Scan QR Code for Payment", width=200)
    
    # Display invoices
    if st.session_state.invoices:
        st.subheader("Generated Invoices")
        invoices_df = pd.DataFrame(st.session_state.invoices)
        st.dataframe(invoices_df)
        csv = invoices_df.to_csv(index=False)
        st.download_button("Download Invoices", csv, "invoices.csv", "text/csv")

# Module 4: Receipts Input
elif app_mode == "Receipts Input":
    st.header("Simplified Receipts Input Tool")
    
    with st.form("receipt_form"):
        st.subheader("Add Receipt")
        receipt_date = st.date_input("Receipt Date")
        amount = st.number_input("Amount ($)", min_value=0.0, step=10.0)
        category = st.selectbox("Category", ["Materials", "Labor", "Equipment", "Other"])
        uploaded_file = st.file_uploader("Upload Receipt Image", type=["jpg", "png", "pdf"])
        submitted = st.form_submit_button("Add Receipt")
        
        if submitted:
            file_path = save_uploaded_file(uploaded_file) if uploaded_file else None
            st.session_state.receipts.append({
                "Date": receipt_date,
                "Amount": amount,
                "Category": category,
                "File": file_path
            })
            st.success("Receipt added!")
    
    # Display receipts
    if st.session_state.receipts:
        st.subheader("Uploaded Receipts")
        receipts_df = pd.DataFrame(st.session_state.receipts)
        st.dataframe(receipts_df)
        csv = receipts_df.to_csv(index=False)
        st.download_button("Download Receipts", csv, "receipts.csv", "text/csv")

# Module 5: QR Code Generator
elif app_mode == "QR Code Generator":
    st.header("Static QR Code Generator")
    
    with st.form("qr_form"):
        st.subheader("Generate QR Code")
        qr_data = st.text_input("Enter Data for QR Code (e.g., payment link, website)")
        submitted = st.form_submit_button("Generate QR Code")
        
        if submitted and qr_data:
            qr_filename = generate_qr_code(qr_data)
            st.image(qr_filename, caption="Generated QR Code", width=200)
            with open(qr_filename, "rb") as file:
                st.download_button("Download QR Code", file, qr_filename, "image/png")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Construction Business Efficiency Suite © 2025")
