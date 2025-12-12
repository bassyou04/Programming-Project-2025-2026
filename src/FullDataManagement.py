import pandas as pd
def New_Columns():
    # Load the CSV
    df = pd.read_csv('C:\Pyhton Programming\Programming Project\Programming-Project-2025-2026\Data\data.csv')
    # 1. Calculate total compensation without benefits
    df['TotalCompensation'] = df['BasePay'] + df['OvertimePay'] + df['OtherPay']
    # 2. Calculate overtime percentage of base pay
    df['OvertimePercent'] = (df['OvertimePay'] / df['BasePay']) * 100
    # 3. Benefits to total pay ratio
    df['BenefitsRatio'] = df['Benefits'] / df['TotalPay']
    # 4. Create salary categories
    df['SalaryCategory'] = pd.cut(df['TotalPayBenefits'], bins=[0, 50000, 100000, 150000, float('inf')],labels=['Low', 'Medium', 'High', 'Very High'])
    # 5. Flag high overtime earners (over 20% of base pay)
    df['HighOvertimeFlag'] = df['OvertimePercent'] > 20
    # 6. Extract year as category
    df['YearCategory'] = df['Year'].astype('category')
    # 7. Full name length (just as an example)
    df['NameLength'] = df['EmployeeName'].str.len()
def Summary_Statistics(df):
     # Basic summary statistics for numerical columns
    print(df[['BasePay', 'OvertimePay', 'TotalPay', 'Benefits']].describe())

    # Custom aggregations
    summary = df.agg({
        'BasePay': ['mean', 'median', 'std', 'min', 'max'],
        'OvertimePay': ['sum', 'mean'],
        'TotalPayBenefits': ['mean', 'max']
    })
    print(summary)

    # Group by Job Title
    job_summary = df.groupby('JobTitle').agg({
        'BasePay': 'mean',
        'OvertimePay': 'mean',
        'TotalPayBenefits': ['mean', 'count']
    }).round(2)

    # Group by Agency
    agency_summary = df.groupby('Agency').agg({
        'TotalPay': ['mean', 'sum', 'count'],
        'OvertimePay': 'sum'
    })

    # Multiple grouping (Agency and Year)
    multi_summary = df.groupby(['Agency', 'Year'])['TotalPayBenefits'].agg(['mean', 'count'])

    # Correlation between numerical columns
    correlation = df[['BasePay', 'OvertimePay', 'OtherPay', 'Benefits']].corr()

    # Value counts for categorical columns
    print(df['JobTitle'].value_counts())
    print(df['Status'].value_counts())

    # Percentiles
    percentiles = df['TotalPayBenefits'].quantile([0.25, 0.5, 0.75, 0.9, 0.95])
def Joining():
    # ===== STEP 1: Create Agency Mapping (if needed) =====
    # Skip this if you already have agency_code.csv
    agency_mapping = pd.DataFrame({
        'Agency': ['Police Department', 'Fire Department', 'Public Works'],
        'AgencyCode': ['PD-001', 'FD-002', 'PW-003'],
        'Department': ['Public Safety', 'Public Safety', 'Infrastructure']
    })
    agency_mapping.to_csv('agency_code.csv', index=False)

    # ===== STEP 2: Load Main Dataset =====
    dtypes_main = {
        'Id': 'int32',
        'EmployeeName': 'string',
        'JobTitle': 'category',
        'BasePay': 'float32',
        'OvertimePay': 'float32',
        'OtherPay': 'float32',
        'Benefits': 'float32',
        'TotalPay': 'float32',
        'TotalPayBenefits': 'float32',
        'Year': 'int16',
        'Agency': 'string',
        'Status': 'category'
    }

    df_employees = pd.read_csv('C:\Pyhton Programming\Programming Project\Programming-Project-2025-2026\Data\data.csv', dtype=dtypes_main)

    # ===== STEP 3: Load Agency Codes =====
    df_agency_codes = pd.read_csv('agency_code.csv')

    # ===== STEP 4: Merge =====
    merged_df = pd.merge(
        df_employees,
        df_agency_codes,
        on='Agency',
        how='left'
    )

    # ===== STEP 5: Validate Merge =====
    print(f"Original records: {len(df_employees)}")
    print(f"Merged records: {len(merged_df)}")
    print(f"Agencies in main data: {df_employees['Agency'].nunique()}")
    print(f"Agencies in mapping: {len(df_agency_codes)}")

    # Check for unmatched agencies
    unmatched_count = merged_df['AgencyCode'].isna().sum()
    if unmatched_count > 0:
        print(f"\nWarning: {unmatched_count} records with unmatched agencies")

    # ===== STEP 6: Save =====
    merged_df.to_csv('merged_data.csv', index=False)
    print("\n✓ Merged data saved to 'merged_data.csv'")


New_Columns()
df=pd.read_csv('C:\Pyhton Programming\Programming Project\Programming-Project-2025-2026\Data\data.csv')
Summary_Statistics(df)
Joining()
