import os
import subprocess
import shutil
import sys

print("=" * 60)
print("Books with Lakshya Video Engine v2.0")
print("=" * 60)

# ------------------------------------------------
# Base Folder
# ------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCENES_DIR = os.path.join(BASE_DIR, "scenes")
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------
# FFmpeg
# ------------------------------------------------

FFMPEG = shutil.which("ffmpeg")

if FFMPEG is None:
    print("\n❌ FFmpeg not found!")
    sys.exit()

print("FFmpeg Found ✔")
print(FFMPEG)

# ------------------------------------------------
# Scan Files
# ------------------------------------------------

scene_files = sorted(
    [
        f for f in os.listdir(SCENES_DIR)
        if f.lower().startswith("scene")
        and f.lower().endswith(".png")
    ],
    key=lambda x: int(x.lower().replace("scene", "").replace(".png", ""))
)

audio_files = sorted(
    [
        f for f in os.listdir(AUDIO_DIR)
        if f.lower().endswith((".m4a", ".mp3", ".wav"))
    ],
    key=lambda x: int(''.join(filter(str.isdigit, x)))
)

starting_video = os.path.join(
    SCENES_DIR,
    "Starting scene.mp4"
)

ending_scene = os.path.join(
    SCENES_DIR,
    "Ending scene.png"
)

print("\nFiles Detected\n")

print("Scenes :", len(scene_files))
print("Audios :", len(audio_files))

# ------------------------------------------------
# Validation
# ------------------------------------------------

if not os.path.exists(starting_video):

    print("\n❌ Starting scene.mp4 not found")
    sys.exit()

if not os.path.exists(ending_scene):

    print("\n❌ Ending scene.png not found")
    sys.exit()

if len(scene_files) != len(audio_files):

    print("\n❌ Scene and Audio count mismatch")
    sys.exit()

print("\n✔ Validation Passed")

# ------------------------------------------------
# Clean Temp Folder
# ------------------------------------------------

print("\nCleaning Temp Folder...")

for file in os.listdir(TEMP_DIR):

    path = os.path.join(TEMP_DIR, file)

    try:
        os.remove(path)
    except:
        pass

print("✔ Temp Folder Ready")

print("\nReady For Rendering...\n")
# ------------------------------------------------
# Render All Scenes
# ------------------------------------------------

print("=" * 60)
print("Rendering All Scenes")
print("=" * 60)

rendered_files = []

for i in range(len(scene_files)):

    scene_path = os.path.join(SCENES_DIR, scene_files[i])
    audio_path = os.path.join(AUDIO_DIR, audio_files[i])

    output_video = os.path.join(
        TEMP_DIR,
        f"scene{i+1}.mp4"
    )

    print(f"\nRendering Scene {i+1}")

    command = [

        FFMPEG,

        "-y",

        "-loop", "1",

        "-i", scene_path,

        "-i", audio_path,

        "-c:v", "libx264",

        "-pix_fmt", "yuv420p",

        "-tune", "stillimage",

        "-c:a", "aac",

        "-shortest",

        "-r", "30",

        "-vf", "scale=1920:1080",

        output_video

    ]

    result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)
print(result.stderr)

if result.returncode != 0:
    print("Merge Failed")
    sys.exit()
    rendered_files.append(output_video)

    print(f"✔ Scene {i+1} Complete")

print("\n===================================")
print("✔ All Scenes Rendered Successfully")
print("===================================")
# ------------------------------------------------
# Render Starting Video
# ------------------------------------------------

print("\n" + "=" * 60)
print("Preparing Starting Video")
print("=" * 60)

starting_output = os.path.join(TEMP_DIR, "000_start.mp4")

shutil.copy2(starting_video, starting_output)

print("✔ Starting Video Ready")

# ------------------------------------------------
# Render Ending Scene
# ------------------------------------------------

print("\n" + "=" * 60)
print("Rendering Ending Scene")
print("=" * 60)

ending_output = os.path.join(TEMP_DIR, "999_end.mp4")

command = [

    FFMPEG,

    "-y",

    "-loop", "1",

    "-i", ending_scene,

    "-f", "lavfi",

    "-i", "anullsrc=r=44100:cl=stereo",

    "-t", "10",

    "-c:v", "libx264",

    "-pix_fmt", "yuv420p",

    "-tune", "stillimage",

    "-c:a", "aac",

    "-vf", "scale=1920:1080",

    "-r", "30",

    ending_output

]

result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)
print(result.stderr)

if result.returncode != 0:
    print("Merge Failed")
    sys.exit()

print("✔ Ending Scene Ready")

print("\n===================================")
print("Starting + Ending Ready")
print("===================================")
# ------------------------------------------------
# Create Merge List
# ------------------------------------------------

print("\n" + "=" * 60)
print("Creating Merge List")
print("=" * 60)

merge_file = os.path.join(TEMP_DIR, "merge.txt")
merge_order = []

# Starting Video
merge_order.append(starting_output)

# Scene Videos
for i in range(1, len(scene_files) + 1):

    merge_order.append(
        os.path.join(TEMP_DIR, f"scene{i}.mp4")
    )

# Ending Video
merge_order.append(ending_output)

with open(merge_file, "w", encoding="utf-8") as f:

    for video in merge_order:

        video = video.replace("\\", "/")

        f.write(f"file '{video}'\n")

print("✔ Merge List Ready")

# ------------------------------------------------
# Merge Final Video
# ------------------------------------------------

print("\n" + "=" * 60)
print("Creating Final Video")
print("=" * 60)

final_video = os.path.join(
    OUTPUT_DIR,
    "Books_with_Lakshya.mp4"
)

command = [
    FFMPEG,
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", merge_file,
    "-c", "copy",
    final_video
]


result = subprocess.run(command, capture_output=True, text=True)

print(result.stdout)
print(result.stderr)

if result.returncode != 0:
    print("Merge Failed")
    sys.exit()

print("\n" + "=" * 60)
print("🎉 VIDEO CREATED SUCCESSFULLY!")
print("=" * 60)

print("\nSaved To:")

print(final_video)