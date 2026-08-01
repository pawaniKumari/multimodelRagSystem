import os
import streamlit as st
from src.retriever import (
    structured_search,
    semantic_search,
    image_similarity_search_by_file,
    image_similarity_search_by_text,
    hybrid_search
)
from src.rag_chain import generate_multimodal_rag_response

st.set_page_config(page_title="Tourism Assistant", layout="wide")
st.title("Your Sri Lankan Tourism Assistant 🤖")

# Navigation Tabs as required by assignment deliverables
tab1, tab2, tab3, tab4 = st.tabs([
    "🔀 Hybrid Search", 
    "📊 Structured Search", 
    "📝 Text Search", 
    "🖼️ Image Search"
])

# Helper function to render images safely without raising TypeError
def render_destination_image(image_path, width=300):
    if image_path and isinstance(image_path, str) and os.path.exists(image_path):
        st.image(image_path, width=width)
    else:
        st.caption("📷 No local image available")

# ----------------- TAB 1: HYBRID SEARCH (MAIN DEMO) -----------------
with tab1:
    st.header("Hybrid Search")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        category_filter = st.selectbox("Category", ["All", "waterfalls", "historical sites", "wildlife", "temples", "beaches"])
        max_fee = st.number_input("Max Entrance Fee (LKR)", min_value=0, value=3000, step=100)
        query_text = st.text_input("Ask a question about Sri Lankan tourist places:")
        search_btn = st.button("Generate Answer")

    with col2:
        if search_btn and query_text:
            cat = None if category_filter == "All" else category_filter
            
            with st.spinner("Searching & generating response..."):
                retrieved_docs = hybrid_search(query_text, category=cat, max_fee=max_fee, top_k=3)
                rag_response = generate_multimodal_rag_response(query_text, retrieved_docs)
            
            st.subheader("🤖 Generated Response")
            st.write(rag_response)
            
            st.subheader("📚 Retrieved Context")
            if retrieved_docs:
                for doc in retrieved_docs:
                    distance = round(float(doc['cosine_distance']), 4) if 'cosine_distance' in doc else "N/A"
                    with st.expander(f"{doc['name']} - Distance: {distance}"):
                        st.write(f"**Category:** {doc.get('category', 'N/A')} | **Fee:** LKR {doc.get('entrance_fee', 0)}")
                        st.write(f"**Description:** {doc.get('description', '')}")
                        render_destination_image(doc.get('image_path'))
            else:
                st.info("No matching destinations found for your search.")

# ----------------- TAB 2: STRUCTURED SEARCH -----------------
with tab2:
    st.header("Structured Search")
    struct_cat = st.selectbox("Filter Category", ["waterfalls", "historical sites", "wildlife", "attraction"])
    struct_fee = st.slider("Maximum Fee (LKR)", 0, 5000, 1500)
    
    if st.button("Run SQL Search"):
        with st.spinner("Finding..."):
            results = structured_search(category=struct_cat, max_fee=struct_fee)
        
        if results:
            st.dataframe(results)
        else:
            st.info("No records matched the selected SQL criteria.")

# ----------------- TAB 3: SEMANTIC SEARCH -----------------
with tab3:
    st.header("Text Search")
    semantic_q = st.text_input("Enter the question (e.g. 'tall water drops in mountains'):")
    
    if st.button("Run Semantic Search"):
        if semantic_q:
            with st.spinner("Searching..."):
                results = semantic_search(semantic_q, top_k=3)
            
            if results:
                for res in results:
                    st.markdown(f"### {res['name']}")
                    st.write(res.get('description', ''))
                    st.divider()
            else:
                st.info("No matches found.")
        else:
            st.warning("Please enter question.")

# ----------------- TAB 4: IMAGE SIMILARITY SEARCH -----------------
with tab4:
    st.header("Image Search")
    img_mode = st.radio("Search Mode", ["Text-to-Image", "Image-to-Image"])
    
    if img_mode == "Text-to-Image":
        txt_img_q = st.text_input("Describe the image you want to find (e.g., 'leopard in safari forest'):")
        if st.button("Search Image by Text"):
            if txt_img_q:
                with st.spinner("Searching images..."):
                    results = image_similarity_search_by_text(txt_img_q, top_k=2)
                
                if results:
                    for res in results:
                        st.write(f"**{res['name']}**")
                        render_destination_image(res.get('image_path'))
                else:
                    st.info("No visually matching images found.")
            else:
                st.warning("Please describe the image you are searching for.")
                    
    else:
        uploaded_img = st.file_uploader("Upload an image file:", type=["jpg", "jpeg", "png"])
        if uploaded_img:
            # Display uploaded image preview using raw bytes directly in Streamlit memory
            st.image(uploaded_img, caption="Uploaded Input Image", width=200)
            
            if st.button("Search Similar Places"):
                temp_path = f"temp_{uploaded_img.name}"
                
                try:
                    with st.spinner("Processing uploaded image..."):
                        # Save temp file on disk for embedding generation
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_img.getbuffer())
                        
                        results = image_similarity_search_by_file(temp_path, top_k=2)
                    
                    if results:
                        for res in results:
                            st.write(f"**Matched Place:** {res['name']}")
                            render_destination_image(res.get('image_path'))
                    else:
                        st.info("No visually similar destinations found in the database.")
                        
                finally:
                    # Clean up temporary upload file immediately after search completes
                    if os.path.exists(temp_path):
                        os.remove(temp_path)