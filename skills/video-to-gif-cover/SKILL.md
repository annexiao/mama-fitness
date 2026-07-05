---
name: video-to-gif-cover
description: Turn a segment of a real video (YouTube / Bilibili / local file) into a looping GIF, and optionally frame it to a fixed aspect ratio for use as a card/gallery cover image. Use whenever the task is "make a GIF from this video at these timestamps", "clip this to a looping demo", "the cover GIF cuts off the person / only shows the background", or building an exercise/product/tutorial gallery where each item needs an animated cover. Covers the full pipeline: download (Bilibili needs nightly yt-dlp), inspect a frame to find the subject + ad bands, choose a framing strategy (direct crop vs blurred-background for portrait-in-landscape), encode with the ffmpeg palette pipeline, and compress with gifsicle to a target size.
---

# Video → GIF → (optional) cover

Make a looping GIF from a video segment, and optionally frame it to a fixed aspect
ratio so it works as a gallery/card cover without cutting off the subject.

Born from a family fitness site: exercise cards each show an
animated cover GIF cropped from a real demo video. The two failure modes that drove this
skill: (1) Bilibili downloads 412'ing on stale yt-dlp, and (2) a portrait standing-person
GIF dropped into a 4/3 landscape cover with `object-fit:cover` → only the ceiling/background
survives the crop, the person is gone.

## The one rule that prevents most rework

**Extract a still frame and LOOK before you encode.** Every decision below — where the
subject is, whether there are ad/watermark bands to crop out, portrait vs landscape, which
2-3 seconds are clean (no camera cut mid-clip) — is a visual judgment. Guessing the crop
numbers and encoding a 5s GIF, then discovering the subject is half out of frame, wastes a
full download+encode cycle. One `ffmpeg -ss T -frames:v 1 frame.png` + Read is far cheaper.

## Pipeline

### 1. Download the source

```bash
# YouTube (watch OR shorts URL) — homebrew yt-dlp is usually fine, but uvx nightly is safest
uvx --prerelease=allow yt-dlp -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 \
  -o "src.%(ext)s" "<URL>"
```

**Format-selector gotcha:** some videos have only a 4K-webm best video with no mp4-mergeable
audio, and `bv*[height<=1080]+ba/b` can silently produce an **empty file** (ffprobe shows no
dimensions). If that happens, use the explicit mp4-first fallback chain:
```bash
uvx --prerelease=allow yt-dlp \
  -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 -o "src.%(ext)s" "<URL>"
```
Always `ffprobe` the result before proceeding — an empty/zero-dimension file means the
selector matched nothing usable, not that the video is gone.

**Bilibili gotcha (non-negotiable):** Bilibili uses WBI request signing; a stale yt-dlp
(homebrew) fails with **HTTP 412 Precondition Failed**. Use the **nightly** build via
`uvx --prerelease=allow yt-dlp` — it carries the current signing logic. This is the same
tool invocation for YouTube, so just always use it.

Then probe:
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration \
  -of csv=p=0 src.mp4
