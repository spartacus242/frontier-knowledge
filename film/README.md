# The homepage film

`render.py` draws every frame of `site/film/the-edge-of-the-known.mp4` from code
(Python, NumPy, Pillow, ffmpeg). Each element is a function of time, so a
change to the story is an edit here and a re-render:

    python3 film/render.py out.mp4 24              # whole film, x264 CRF 25
    python3 film/render.py --still 109.5 frame.png  # one frame (the poster)

When the words change, update the film's transcript in `site/index.html` too.
It expects the Caladea, Inter and DejaVu Sans Mono fonts at the paths at the
top of the script. The film is licensed CC BY-SA 4.0.
