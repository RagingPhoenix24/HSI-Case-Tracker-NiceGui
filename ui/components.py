from nicegui import ui
from datetime import date
import json

def render_invoice_preview(case_row: dict, billing: dict, case_details: dict):
    html = f"""
    <div id="invoice" style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 50px 40px; border: 1px solid #ddd; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1 style="margin: 0; color: #1a3c6e;">Hideaway Source Intelligence</h1>
                <p style="margin: 12px 0 0 0; font-size: 14px; line-height: 1.4;">
                    Lee Mueller<br>
                    31523 North Lake Creek Drive, Tangent, OR 97389<br>
                    mueller.lee@hideawayintel.com<br>
                    (562) 666-5606<br>
                    1922753159-000
                </p>
            </div>
            <div style="text-align: right;">
                <h2 style="margin: 0; color: #1a3c6e;">INVOICE</h2>
                <p style="font-size: 14px; line-height: 1.6; margin-top: 8px;">
                    <strong>Invoice #:</strong> {case_details.get("invoice_number", "")}<br>
                    <strong>Invoice Period:</strong> {case_details.get("invoice_period", "")}<br>
                    <strong>Date:</strong> {date.today().strftime("%m/%d/%Y")}
                </p>
            </div>
        </div>
        <hr style="border: 1px solid #ddd; margin: 35px 0 25px 0;">
        <p style="margin-bottom: 28px; line-height: 1.5;">
            <strong>Case Number:</strong> {case_row.get("Case_Number", case_row["case_id"])}<br>
            <strong>Client Name:</strong> {case_row.get("Client", "")}
        </p>
        <!-- Service Fees, Other Expenses, Travel tables exactly as in your original code -->
        <h3 style="color: #1a3c6e; margin-bottom: 12px;">Service Fees</h3>
        <table style="width:100%; border-collapse: collapse; margin-bottom: 28px;">
            <thead>
                <tr style="background: #f0f0f0;">
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Date</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Quantity/Activity</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Hours</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Rate</th>
                    <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Amount</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f"<tr><td style='border:1px solid #ddd;padding:12px'>{row.get('Date','')}</td><td style='border:1px solid #ddd;padding:12px'>{row.get('Quantity/Activity','')}</td><td style='border:1px solid #ddd;padding:12px;text-align:right'>{row.get('Hours',0):.2f}</td><td style='border:1px solid #ddd;padding:12px;text-align:right'>${row.get('Rate',0):.2f}</td><td style='border:1px solid #ddd;padding:12px;text-align:right'>${row.get('Amount',0):.2f}</td></tr>" for row in sorted(billing.get("service_fees", []), key=lambda x: x.get('Date',''))])}
            </tbody>
        </table>
        <!-- (Other tables omitted for brevity in this message but are identical to your original HTML) -->
        <h2 style="text-align:right; border-top: 3px solid #1a3c6e; padding-top: 15px; margin-top: 40px;">Invoice Grand Total: ${sum(row.get("Amount",0) for row in billing.get("service_fees", [])) + sum(row.get("Amount",0) for row in billing.get("other_expenses", [])) + sum(row.get("Amount",0) for row in billing.get("travel_mileage", [])):.2f}</h2>
        <div style="text-align:center; margin-top: 50px;">
            <button onclick="window.print()" style="background:#1a3c6e; color:white; border:none; padding:15px 40px; font-size:18px; border-radius:8px; cursor:pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">🖨️ Print / Save as PDF</button>
        </div>
    </div>
    """
    ui.html(html).classes("w-full")
