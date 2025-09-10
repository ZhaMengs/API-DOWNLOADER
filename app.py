from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)   # biar frontend di Netlify bisa akses

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL wajib diisi"}), 400

    ydl_opts = {
        'format': 'best',
        'writesubtitles': False,
        'quiet': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []

        # VIDEO
        for f in info['formats']:
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                formats.append({
                    "type": "video",
                    "quality": f.get('format_note') or f"{f.get('height', '0')}p",
                    "url": f['url'],
                    "ext": f['ext'],
                    "size": f.get('filesize') or f.get('filesize_approx') or None
                })

        # AUDIO
        for f in info['formats']:
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                formats.append({
                    "type": "audio",
                    "quality": "MP3",
                    "url": f['url'],
                    "ext": "mp3",
                    "size": f.get('filesize') or f.get('filesize_approx') or None
                })

        # THUMBNAILS
        thumbnails = info.get('thumbnails', [])
        photos = [t for t in thumbnails if t.get('url') and '.jpg' in t['url']]
        for p in photos[:3]:
            formats.append({
                "type": "photo",
                "quality": "original",
                "url": p['url'],
                "ext": "jpg",
                "size": None
            })

        return jsonify({
            "success": True,
            "title": info.get('title'),
            "uploader": info.get('uploader'),
            "thumbnail": info.get('thumbnail'),
            "profilePic": info.get('avatar') or info.get('uploader_avatar') or None,
            "duration": info.get('duration'),
            "platform": info.get('extractor_key', 'unknown').lower(),
            "formats": formats
        })

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"success": False, "error": "Gagal extract. Pastikan URL valid & publik."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)