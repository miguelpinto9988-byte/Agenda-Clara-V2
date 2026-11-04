#!/usr/bin/env python3
"""Phase 17: sanitize all 30 numbered scenic PNGs, losslessly preserving scenery.

The 30 source PNGs include the number inside a blue corner badge; 08 on
2026-11-04 is artwork baked into bg_mi_dia_08.png, not an Android TextView.
Reconstruct the covered sky/foliage by mirroring neighboring pixels, with a
feathered right/bottom transition. This leaves the middle 70% and entire lower
75% untouched. Images remain separate, in the same order, available offline.

Requires Pillow; intentionally run after the phase51 resource installer and
after phase64 header changes, before compilation (on explicit later approval).
"""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
from tempfile import TemporaryDirectory
import json
import os
from PIL import Image

RES = Path("AgendaClara/app/src/main/res/drawable-nodpi")
MANIFEST = Path("AgendaClara/.mi_dia_bg_clean_v1.json")
EXPECTED_SHA256 = (
    "f65e85513e20ae2f36ea74ec23a8a634091643de7783351e9d2c34d6e2b46a33",
    "f85b1fac34182b00ff78f9f5b11d4c7a8021cbf258a3de0e79a6c41c26928b60",
    "47fb6b5eb6717b615a52906fb8d2518c5316436e3b55b37db9482f50f5f2d27d",
    "146bde86df38b64f250069f9f173f9002c4f21bac4f5b7608fd875dc6747473b",
    "1ec4c0e47c3eeec3f8ab07e3176ffe666d41bd028be673f997507d126ea00922",
    "651dde729d237d06c6050bb52994ec1f9efd6503cc7b98c83c5f234684dbf424",
    "daee6de615474f6c6611171bc27b61c358f668d255935071f0a71b72e721c8c9",
    "15d6e7df9b457d2fa9c50a9a9e5f0e4c5678d8abb10e73add0a22d6910c7aa3d",
    "181f5c4fcbce1752685456894b6598d6fd96b54097cd9b3aaa5e37851a328018",
    "e18161d4347c7f381d5a91edb1d43fb8ceb46b1efcb45b24701b75a003aae649",
    "35d6fff15df4b8afa43ad1e23d0241386c31b32b44f8b57a36bcf40107892232",
    "852fbe222c7bf69e5502fc32c404b610cb8e3bdbce343489ede60a3231d34b99",
    "838470b8e9fa7fce132b43c4024068720de97068566c75fa1cdc0cba4d50df5b",
    "43dc257f508869fc89d12318c3cb7ba025ef5a5ff52a1baac49d123b4cfc45ed",
    "57ebe611224b1fcd613763bd40a4bb42bebfa1cc759b673f9e78087aafd3e45e",
    "4f0069593236b518a9484152bb2b1aa1072f846c5ad7d0166f155d0307413a85",
    "bc027fc37011a11b9806ca88245216ce70ae886b5dacdb840feb5233bd8576e2",
    "3bb52a304921ebbcd98fd27a15d171cf1a761edfdee6812a5bbc60491e65f43d",
    "1dd8da4de2496206e6367bac8d6689614e6ae7cf9a9eb289ecf470e8721def9e",
    "604cd9596c9418c8fe19fdf2fe3ce116ad280a2d29c2ae36804e617875b49724",
    "0287bb7ff80b351177cf3ca899f9ef75bffc1f77f43266aa4c9d1e8a02b19b64",
    "24e2f16ac62854b1f22cd86e0f71632a841ea5a9402753140b6ccad3cbe204cb",
    "0ba366889c06babc797eef8f4dcdc9a16f5b01c7c9687b4ddd8a2e7d39367dce",
    "497cbc53d40c51a8f8682a6cdc900ee7c25a51a5576ea4d66f4a6b350fba3801",
    "c13faf1de86a2eb2a93b25ee0a81e1953a4f0edb6622f0e9b1b917b9af7c8605",
    "06ebde37c515dbd4cfbc8b24932de55c77f1ad1e329887b16c05cdde8067eb37",
    "c9943151c4a5755c158e8ac8b3274384a3bbe6ca8aa5a0c0c810ba18ac687ae1",
    "808f05ea06978ba96dadfa662136749a0bd38a4a29028e6395134033629446e3",
    "53c87ca6eb49e9042f0c3b615c29346eb1cf13da5356d9023cc54b384b4c038b",
    "5ea1ae4695a0fe65219b23f6d0e3cd7220c2fa548902c6b64a13a101b61e6e58",
)
COUNT = 30
WIDTH, HEIGHT = 1920, 864
PATCH_W, PATCH_H = 560, 215
OPAQUE_X, OPAQUE_Y = 455, 135
METHOD = "mirror-nearby-scenery-feathered-v1"

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def paths():
    return [RES / ("bg_mi_dia_%02d.png" % i) for i in range(1, COUNT + 1)]

