import os
import pandas as pd
from src.database import get_db_connection
from src.embeddings import generate_text_embedding, generate_image_embedding_from_file

def ingest_destinations():
    csv_path = 'data/raw/destinations.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return

    df = pd.read_csv(csv_path)
    conn = get_db_connection()
    cur = conn.cursor()

    print("Truncating old destinations table...")
    cur.execute("TRUNCATE TABLE destinations RESTART IDENTITY;")

    for idx, row in df.iterrows():
        name = str(row['name']).strip()
        print(f"Processing ({idx+1}/{len(df)}): {name}...")

        description = str(row.get('description', ''))
        
        # Format clean image path
        raw_img_path = str(row.get('image_path', '')).strip()
        if not raw_img_path or raw_img_path.lower() in ['none', 'nan', '']:
            clean_name = name.lower().replace(' ', '_').replace("'", "")
            image_path = f"data/images/{clean_name}.jpg"
        else:
            image_path = raw_img_path

        # 1. Text Embedding
        text_vector = generate_text_embedding(description)
        text_vector_str = str(text_vector) if text_vector else None

        # 2. Image Embedding using Absolute Path
        abs_img_path = os.path.abspath(image_path)
        image_vector_str = None
        
        if os.path.exists(abs_img_path):
            image_vector = generate_image_embedding_from_file(abs_img_path)
            if image_vector:
                image_vector_str = str(image_vector)
                print(f"  └─ ✅ Visual vector generated for {image_path}")
            else:
                print(f"  └─ ⚠️ Failed to compute vector for {image_path}")
        else:
            print(f"  └─ Notice: No file found at '{abs_img_path}'. Vector set to NULL.")

        # 3. Database Insert
        insert_query = """
            INSERT INTO destinations (
                name, category, district, entrance_fee, accessibility, 
                trekking_difficulty, description, image_path, 
                text_embedding, image_embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s::vector);
        """

        cur.execute(insert_query, (
            name,
            str(row.get('category', 'attraction')).lower().strip(),
            str(row.get('district', 'Sri Lanka')).strip(),
            float(pd.to_numeric(row.get('entrance_fee', 0.0), errors='coerce') or 0.0),
            str(row.get('accessibility', 'Moderate')),
            str(row.get('trekking_difficulty', 'N/A')),
            description,
            image_path,
            text_vector_str,
            image_vector_str
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("\n✅ Data ingestion completed successfully!")

if __name__ == '__main__':
    ingest_destinations()