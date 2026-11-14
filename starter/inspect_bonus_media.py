import json
from pathlib import Path
import pypdf

reader = pypdf.PdfReader('data/bonus.pdf')
out_dir = Path('data/bonus_figures')
out_dir.mkdir(parents=True, exist_ok=True)

all_images = []
for p_idx, page in enumerate(reader.pages, start=1):
    for img in page.images:
        all_images.append({
            'page': p_idx,
            'name': img.name,
            'size': len(img.data)
        })
        # Save image
        img_path = out_dir / f"p{p_idx}_{img.name}"
        if not img_path.exists():
            img_path.write_bytes(img.data)

print(f"Total images found: {len(all_images)}")
pngs = [x for x in all_images if x['name'].lower().endswith('.png')]
print(f"Total PNG images (often diagrams/charts): {len(pngs)}")
for p in pngs:
    print(f"Page {p['page']}: {p['name']} ({p['size']} bytes)")

jpgs = [x for x in all_images if x['name'].lower().endswith(('.jpg', '.jpeg'))]
print(f"Total JPG images: {len(jpgs)}")

