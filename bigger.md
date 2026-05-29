# Finding Larger Versions of Site Images

## Goal
Replace small web images on otlstudio.com with larger versions found elsewhere on the machine.

## Approach
1. **Catalog site images** — walk the otlstudio media/image files, record filenames and pixel dimensions
2. **Perceptual hashing** — generate a pHash for each site image using Python `imagehash` library. Unlike MD5, pHash compares visual content so a 4000px original matches its 300px web thumbnail
3. **Search candidate folders** — walk specified directories and Apple Photos, hash each image
4. **Match and compare** — find perceptually similar images where the candidate is larger than the site version
5. **Report** — output a list of matches: site image path, current size, candidate path, candidate size

## Candidate search locations
- Folders TBD (Colin to specify)
- Apple Photos library: `~/Pictures/Photos Library.photoslibrary/originals/` (or use `osxphotos` Python library for cleaner access)

## Dependencies
```
pip install imagehash Pillow osxphotos
```

## Notes
- Could also apply to pogsummers.com and mightycheese.com
- The script should be tolerant of different formats (JPEG, PNG, HEIC) and aspect ratio crops
- Consider a similarity threshold (hamming distance) rather than exact pHash match
