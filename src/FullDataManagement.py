import pandas as pd
import os
import numpy as np

# Fix 1: Use relative paths with os.path.join for cross-platform compatibility
def get_data_path(filename):
    """Get the correct path to data files"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'Data', filename)
    return data_path

def New_Columns():
    """Create new calculated columns with error handling"""
    # Load the CSV using relative path
    data_file = get_data_path('data.csv')
    
    # FIX: Specify dtypes and handle mixed types
    # Use converters to force numeric conversion
    df = pd.read_csv(data_file, low_memory=False)
    
    print(f"Loaded {len(df)} records from {data_file}")
    
    # Convert numeric columns to proper types (handle 'Not Provided', empty strings, etc.)
    numeric_columns = ['BasePay', 'OvertimePay', 'OtherPay', 'Benefits', 'TotalPay', 'TotalPayBenefits']
    
    print("\nConverting columns to numeric types...")
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, forcing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"  ✓ {col}: {df[col].isna().sum()} missing/invalid values")
    
    # Also convert Year to integer
    if 'Year' in df.columns:
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')  # nullable integer
    
    if 'Id' in df.columns:
        df['Id'] = pd.to_numeric(df['Id'], errors='coerce').astype('Int64')
    
    print("\n✓ All numeric conversions complete")
    
    # 1. Calculate total compensation without benefits
    df['TotalCompensation'] = df['BasePay'].fillna(0) + df['OvertimePay'].fillna(0) + df['OtherPay'].fillna(0)
    
    # 2. Calculate overtime percentage of base pay (handle division by zero)
    df['OvertimePercent'] = np.where(
        (df['BasePay'] > 0) & (df['BasePay'].notna()),
        (df['OvertimePay'] / df['BasePay']) * 100,
        np.nan
    )
    
    # 3. Benefits to total pay ratio (handle division by zero)
    df['BenefitsRatio'] = np.where(
        (df['TotalPay'] > 0) & (df['TotalPay'].notna()),
        df['Benefits'] / df['TotalPay'],
        np.nan
    )
    
    # 4. Create salary categories
    df['SalaryCategory'] = pd.cut(
        df['TotalPayBenefits'], 
        bins=[0, 50000, 100000, 150000, float('inf')],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    
    # 5. Flag high overtime earners (over 20% of base pay)
    df['HighOvertimeFlag'] = df['OvertimePercent'] > 20
    
    # 6. Extract year as category
    if 'Year' in df.columns:
        df['YearCategory'] = df['Year'].astype('category')
    
    # 7. Full name length
    if 'EmployeeName' in df.columns:
        df['NameLength'] = df['EmployeeName'].str.len()
    
    # Save the modified dataframe
    output_file = get_data_path('data_with_new_columns.csv')
    df.to_csv(output_file, index=False)
    print(f"\n✓ New columns added and saved to {output_file}")
    
    # Show summary of new columns
    print("\n" + "="*60)
    print("NEW COLUMNS SUMMARY")
    print("="*60)
    print(f"  - Total records: {len(df):,}")
    print(f"  - Rows with zero/missing BasePay: {((df['BasePay'] == 0) | df['BasePay'].isna()).sum():,}")
    print(f"  - Rows with zero/missing TotalPay: {((df['TotalPay'] == 0) | df['TotalPay'].isna()).sum():,}")
    print(f"  - High Overtime Employees: {df['HighOvertimeFlag'].sum():,}")
    print(f"\n  - Salary Categories:")
    print(df['SalaryCategory'].value_counts().sort_index())
    
    return df

def Summary_Statistics(df):
    """Generate comprehensive summary statistics"""
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    # Basic summary statistics for numerical columns
    print("\n1. Basic Statistics for Key Columns:")
    print(df[['BasePay', 'OvertimePay', 'TotalPay', 'Benefits']].describe())

    # Custom aggregations
    print("\n2. Custom Aggregations:")
    summary = df.agg({
        'BasePay': ['mean', 'median', 'std', 'min', 'max'],
        'OvertimePay': ['sum', 'mean'],
        'TotalPayBenefits': ['mean', 'max']
    })
    print(summary)

    # Group by Job Title (top 10 only to avoid clutter)
    print("\n3. Top 10 Job Titles by Average Pay:")
    job_summary = df.groupby('JobTitle').agg({
        'BasePay': 'mean',
        'OvertimePay': 'mean',
        'TotalPayBenefits': ['mean', 'count']
    }).round(2)
    job_summary.columns = ['_'.join(col) for col in job_summary.columns]
    job_summary = job_summary.sort_values('TotalPayBenefits_mean', ascending=False).head(10)
    print(job_summary)

    # Group by Agency
    print("\n4. Top 10 Agencies by Total Pay:")
    agency_summary = df.groupby('Agency').agg({
        'TotalPay': ['mean', 'sum', 'count'],
        'OvertimePay': 'sum'
    }).round(2)
    agency_summary.columns = ['_'.join(col) for col in agency_summary.columns]
    agency_summary = agency_summary.sort_values('TotalPay_sum', ascending=False).head(10)
    print(agency_summary)

    # Multiple grouping (Agency and Year) - sample
    print("\n5. Pay Statistics by Agency and Year (sample):")
    multi_summary = df.groupby(['Agency', 'Year'])['TotalPayBenefits'].agg(['mean', 'count'])
    print(multi_summary.head(15))

    # Correlation between numerical columns
    print("\n6. Correlation Matrix:")
    correlation = df[['BasePay', 'OvertimePay', 'OtherPay', 'Benefits']].corr()
    print(correlation.round(3))

    # Value counts for categorical columns (top 10)
    print("\n7. Top 10 Most Common Job Titles:")
    print(df['JobTitle'].value_counts().head(10))
    
    print("\n8. Status Distribution:")
    if 'Status' in df.columns:
        print(df['Status'].value_counts())

    # Percentiles
    print("\n9. TotalPayBenefits Percentiles:")
    percentiles = df['TotalPayBenefits'].quantile([0.25, 0.5, 0.75, 0.9, 0.95])
    for pct, val in percentiles.items():
        print(f"  {int(pct*100)}th percentile: ${val:,.2f}")

def Joining():
    """Merge employee data with agency codes"""
    print("\n" + "="*60)
    print("JOINING DATASETS")
    print("="*60)
    
    # ===== STEP 1: Load Main Dataset First =====
    data_file = get_data_path('data.csv')
    
    dtypes_main = {
        'EmployeeName': 'string',
        'JobTitle': 'string',
        'Agency': 'string',
        'Status': 'string',
        'Notes': 'string'
    }
    
    print("\nLoading main dataset...")
    df_employees = pd.read_csv(data_file, dtype=dtypes_main, low_memory=False)
    
    # Convert numeric columns
    numeric_columns = ['Id', 'BasePay', 'OvertimePay', 'OtherPay', 'Benefits', 'TotalPay', 'TotalPayBenefits', 'Year']
    for col in numeric_columns:
        if col in df_employees.columns:
            df_employees[col] = pd.to_numeric(df_employees[col], errors='coerce')
    
    # Get unique agencies
    unique_agencies = df_employees['Agency'].dropna().unique()
    print(f"Found {len(unique_agencies)} unique agencies in main dataset")
    
    # ===== STEP 2: Create Agency Mapping =====
    print("Creating agency mapping...")
    
    # Create mapping for all unique agencies
    agency_mapping = pd.DataFrame({
        'Agency': unique_agencies,
        'AgencyCode': [f'AG-{str(i).zfill(4)}' for i in range(len(unique_agencies))],
        'Department': ['General' for _ in range(len(unique_agencies))]
    })
    
    # Save agency mapping
    mapping_file = get_data_path('agency_code.csv')
    agency_mapping.to_csv(mapping_file, index=False)
    print(f"✓ Agency mapping saved to {mapping_file}")

    # ===== STEP 3: Load Agency Codes =====
    df_agency_codes = pd.read_csv(mapping_file)

    # ===== STEP 4: Merge =====
    print("\nMerging datasets...")
    merged_df = pd.merge(
        df_employees,
        df_agency_codes,
        on='Agency',
        how='left'
    )

    # ===== STEP 5: Validate Merge =====
    print(f"\nMerge Results:")
    print(f"  - Original records: {len(df_employees):,}")
    print(f"  - Merged records: {len(merged_df):,}")
    print(f"  - Agencies in main data: {df_employees['Agency'].nunique()}")
    print(f"  - Agencies in mapping: {len(df_agency_codes)}")

    # Check for unmatched agencies
    unmatched_count = merged_df['AgencyCode'].isna().sum()
    if unmatched_count > 0:
        print(f"\n⚠ Warning: {unmatched_count:,} records with unmatched agencies")
        unmatched_agencies = merged_df[merged_df['AgencyCode'].isna()]['Agency'].unique()
        print(f"  Unmatched agencies: {len(unmatched_agencies)}")
        if len(unmatched_agencies) > 0 and len(unmatched_agencies) <= 10:
            for agency in unmatched_agencies:
                print(f"    - {agency}")

    # ===== STEP 6: Save =====
    merged_file = get_data_path('merged_data.csv')
    merged_df.to_csv(merged_file, index=False)
    print(f"\n✓ Merged data saved to {merged_file}")
    
    return merged_df

# Main execution
if __name__ == "__main__":
    try:
        print("="*60)
        print("DATA MANAGEMENT PIPELINE")
        print("="*60)
        
        # Step 1: Create new columns
        print("\n[STEP 1/3] Creating new columns...")
        df = New_Columns()
        
        # Step 2: Generate summary statistics
        print("\n[STEP 2/3] Generating summary statistics...")
        Summary_Statistics(df)
        
        # Step 3: Join with agency codes
        print("\n[STEP 3/3] Joining with agency codes...")
        merged_df = Joining()
        
        print("\n" + "="*60)
        print("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nOutput files created:")
        print("  1. data_with_new_columns.csv")
        print("  2. agency_code.csv")
        print("  3. merged_data.csv")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find file - {e}")
        print("Please check that your data files are in the correct location.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()