from src.database import get_db_connection
from src.embeddings import (
    generate_text_embedding,
    generate_image_embedding_from_file,
    generate_clip_text_embedding
)

# ----------------- 1. STRUCTURED SEARCH (SQL) -----------------
def structured_search(category: str = None, max_fee: float = None):
    """Executes a standard relational SQL query with optional filters."""
    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT id, name, category, district, entrance_fee, description, image_path FROM destinations WHERE 1=1"
    params = []

    if category:
        query += " AND LOWER(category) = %s"
        params.append(category.lower().strip())
    if max_fee is not None:
        query += " AND entrance_fee <= %s"
        params.append(max_fee)

    cur.execute(query, tuple(params))
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(zip(colnames, row)) for row in rows]


# ----------------- 2. SEMANTIC SEARCH (TEXT VECTOR) -----------------
def semantic_search(query_text: str, top_k: int = 3):
    """Performs cosine similarity search using MiniLM text embeddings."""
    query_vector = generate_text_embedding(query_text)
    if not query_vector:
        return []

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT id, name, category, district, entrance_fee, description, image_path,
               (text_embedding <=> %s::vector) AS cosine_distance
        FROM destinations
        WHERE text_embedding IS NOT NULL
        ORDER BY cosine_distance ASC
        LIMIT %s;
    """

    cur.execute(query, (str(query_vector), top_k))
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(zip(colnames, row)) for row in rows]


# ----------------- 3. IMAGE SEARCH BY FILE (IMAGE-TO-IMAGE) -----------------
def image_similarity_search_by_file(image_path: str, top_k: int = 2):
    """Finds visually similar destinations using an uploaded input image file."""
    image_vector = generate_image_embedding_from_file(image_path)
    if not image_vector:
        return []

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT id, name, category, district, entrance_fee, description, image_path,
               (image_embedding <=> %s::vector) AS distance
        FROM destinations
        WHERE image_embedding IS NOT NULL
        ORDER BY distance ASC
        LIMIT %s;
    """

    cur.execute(query, (str(image_vector), top_k))
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(zip(colnames, row)) for row in rows]


# ----------------- 4. IMAGE SEARCH BY TEXT (TEXT-TO-IMAGE) -----------------
def image_similarity_search_by_text(query_text: str, top_k: int = 2):
    """Finds destinations matching a textual query in the CLIP image embedding space."""
    query_vector = generate_clip_text_embedding(query_text)
    if not query_vector:
        return []

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT id, name, category, district, entrance_fee, description, image_path,
               (image_embedding <=> %s::vector) AS distance
        FROM destinations
        WHERE image_embedding IS NOT NULL
        ORDER BY distance ASC
        LIMIT %s;
    """

    cur.execute(query, (str(query_vector), top_k))
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(zip(colnames, row)) for row in rows]


# ----------------- 5. HYBRID SEARCH (SQL + VECTOR) -----------------
def hybrid_search(query_text: str, category: str = None, max_fee: float = None, top_k: int = 3):
    """Combines relational SQL filtering with semantic vector search."""
    query_vector = generate_text_embedding(query_text)

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT id, name, category, district, entrance_fee, accessibility, trekking_difficulty, description, image_path,
           (text_embedding <=> %s::vector) AS cosine_distance
    FROM destinations
    WHERE text_embedding IS NOT NULL
    """
    params = [str(query_vector)]

    if category:
        query += " AND LOWER(category) = %s"
        params.append(category.lower().strip())
    if max_fee is not None:
        query += " AND entrance_fee <= %s"
        params.append(max_fee)

    query += " ORDER BY cosine_distance ASC LIMIT %s;"
    params.append(top_k)

    cur.execute(query, tuple(params))
    colnames = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(zip(colnames, row)) for row in rows]