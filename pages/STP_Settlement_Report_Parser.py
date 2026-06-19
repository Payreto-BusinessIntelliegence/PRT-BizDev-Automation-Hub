import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
from datetime import datetime

st.set_page_config(page_title="Settlement Report Parser", layout="wide")

st.title("📊 Settlement Report Parser")
st.markdown("Upload one or more Vision Pay settlement report Excel files to parse and analyze the data.")

def get_currency_from_cell(ws, row_idx, col_idx):
    """Extract currency from Excel cell format"""
    cell = ws.cell(row=row_idx + 1, column=col_idx + 1)
    number_format = cell.number_format
    
    if '€' in number_format or 'EUR' in number_format:
        return 'EUR'
    elif '$' in number_format or 'USD' in number_format:
        return 'USD'
    
    return None

def parse_section(df_single, ws, start_idx, end_idx, settlement_date, report_number, coverage_from, coverage_to):
    """Parse a section of the report and return a DataFrame"""
    data = []
    current_label = None
    
    for idx in range(start_idx + 1, end_idx):
        row = df_single.iloc[idx]
        if row.isna().all() or "Particulars" in str(row.iloc[0]):
            continue
        
        label = row.iloc[0] if pd.notna(row.iloc[0]) else None
        card_type = row.iloc[1] if pd.notna(row.iloc[1]) else None
        count = row.iloc[3] if pd.notna(row.iloc[3]) else None
        amount = row.iloc[4] if pd.notna(row.iloc[4]) else None
        
        if label is not None:
            current_label = label
        
        currency = get_currency_from_cell(ws, idx + 1, 4)
        
        if isinstance(count, str) and count in ['EUR', 'USDC', 'USD']:
            currency = count
            count = None
        
        record = {
            "Settlement Date": settlement_date,
            "Report Number": report_number,
            "Coverage From": coverage_from,
            "Coverage To": coverage_to,
            "Label": current_label,
            "Card Type": card_type,
            "Count": count,
            "Amount": amount,
            "Currency": currency
        }
        data.append(record)
    
    return pd.DataFrame(data)

def process_single_file(uploaded_file, file_name):
    """Process a single Excel file and return all parsed sections"""
    try:
        df_single = pd.read_excel(uploaded_file)
        uploaded_file.seek(0)
        wb = load_workbook(uploaded_file)
        ws = wb.active
        
        settlement_date = df_single.iloc[4, 1]
        if pd.notna(settlement_date):
            settlement_date = str(settlement_date).split()[0] if isinstance(settlement_date, pd.Timestamp) else str(settlement_date)
        
        report_number = str(df_single.iloc[5, 1]) if pd.notna(df_single.iloc[5, 1]) else ""
        
        coverage_from = df_single.iloc[6, 2]
        if pd.notna(coverage_from):
            coverage_from = str(coverage_from).split()[0] if isinstance(coverage_from, pd.Timestamp) else str(coverage_from)
        
        coverage_to = df_single.iloc[7, 2]
        if pd.notna(coverage_to):
            coverage_to = str(coverage_to).split()[0] if isinstance(coverage_to, pd.Timestamp) else str(coverage_to)
        
        # Find sections
        sections = {}
        for idx, row in df_single.iterrows():
            row_values = row.astype(str).tolist()
            if 'Merchant Information' in row_values:
                sections['Merchant Information'] = idx
            if 'Sales Volume' in row_values:
                sections['Sales Volume'] = idx
            elif 'Cancellations' in row_values:
                sections['Cancellations'] = idx
            elif 'Fee Breakdown' in row_values:
                sections['Fee Breakdown'] = idx
            elif 'Rolling Reserve' in row_values:
                sections['Rolling Reserve'] = idx
            elif 'Final Payout' in row_values:
                sections['Final Payout'] = idx
        
        # Parse each section
        sales_df = parse_section(
            df_single, ws, 
            sections['Sales Volume'], 
            sections['Fee Breakdown'],
            settlement_date, report_number, coverage_from, coverage_to
        )
        
        fee_bd_df = parse_section(
            df_single, ws,
            sections['Fee Breakdown'],
            sections['Rolling Reserve'],
            settlement_date, report_number, coverage_from, coverage_to
        )
        
        rolling_reserve_df = parse_section(
            df_single, ws,
            sections['Rolling Reserve'],
            sections['Final Payout'],
            settlement_date, report_number, coverage_from, coverage_to
        )
        
        final_payout_df = parse_section(
            df_single, ws,
            sections['Final Payout'],
            len(df_single),
            settlement_date, report_number, coverage_from, coverage_to
        )
        
        return {
            'file_name': file_name,
            'settlement_date': settlement_date,
            'report_number': report_number,
            'coverage_from': coverage_from,
            'coverage_to': coverage_to,
            'sales_df': sales_df,
            'fee_bd_df': fee_bd_df,
            'rolling_reserve_df': rolling_reserve_df,
            'final_payout_df': final_payout_df
        }
    except Exception as e:
        st.error(f"Error processing {file_name}: {str(e)}")
        return None

