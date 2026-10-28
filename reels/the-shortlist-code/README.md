# Reel: The Shortlist Code

Instagram Reel (1080×1920, 29 s) for https://skillpilotofficial.com/products/the-shortlist-code.
Notebook edit: five pages flip over a spiral binding, one page per part of the script.

| Time | Page | What happens |
|---|---|---|
| 0.0–4.4 | p.01 | STOP stamp, same resume copied into five applications, "no reply" × 5, callbacks: 0 |
| 4.9–10.9 | p.02 | Red-pen audit (structure, skills, achievements), recruiter scan, NOT SHORTLISTED stamp |
| 11.4–18.0 | p.03 | Cover drop, logo sticker, ×6 templates (3 locked), sample resume, locked role guides |
| 18.4–21.7 | p.04 | Job post keywords highlighted, resume bullets rewritten, 3/3 keywords matched |
| 22.4–29.0 | p.05 | Sticky note on "Send application", comment box types RESUME, DM with the link, end card |

Output: `the-shortlist-code-reel.mp4`. Rebuild with `./build.sh` (needs ffmpeg, Node + Playwright, Python + numpy).

## Adding real product images and reviews

The store domain could not be reached from the session that built this reel, so the template
thumbnails are drawn wireframes and no reviews are shown. To use the real thing:

- **Product previews:** put page screenshots in `previews/` (`01.png` … `06.png`, sorted by name).
  They replace the six template thumbnails on p.03 (files 4–6 stay blurred behind a lock) and the
  blurred fan on the end card.
- **Reviews:** fill `data/reviews.json` with real, published reviews, e.g.
  `[{"name": "A. Sharma", "rating": 5, "text": "…", "verified": true}]`.
  The first two replace the "Send application" form at 22.4–24.5 s.

Then run `./build.sh`.

## Files

- `reel.html` — all scenes, drawn and animated from `render(t)`
- `capture.js` — renders frames with Playwright and pipes them to ffmpeg
- `audio.py` — voice cleanup (high-pass, denoise, EQ, de-ess, compression, -16 LUFS stem),
  a synthesized music bed ducked under the voice, synthesized sound effects, final mix at -14 LUFS
- `data/words.json` — word timings from forced alignment of the script against the voice-over
- `fonts/` — Caveat and Permanent Marker (SIL OFL, licences included)