```
Note the **aspect ratio** (portrait 9:16 vs landscape 16:9) and **duration** — both drive
the next choices.

### 2. Inspect a representative frame

```bash
ffmpeg -y -ss <mid-segment-seconds> -i src.mp4 -frames:v 1 frame.png
```
Read `frame.png` and answer:
- **Where is the subject?** (bounding box; is it centered or off to a side/bottom?)
- **Which way is the subject oriented?** Lying down / horizontal → *landscape-friendly*.
  Standing / vertical → *portrait subject* (the hard case for a wide cover).
- **Are there ad / watermark / subscribe bands?** Shorts and re-uploads often have a
  title bar on top and a "SUBSCRIBED"/like-bell band on the bottom. Note their y-pixel
  boundaries — you will crop them out.
- **Does the subject move across the frame?** (lateral walks, monster walks) → the crop
  must be wide enough to contain the whole movement range, or the subject walks out.

If the clip has a **camera cut or zoom mid-segment**, pick a sub-range that's one continuous
shot — check the first and last frame of your intended range, not just the middle.

### 3. Choose a framing strategy

Only relevant if the GIF will be a **fixed-aspect cover** (e.g. a `.cover{aspect-ratio:4/3}`
box with `object-fit:cover`). If the GIF is shown at its native ratio, skip to step 4.

**The root cause to internalize:** `object-fit:cover` scales the image to *fill* the box and
crops the overflow. A portrait GIF in a landscape box → top+bottom cropped → only the
horizontal-center band survives. If the subject isn't in that band, it's gone. So the GIF's
own aspect ratio should match the cover, framed so the subject survives.

| Situation | Strategy |
|---|---|
| Subject is **horizontal** (lying), OR source is landscape and tall enough to fit a standing subject in the target ratio | **Direct crop** to the target ratio around the subject. Fills the cover, no bars. |
| Subject is **standing/portrait** and can't fit the wide target ratio without cutting off head or feet | **Blurred-background** composite (below). Whole subject stays visible, sharp, centered; blurred zoomed copy fills the sides. This is what YouTube/Instagram do for vertical video in a horizontal player. |

To decide "tall enough": for target ratio `W:H`, a direct crop of the subject's full height
`h` needs width `h*(W/H)`. If that's ≤ the source width AND the subject's horizontal extent
fits in it, direct crop works. Otherwise use blurred-bg.

### 4a. Encode — direct crop (fills the cover)

`crop=CW:CH:CX:CY` picks the window; choose CW:CH to the **exact target ratio** (e.g.
`608:456` = 4/3) and position CX:CY to (a) center the subject and (b) exclude ad bands.

```bash
ffmpeg -y -ss <start> -t <dur> -i src.mp4 \
  -vf "crop=608:456:0:372,fps=10,scale=400:-1:flags=lanczos,\
split[a][b];[a]palettegen=stats_mode=diff:max_colors=80[p];\
[b][p]paletteuse=dither=bayer:bayer_scale=3" out.gif
```
(Example: source content lives y155–830 between two ad bands; a 456-tall window at y372
sits cleanly inside it.)

### 4b. Encode — blurred-background (portrait subject in a wide cover)

Two passes: composite first, then GIF. `CROP` = the subject's bounding box (crop away empty
room so the subject isn't tiny). `force_original_aspect_ratio=increase`+`crop` makes the
blurred bg *cover* the canvas; `=decrease` makes the sharp fg *fit* inside it — so the whole
subject is always visible whether the crop is portrait or landscape.

```bash
# target canvas here is 4/3 (480x360). Adjust to your cover ratio.
ffmpeg -y -ss <start> -t <dur> -i src.mp4 -filter_complex \
"[0:v]crop=CW:CH:CX:CY,setsar=1[c];[c]split[a][b];\
[a]scale=480:360:force_original_aspect_ratio=increase,crop=480:360,gblur=sigma=14[bg];\
[b]scale=480:360:force_original_aspect_ratio=decrease[fg];\
[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=10" -an comp.mp4

ffmpeg -y -i comp.mp4 -vf \
"scale=400:-1:flags=lanczos,split[a][b];\
[a]palettegen=stats_mode=diff:max_colors=80[p];\
[b][p]paletteuse=dither=bayer:bayer_scale=3" out.gif
```

### 5. Compress to target size

Gallery covers should be small (aim **< ~850KB**, ideally < 600KB). The palette pipeline
alone often isn't enough — the blurred bg adds gradient noise. Finish with gifsicle:

```bash
brew install gifsicle   # once
gifsicle -O3 --lossy=100 --colors 72 -o out.gif out.gif
```

If still too big: shorten the clip (2-4s is plenty for a loop), drop `fps` to 8, or narrow
`--colors` to 64. `stats_mode=diff` (only palettes the moving pixels) already helps a lot.

### 6. Verify visually, then wire up

Extract the GIF's first frame and Read it to confirm the subject is fully framed:
```bash
ffmpeg -y -i out.gif -frames:v 1 check.png
```
For a data-driven site, drop the GIF into the assets dir and reference it from the content
file (YAML/JSON) — the filename stays stable so re-encoding a better version needs no data
change.

## Encoding defaults (good starting points)

- **fps 10** (8 for long/heavy clips, 12 if motion is fast and size allows)
- **width 400** for gallery covers (scale height by ratio: `scale=400:-1`)
- **max_colors 72-80**, `palettegen=stats_mode=diff`, `paletteuse=dither=bayer:bayer_scale=3`
- **clip length 2-5s** — a loop doesn't need a full rep cycle to read
- **gblur sigma 14-18** for the blurred background

## Gotchas

- **Bilibili 412** → nightly yt-dlp (`uvx --prerelease=allow yt-dlp`). Homebrew's is stale.
- **`object-fit:cover` eats portrait subjects** in a landscape box. Match the GIF ratio to
  the cover, or use blurred-bg. This is the single most common "the cover looks broken" bug.
- **Ad/watermark bands** ride on re-uploaded clips — crop them out; don't ship a "SUBSCRIBE"
  bell in a product cover.
- **Camera cut mid-clip** → check first+last frame of your range; trim to one continuous shot.
- **Lateral-movement exercises** need a crop wide enough for the whole travel, or the subject
  walks out of frame.
- **Content accuracy** (if labeling): make sure the clip actually shows the movement the card
  claims. A side-*lying* demo on a card titled "*standing* leg raise" is a mismatch — flag it
  or rename the item; don't ship "close enough".
- **gifsicle not installed** → `brew install gifsicle`. Without it, the palette pipeline is
  your only lever and heavy/blurred GIFs stay large.

## Related

- Local file input works the same — skip step 1, point ffmpeg at the file.
- For the *cover width/framing* design side (aspect ratios, `object-fit`), this pairs with
  the web UI rules; this skill owns the *media production*, not the CSS.
