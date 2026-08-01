from transformers import CLIPModel, CLIPProcessor

print("Downloading clean CLIP model and processor...")
CLIPModel.from_pretrained("openai/clip-vit-base-patch32", force_download=True)
CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", force_download=True)
print("CLIP successfully downloaded!")