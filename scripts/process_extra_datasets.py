import pandas as pd
import os

def prepare_combined_dataset():
    raw_dir = 'data/raw'
    
    # Target original input files
    dest_path = os.path.join(raw_dir, 'destinations.csv')
    reviews_path = os.path.join(raw_dir, 'Destination Reviews.csv')
    accom_path = os.path.join(raw_dir, 'Information for accommodation.csv') # Verify exact filename

    dfs = []

    # 1. Load Main Destinations
    if os.path.exists(dest_path):
        df_dest = pd.read_csv(dest_path)
        df_dest.columns = [str(c).strip().lower() for c in df_dest.columns]
        if 'name' in df_dest.columns:
            df_dest = df_dest.rename(columns={'name': 'destination_name'})
        dfs.append(df_dest)

    # 2. Load Reviews (Explicitly drop Review & Timespan)
    if os.path.exists(reviews_path):
        df_rev = pd.read_csv(reviews_path)
        df_rev.columns = [str(c).strip().lower() for c in df_rev.columns]
        
        # Exclude review and timespan columns
        cols_to_drop = [c for c in ['review', 'timespan'] if c in df_rev.columns]
        if cols_to_drop:
            df_rev = df_rev.drop(columns=cols_to_drop)

        # Map 'destination' header to 'destination_name'
        if 'destination' in df_rev.columns:
            df_rev = df_rev.rename(columns={'destination': 'destination_name'})
            
        dfs.append(df_rev)

    # 3. Load Accommodations
    if os.path.exists(accom_path):
        df_acc = pd.read_csv(accom_path)
        df_acc.columns = [str(c).strip().lower() for c in df_acc.columns]
        
        if 'name' in df_acc.columns:
            df_acc = df_acc.rename(columns={'name': 'hotel_name'})
        
        if 'district' in df_acc.columns and 'destination_name' not in df_acc.columns:
            df_acc['destination_name'] = df_acc['district']
            
        dfs.append(df_acc)

    if not dfs:
        print("No CSV datasets found in data/raw!")
        return

    # Combine datasets
    combined_df = pd.concat(dfs, ignore_index=True)

    if 'destination_name' not in combined_df.columns:
        print("Error: Could not identify destination names across your CSVs!")
        return

    # Clean destination name
    combined_df['destination_name'] = combined_df['destination_name'].astype(str).str.strip()

    aggregated_records = []

    # Group by unique destination name
    for dest_name, group in combined_df.groupby('destination_name'):
        if pd.isna(dest_name) or dest_name.lower() in ['nan', 'none', '']:
            continue

        category = group['category'].dropna().iloc[0] if 'category' in group and not group['category'].dropna().empty else 'attraction'
        district = group['district'].dropna().iloc[0] if 'district' in group and not group['district'].dropna().empty else 'Sri Lanka'
        entrance_fee = group['entrance_fee'].dropna().iloc[0] if 'entrance_fee' in group and not group['entrance_fee'].dropna().empty else 0.00
        accessibility = group['accessibility'].dropna().iloc[0] if 'accessibility' in group and not group['accessibility'].dropna().empty else 'Moderate'
        trekking = group['trekking_difficulty'].dropna().iloc[0] if 'trekking_difficulty' in group and not group['trekking_difficulty'].dropna().empty else 'N/A'

        text_parts = []
        
        # Base description
        if 'description' in group.columns:
            descs = group['description'].dropna().unique()
            if len(descs) > 0:
                text_parts.append(" ".join(descs))

        # Accommodation text
        if 'hotel_name' in group.columns:
            hotels = group[['hotel_name', 'type']].dropna().to_dict(orient='records') if 'type' in group else []
            if hotels:
                hotel_str = ", ".join([f"{h.get('hotel_name')} ({h.get('type', 'Hotel')})" for h in hotels[:3]])
                text_parts.append("Nearby Accommodation: " + hotel_str)

        full_description = " ".join(text_parts).strip()
        if not full_description:
            full_description = f"{dest_name} located in {district}."

        clean_name = dest_name.lower().replace(' ', '_').replace("'", "")
        image_path = f"data/images/{clean_name}.jpg"

        aggregated_records.append({
            'name': dest_name,
            'category': str(category).lower().strip(),
            'district': str(district).strip(),
            'entrance_fee': float(pd.to_numeric(entrance_fee, errors='coerce') or 0.00),
            'accessibility': str(accessibility),
            'trekking_difficulty': str(trekking),
            'description': full_description,
            'image_path': image_path
        })

    master_df = pd.DataFrame(aggregated_records)

    # Save output to NEW file: destinations_processed.csv
    output_path = os.path.join(raw_dir, 'destinations.csv')
    master_df.to_csv(output_path, index=False)
    print(f"Successfully created clean dataset at '{output_path}' ({len(master_df)} unique destinations)!")

if __name__ == '__main__':
    prepare_combined_dataset()