uploaded_files = st.file_uploader("Choose Excel file(s)", type=['xlsx'], accept_multiple_files=True)

if uploaded_files:
    all_processed_data = []
    all_flattened_data = []
    
    # Process all files
    with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
        for uploaded_file in uploaded_files:
            result = process_single_file(uploaded_file, uploaded_file.name)
            if result:
                all_processed_data.append(result)
                
                # Collect flattened data from this file
                file_sections = []
                if not result['sales_df'].empty:
                    result['sales_df']['Section'] = 'Sales Volume'
                    result['sales_df']['File Name'] = uploaded_file.name
                    file_sections.append(result['sales_df'])
                if not result['fee_bd_df'].empty:
                    result['fee_bd_df']['Section'] = 'Fee Breakdown'
                    result['fee_bd_df']['File Name'] = uploaded_file.name
                    file_sections.append(result['fee_bd_df'])
                if not result['rolling_reserve_df'].empty:
                    result['rolling_reserve_df']['Section'] = 'Rolling Reserve'
                    result['rolling_reserve_df']['File Name'] = uploaded_file.name
                    file_sections.append(result['rolling_reserve_df'])
                if not result['final_payout_df'].empty:
                    result['final_payout_df']['Section'] = 'Final Payout'
                    result['final_payout_df']['File Name'] = uploaded_file.name
                    file_sections.append(result['final_payout_df'])
                
                if file_sections:
                    all_flattened_data.extend(file_sections)
    
    if all_processed_data:
        st.success(f"✅ Successfully processed {len(all_processed_data)} file(s)")
        
        # Create tabs for each file and combined summary
        tab_names = [f"📄 {data['file_name']}" for data in all_processed_data] + ["📥 Combined Summary"]
        tabs = st.tabs(tab_names)
        
        # Display individual file reports
        for idx, data in enumerate(all_processed_data):
            with tabs[idx]:
                st.header(f"Report: {data['file_name']}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Settlement Date", data['settlement_date'])
                with col2:
                    st.metric("Report Number", data['report_number'])
                with col3:
                    st.metric("Coverage From", data['coverage_from'])
                with col4:
                    st.metric("Coverage To", data['coverage_to'])
                
                st.divider()
                
                # Sub-tabs for sections
                subtab1, subtab2, subtab3, subtab4 = st.tabs(["💰 Sales Volume", "💳 Fee Breakdown", "🏦 Rolling Reserve", "✅ Final Payout"])
                
                with subtab1:
                    st.subheader("Sales Volume")
                    st.dataframe(data['sales_df'], use_container_width=True)
                    if not data['sales_df'].empty:
                        total_row = data['sales_df'][data['sales_df']['Label'] == 'Total Gross Sales']
                        if not total_row.empty:
                            total_amount = total_row['Amount'].iloc[0]
                            currency = total_row['Currency'].iloc[0] if pd.notna(total_row['Currency'].iloc[0]) else ""
                            st.metric("Total Gross Sales", f"{currency} {total_amount:,.2f}" if currency else f"{total_amount:,.2f}")
                
                with subtab2:
                    st.subheader("Fee Breakdown")
                    st.dataframe(data['fee_bd_df'], use_container_width=True)
                    if not data['fee_bd_df'].empty:
                        total_fees = data['fee_bd_df'][data['fee_bd_df']['Label'] == 'Total Fees']
                        if not total_fees.empty:
                            total_fee_amount = total_fees['Amount'].iloc[0]
                            currency = total_fees['Currency'].iloc[0] if pd.notna(total_fees['Currency'].iloc[0]) else ""
                            st.metric("Total Fees", f"{currency} {total_fee_amount:,.2f}" if currency else f"{total_fee_amount:,.2f}")
                
                with subtab3:
                    st.subheader("Rolling Reserve")
                    st.dataframe(data['rolling_reserve_df'], use_container_width=True)
                    if not data['rolling_reserve_df'].empty:
                        total_reserve = data['rolling_reserve_df'][data['rolling_reserve_df']['Label'] == 'Total Reserve (Running Balance)']
                        if not total_reserve.empty:
                            total_reserve_amount = total_reserve['Amount'].iloc[0]
                            currency = total_reserve['Currency'].iloc[0] if pd.notna(total_reserve['Currency'].iloc[0]) else ""
                            st.metric("Total Reserve", f"{currency} {total_reserve_amount:,.2f}" if currency else f"{total_reserve_amount:,.2f}")
                    
                with subtab4:
                    st.subheader("Final Payout")
                    st.dataframe(data['final_payout_df'], use_container_width=True)
                    if not data['final_payout_df'].empty:
                        total_eur_row = data['final_payout_df'][(data['final_payout_df']['Label'] == 'Total NET PAYOUT') & (data['final_payout_df']['Currency'] == 'EUR')]
                        total_usdc_row = data['final_payout_df'][(data['final_payout_df']['Label'] == 'Total NET PAYOUT') & (data['final_payout_df']['Currency'] == 'USDC')]
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if not total_eur_row.empty:
                                total_eur_amount = total_eur_row['Amount'].iloc[0]
                                st.metric("Total NET PAYOUT (EUR)", f"€ {total_eur_amount:,.2f}")
                            else:
                                st.metric("Total NET PAYOUT (EUR)", "€ 0.00")

                        with col_b:
                            if not total_usdc_row.empty:
                                total_usdc_amount = total_usdc_row['Amount'].iloc[0]
                                st.metric("Total NET PAYOUT (USDC)", f"$ {total_usdc_amount:,.2f}")
                            else:
                                st.metric("Total NET PAYOUT (USDC)", "$ 0.00")
        
        # Combined Summary Tab
        with tabs[-1]:
            st.header("📥 Combined Flattened Summary")
            st.markdown(f"**Total Files Processed:** {len(all_processed_data)}")
            
            if all_flattened_data:
                combined_df = pd.concat(all_flattened_data, ignore_index=True)
                
                # Reorder columns to put File Name first
                cols = ['File Name'] + [col for col in combined_df.columns if col != 'File Name']
                combined_df = combined_df[cols]
                
                st.dataframe(combined_df, use_container_width=True)
                
                st.divider()
                st.subheader("📥 Download Options")
                
                col1, col2 = st.columns(2)
                
                # CSV Download
                with col1:
                    csv_buffer = io.StringIO()
                    combined_df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📄 Download as CSV",
                        data=csv_data,
                        file_name=f"combined_settlement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Excel Download
                with col2:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        combined_df.to_excel(writer, index=False, sheet_name='Combined Summary')
                    excel_data = excel_buffer.getvalue()
                    
                    st.download_button(
                        label="📊 Download as Excel",
                        data=excel_data,
                        file_name=f"combined_settlement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Summary Statistics
                st.divider()
                st.subheader("📊 Summary Statistics")
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("Total Records", len(combined_df))
                with stat_col2:
                    st.metric("Unique Reports", combined_df['Report Number'].nunique())
                with stat_col3:
                    st.metric("Date Range", f"{combined_df['Coverage From'].min()} to {combined_df['Coverage To'].max()}")
            else:
                st.info("No valid data available to generate combined summary.")
    else:
        st.warning("⚠️ No files were successfully processed. Please check the file format.")
else:
    st.info("👆 Please upload one or more Excel files to begin parsing.")
    st.markdown("""
    ### Expected File Format
    The application expects Vision Pay settlement reports with the following sections:
    - Merchant Information
    - Sales Volume
    - Cancellations
    - Fee Breakdown
    - Rolling Reserve
    - Final Payout
    
    ### Features
    - ✅ Upload multiple files at once
    - ✅ View individual report details
    - ✅ Combined flattened summary with all data
    - ✅ Download as CSV or Excel
    - ✅ Summary statistics across all reports
    """)