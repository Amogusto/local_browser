from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import subprocess

app = Flask(__name__, static_folder="static")

@app.route("/")
def home():
    return "✅ API работает!"

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    url = data.get("url")
    filename = data.get("filename", "clip.mp4")
    start = data.get("start", "00:00:30")
    duration = data.get("duration", "00:00:30")

    original_path = "original.mp4"
    clip_path = os.path.join("static", filename)

    try:
        ydl_opts = {
            'outtmpl': original_path,
            'format': 'best',
            'cookiesfrombrowser': ('chrome',),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        subprocess.run([
            "ffmpeg", "-ss", start, "-t", duration,
            "-i", original_path, "-c", "copy", clip_path
        ], check=True)

        if os.path.exists(original_path):
            os.remove(original_path)

        return jsonify({
            "status": "ok",
            "url": f"{request.host_url}static/{filename}"
        })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
