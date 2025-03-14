import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from datetime import datetime

# Function to generate PDF invoice
def generate_invoice(company_name, customer_name, customer_email, items, currency, tax_percentage, logo_path=None):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    
    # Set margins
    left_margin = 50
    top_margin = 600
    bottom_margin = 50
    
    # Draw a bold black border around the page
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(2)  # Thicker border
    pdf.rect(left_margin - 10, bottom_margin - 10, A4[0] - left_margin - 50, top_margin - bottom_margin + 20)
    
    # Add logo and header
    if logo_path:
        pdf.drawImage(logo_path, left_margin, top_margin - 50, width=100, height=50)
    
    # Company name and invoice title
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(left_margin, top_margin, f"Invoice - {company_name}")
    
    # Invoice details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(left_margin, top_margin - 60, f"Customer: {customer_name}")
    pdf.drawString(left_margin, top_margin - 80, f"Email: {customer_email}")
    pdf.drawString(left_margin + 300, top_margin, f"Invoice Date: {datetime.now().strftime('%Y-%m-%d')}")
    pdf.drawString(left_margin + 300, top_margin - 20, f"Purchase Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Table header
    data = [["Item", "Quantity", f"Unit Price ({currency})", f"Total Price ({currency})"]]
    total_amount = 0
    
    # Add items to the table
    for item in items:
        item_name, qty, price = item
        total_price = qty * price
        data.append([item_name, str(qty), f"{price:.2f}", f"{total_price:.2f}"])
        total_amount += total_price
    
    # Calculate tax and grand total
    tax_amount = (total_amount * tax_percentage) / 100
    grand_total = total_amount + tax_amount
    
    # Add subtotal, tax, and grand total rows
    data.append(["", "", "Subtotal:", f"{currency} {total_amount:.2f}"])
    data.append(["", "", f"Tax ({tax_percentage}%):", f"{currency} {tax_amount:.2f}"])
    data.append(["", "", "Grand Total:", f"{currency} {grand_total:.2f}"])
    
    # Create table
    table = Table(data, colWidths=[200, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),  # Green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -3), colors.HexColor("#F0F0F0")),  # Light gray background for items
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Bold line below header
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),  # Bold line above subtotal
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),  # Bold line above grand total
    ]))
    
    # Draw table on PDF
    table.wrapOn(pdf, left_margin, top_margin - 250)
    table.drawOn(pdf, left_margin, top_margin - 250 - len(items) * 20)
    
    # Footer
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_margin, bottom_margin + 20, "Thank you for your business!")
    pdf.drawString(left_margin, bottom_margin, "Terms & Conditions: Payment due within 30 days.")
    
    pdf.save()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.set_page_config(page_title="Automated Invoice Generator", page_icon="🧾", layout="wide")

st.title("🧾 Automated Invoice Generator")

# Sidebar for input
st.sidebar.header("Enter Invoice Details")
company_name = st.sidebar.text_input("Company Name", "Company")
customer_name = st.sidebar.text_input("Customer Name")
customer_email = st.sidebar.text_input("Customer Email")
currency = st.sidebar.selectbox("Select Currency", ["₹", "$", "€", "£"], index=0)
tax_percentage = st.sidebar.number_input("Tax Percentage (%)", min_value=0.0, max_value=100.0, value=18.0)
logo_path = st.sidebar.file_uploader("Upload Company Logo (optional)", type=["png", "jpg", "jpeg"])

st.sidebar.subheader("Add Items")
items = []
num_items = st.sidebar.number_input("Number of Items", min_value=1, max_value=10, value=3)

for i in range(num_items):
    col1, col2, col3 = st.sidebar.columns(3)
    item_name = col1.text_input(f"Item {i+1} Name", key=f"name{i}")
    qty = col2.number_input(f"Qty {i+1}", min_value=1, value=1, key=f"qty{i}")
    price = col3.number_input(f"Price {i+1}", min_value=0.0, value=100.0, key=f"price{i}")
    items.append((item_name, qty, price))

# Generate Invoice button
if st.sidebar.button("Generate Invoice"):
    if customer_name and customer_email:
        # Save the uploaded logo to a temporary file
        if logo_path:
            with open("temp_logo.png", "wb") as f:
                f.write(logo_path.getbuffer())
            logo_path = "temp_logo.png"
        else:
            logo_path = None
        
        pdf_file = generate_invoice(company_name, customer_name, customer_email, items, currency, tax_percentage, logo_path)
        st.success("Invoice generated successfully!")
        st.download_button("📥 Download Invoice", pdf_file, file_name="invoice.pdf", mime="application/pdf")
    else:
        st.error("Please enter customer details.")

# Preview Invoice
st.subheader("Invoice Preview")
if customer_name and customer_email:
    st.write(f"**Company Name:** {company_name}")
    st.write(f"**Customer Name:** {customer_name}")
    st.write(f"**Customer Email:** {customer_email}")
    st.write(f"**Invoice Date:** {datetime.now().strftime('%Y-%m-%d')}")
    st.write(f"**Purchase Time:** {datetime.now().strftime('%H:%M:%S')}")
    st.write(f"**Currency:** {currency}")
    st.write(f"**Tax Percentage:** {tax_percentage}%")
    st.write("**Items:**")
    preview_items = pd.DataFrame(items, columns=["Item", "Qty", f"Price ({currency})"])
    preview_items[f"Total ({currency})"] = preview_items["Qty"] * preview_items[f"Price ({currency})"]
    st.table(preview_items)
    
    # Calculate tax and grand total
    subtotal = preview_items[f"Total ({currency})"].sum()
    tax_amount = (subtotal * tax_percentage) / 100
    grand_total = subtotal + tax_amount
    
    st.write(f"**Subtotal:** {currency} {subtotal:.2f}")
    st.write(f"**Tax ({tax_percentage}%):** {currency} {tax_amount:.2f}")
    st.write(f"**Grand Total:** {currency} {grand_total:.2f}")
else:
    st.warning("Please enter customer details to preview the invoice.")