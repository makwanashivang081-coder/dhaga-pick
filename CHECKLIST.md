# Dhaga Pick — UI checklist

## Done (handwritten note + first build)

- [x] Simpler UI — recipe strips instead of needle-by-needle flow
- [x] Neck / part dropdown removed
- [x] 5 recipe strips with spacing (paint-chip style)
- [x] Tap recipe 1–5 to switch choice
- [x] 6 extra colour options under strips
- [x] Thread colour shown after tap (name + shade)
- [x] Chosen cloth palette strip (light / mid / dark)
- [x] Bold WhatsApp-style colours
- [x] No hover on strip / needle pick (touch-first)
- [x] English only UI (Gujarati removed)

## Done (photo cloth + final canvas update)

- [x] Photo-first cloth colour — tap cloth photo, app guesses colour
- [x] User approval — Yes / pick different before recipes load
- [x] Shade slider removed — no light/dark bar
- [x] Dhaga = colour strip — main visual is horizontal thread strip
- [x] Needle number in cloth colour — badge uses cloth, strip uses thread
- [x] Final full-screen view — background = cloth colour, all needles shown as strips
- [x] Server API — `POST /api/detect-cloth-color` from cloth photo
- [x] Manual swatch fallback if photo guess is wrong

## Still optional / later

- [ ] Tap a point on photo to sample colour (currently centre crop)
- [ ] 6 needles (data model max is 5 today)
