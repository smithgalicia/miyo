#!/usr/bin/env python3
# Build a IIIF Presentation v2.1 manifest from one or more static info.json folders.
# Run this from INSIDE the "site" folder that contains the image sub-folders.
# Usage: python make_manifest.py <prefix_url> "<label>" <id1> [<id2> ...]
# Example:
#   python make_manifest.py "https://USERNAME.github.io/genji-iiif" "Genji album leaf" colophon sheet
import sys, json, os

prefix = sys.argv[1].rstrip('/')
label  = sys.argv[2]
ids    = sys.argv[3:]

def load_info(iid):
    with open(os.path.join(iid, 'info.json')) as f:
        return json.load(f)

canvases = []
for n, iid in enumerate(ids, 1):
    info = load_info(iid)
    w, h = info['width'], info['height']
    svc  = f"{prefix}/{iid}"
    sizes = info.get('sizes', [{'width': w, 'height': h}])
    big   = max(sizes, key=lambda s: s['width'])          # largest whole-image size generated
    img_url   = f"{svc}/full/{big['width']},/0/default.jpg"
    canvas_id = f"{prefix}/canvas/p{n}"
    canvases.append({
        "@id": canvas_id, "@type": "sc:Canvas", "label": iid,
        "width": w, "height": h,
        "images": [{
            "@id": f"{prefix}/annotation/p{n}", "@type": "oa:Annotation",
            "motivation": "sc:painting", "on": canvas_id,
            "resource": {
                "@id": img_url, "@type": "dctypes:Image", "format": "image/jpeg",
                "width": big['width'], "height": big['height'],
                "service": {
                    "@context": "http://iiif.io/api/image/2/context.json",
                    "@id": svc,
                    "profile": "http://iiif.io/api/image/2/level0.json"
                }
            }
        }]
    })

manifest = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": f"{prefix}/manifest.json", "@type": "sc:Manifest", "label": label,
    "sequences": [{"@id": f"{prefix}/sequence/normal", "@type": "sc:Sequence",
                   "canvases": canvases}]
}
with open('manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print("wrote manifest.json with", len(canvases), "canvas(es)")
