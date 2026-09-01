import math
import random
import os
import shutil
import json
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageSequence


# --- Random harmonograph parameters ---
def rand_harmonograph():
    # 2D harmonograph: sum of 2 damped sinusoids in x and y
    # x(t) = A1*sin(f1*t+p1)*e^(-d1*t) + A2*sin(f2*t+p2)*e^(-d2*t)
    # y(t) = A3*sin(f3*t+p3)*e^(-d3*t) + A4*sin(f4*t+p4)*e^(-d4*t)

    base = random.uniform(1.2, 3.0)
    ratios = [
        1.0,
        random.choice([1.5, 2.0, 2.5, 3.0]),
        random.choice([1.25, 1.6, 2.2, 2.8]),
    ]

    f1 = base * ratios[0]
    f2 = base * ratios[1]
    f3 = base * ratios[2]
    f4 = base * random.choice([1.0, 1.4, 2.0, 2.6])

    A = [random.uniform(0.4, 1.0) for _ in range(4)]
    p = [random.uniform(0, 2 * math.pi) for _ in range(4)]
    d = [random.uniform(0.0015, 0.01) for _ in range(4)]

    return (A, (f1, f2, f3, f4), p, d)


def point(t, A, f, p, d):
    x = (
        A[0] * math.sin(f[0] * t + p[0]) * math.exp(-d[0] * t)
        + A[1] * math.sin(f[1] * t + p[1]) * math.exp(-d[1] * t)
    )

    y = (
        A[2] * math.sin(f[2] * t + p[2]) * math.exp(-d[2] * t)
        + A[3] * math.sin(f[3] * t + p[3]) * math.exp(-d[3] * t)
    )

    return x, y


# --- Render a GIF ---
def render_gif(
    out_path="harmonograph.gif",
    size=720,
    frames=240,
    steps_per_frame=350,
    t_step=0.012,
    bg=(0, 0, 0, 0),
    fg=(255, 255, 255, 255),
    line_width=2,
):
    A, f, p, d = rand_harmonograph()

    # Pre-scan to auto-scale nicely
    sample_n = 6000
    xs, ys = [], []
    t = 0.0

    for _ in range(sample_n):
        x, y = point(t, A, f, p, d)
        xs.append(x)
        ys.append(y)
        t += t_step

    max_abs = max(
        max(map(abs, xs)),
        max(map(abs, ys)),
        1e-9,
    )

    margin = 0.10
    scale = (size * (0.5 - margin)) / max_abs
    cx = cy = size / 2

    imgs = []

    # Draw progressively so the animation grows the curve
    for fi in range(frames):
        img = Image.new("RGBA", (size, size), bg)
        draw = ImageDraw.Draw(img)

        local_t = 0.0
        local_prev = None
        total_steps = (fi + 1) * steps_per_frame

        for _ in range(total_steps):
            x, y = point(local_t, A, f, p, d)

            X = cx + x * scale
            Y = cy + y * scale

            if local_prev is not None:
                draw.line(
                    [local_prev, (X, Y)],
                    fill=fg,
                    width=line_width,
                )

            local_prev = (X, Y)
            local_t += t_step

        imgs.append(img)

    imgs[0].save(
        out_path,
        save_all=True,
        append_images=imgs[1:],
        duration=120,
        loop=0,
        transparency=0,
        disposal=2,
    )

    print(f"Saved: {out_path}")


def save_thumbnail_from_gif(
    gif_path: str,
    out_path: str,
    frame_index: int = 15,
):
    """
    Extract a specific frame from an animated GIF
    and save it as a static PNG.
    """
    with Image.open(gif_path) as im:
        frames = [
            frame.copy().convert("RGBA")
            for frame in ImageSequence.Iterator(im)
        ]

        if not frames:
            raise RuntimeError("GIF appears to have no frames.")

        idx = min(
            max(frame_index, 0),
            len(frames) - 1,
        )

        frames[idx].save(out_path)

        print(
            f"Saved thumbnail (frame {idx}): {out_path}"
        )


def append_archive_json(
    hist_dir: str,
    thumb_filename: str,
):
    """
    Append today's thumbnail to harmHistory/archive.json.
    Keeps newest first and prevents duplicates.
    """
    archive_path = os.path.join(
        hist_dir,
        "archive.json",
    )

    data = []

    if os.path.exists(archive_path):
        try:
            with open(
                archive_path,
                "r",
                encoding="utf-8",
            ) as f:
                loaded = json.load(f)

                if isinstance(loaded, list):
                    data = loaded

        except Exception as e:
            print(
                "Warning: could not read existing "
                f"archive.json, rebuilding from empty list. {e}"
            )

            data = []

    if thumb_filename in data:
        data.remove(thumb_filename)

    data.insert(0, thumb_filename)

    tmp_path = archive_path + ".tmp"

    with open(
        tmp_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data, f, indent=2)

    os.replace(
        tmp_path,
        archive_path,
    )

    print(
        f"Updated archive JSON: {archive_path}"
    )


def get_datestr() -> str:
    """
    Prefer HARM_DATE from environment.
    Fallback: UTC date.
    """
    env_date = os.environ.get("HARM_DATE")

    if env_date and env_date.strip():
        return env_date.strip()

    return datetime.now(
        timezone.utc
    ).strftime("%Y%m%d")


if __name__ == "__main__":
    # get_harm.py lives in /scripts
    script_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Project root is one directory above /scripts
    project_root = os.path.dirname(os.path.dirname(script_dir))

    # Generated website assets live in /public/harmonographs
    output_dir = os.path.join(
        project_root,
        "public",
        "harmonographs",
    )

    hist_dir = os.path.join(
        output_dir,
        "harmHistory",
    )

    os.makedirs(
        hist_dir,
        exist_ok=True,
    )

    out_gif = os.path.join(
        output_dir,
        "harmonograph.gif",
    )

    # 1) Generate the current daily GIF
    render_gif(
        out_path=out_gif
    )

    # 2) Build dated filenames
    datestr = get_datestr()

    archive_gif = os.path.join(
        hist_dir,
        f"{datestr}.gif",
    )

    thumb_png = os.path.join(
        hist_dir,
        f"{datestr}-tbn.png",
    )

    thumb_name = (
        f"{datestr}-tbn.png"
    )

    # 3) Save dated archive GIF
    shutil.copy2(
        out_gif,
        archive_gif,
    )

    print(
        f"Archived GIF: {archive_gif}"
    )

    # 4) Save thumbnail PNG
    save_thumbnail_from_gif(
        out_gif,
        thumb_png,
        frame_index=15,
    )

    # 5) Append thumbnail to archive.json
    append_archive_json(
        hist_dir,
        thumb_name,
    )