def alpha_mask():
    # 255 throughout the actual number badge; fade only in known clean areas.
    return Image.frombytes("L", (PATCH_W, PATCH_H),
        bytes(round(255 * min(1., (PATCH_W - x) / (PATCH_W - OPAQUE_X))
                        * min(1., (PATCH_H - y) / (PATCH_H - OPAQUE_Y)))
              for y in range(PATCH_H) for x in range(PATCH_W)))

def transform(original, alpha):
    image = Image.open(BytesIO(original))
    image.load()
    if image.size != (WIDTH, HEIGHT) or image.mode not in ("P", "RGB"):
        raise RuntimeError("Unsupported artwork dimensions or PNG color mode")
    before = image.convert("RGB")
    clean_corner = before.crop((PATCH_W, 0, 2 * PATCH_W, PATCH_H))
    clean_corner = clean_corner.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    corner_rgb = before.crop((0, 0, PATCH_W, PATCH_H))
    corner_rgb.paste(clean_corner, (0, 0), alpha)
    if image.mode == "P":
        # Quantize only the affected corner: outside pixels keep the EXACT
        # original indexed palette bytes, with no unintended recoloring.
        corner_indexed = corner_rgb.quantize(palette=image, dither=Image.Dither.NONE)
        exact_mirror = image.crop((PATCH_W, 0, 2 * PATCH_W, PATCH_H))
        exact_mirror = exact_mirror.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        opaque_mask = alpha.point(lambda value: 255 if value == 255 else 0)
        corner_indexed.paste(exact_mirror, (0, 0), opaque_mask)
        image_out = image.copy()
        image_out.paste(corner_indexed, (0, 0))
    else:
        image_out = image.copy()
        image_out.paste(corner_rgb, (0, 0))
    data = BytesIO()
    image_out.save(data, format="PNG", optimize=True)
    clean_bytes = data.getvalue()
    result = Image.open(BytesIO(clean_bytes)).convert("RGB")
    # A pixel outside the corner mask MUST remain exactly unchanged.
    for xy in ((WIDTH // 2, HEIGHT // 2), (WIDTH - 20, 20),
               (20, HEIGHT - 20), (PATCH_W + 20, PATCH_H + 20)):
        if before.getpixel(xy) != result.getpixel(xy):
            raise RuntimeError("Original scenery changed outside number patch")
    # The number badge is within this fully-opaque region.
    if result.getpixel((110, 25)) != before.getpixel((2 * PATCH_W - 1 - 110, 25)):
        raise RuntimeError("Image corner could not be sanitized")
    return clean_bytes

def run():
    files = paths()
    if any(not p.is_file() for p in files):
        raise RuntimeError("All 30 backgrounds must be installed before phase17")
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        hashes = manifest.get("outputs")
        if manifest.get("algorithm") != METHOD or not isinstance(hashes, dict):
            raise RuntimeError("Unrecognized previous artwork conversion")
        if all(hashes.get(p.name) == digest(p) for p in files):
            print("PASS phase17: 30 backgrounds already normalized; manifest verified")
            return
        raise RuntimeError("Partially changed artwork, refusing second conversion")
    actual = [digest(p) for p in files]
    if tuple(actual) != EXPECTED_SHA256:
        raise RuntimeError("Artwork no longer matches the 30 approved source images; "
                           "refusing to overwrite unrelated assets")
    mask = alpha_mask()
    outputs = {}
    with TemporaryDirectory(prefix="mi_dia_backgrounds_clean_") as folder:
        tmp = Path(folder)
        for i, original_path in enumerate(files, start=1):
            candidate = tmp / original_path.name
            candidate.write_bytes(transform(original_path.read_bytes(), mask))
            outputs[original_path.name] = digest(candidate)
            print("PASS cleaned background %02d/30" % i)
        if len(set(outputs.values())) != COUNT:
            raise RuntimeError("Distinct image resource identity lost")
        # Only after validating all thirty are final resources replaced.
        for original_path in files:
            os.replace(tmp / original_path.name, original_path)
    MANIFEST.write_text(json.dumps({
        "algorithm": METHOD,
        "source": {p.name: h for p, h in zip(files, actual)},
        "outputs": outputs,
        "patch": {"width": PATCH_W, "height": PATCH_H,
                  "opaque_until_x": OPAQUE_X, "opaque_until_y": OPAQUE_Y},
        "rotation": "MiDiaDailyRotation.backgroundIndex unchanged",
        "count": COUNT
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS phase17: 30 numbered labels removed; 1920x864, palette, originals and rotation preserved")

if __name__ == "__main__":
    run()
