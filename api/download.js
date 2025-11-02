export default async function handler(req, res) {
  try {
    const { url } = req.query;
    if (!url) return res.status(400).json({ error: 'URL tidak ditemukan.' });

    // Gunakan API downloader publik (contoh pakai snapinsta atau ttdownloader)
    const api = await fetch(`https://api.tikmate.app/api/lookup?url=${encodeURIComponent(url)}`);
    const data = await api.json();

    if (!data || !data.video_url) {
      return res.status(500).json({ error: 'Gagal ambil video.' });
    }

    return res.status(200).json({
      video: data.video_url,  // Link langsung video
      thumbnail: data.cover,  // Preview
    });
  } catch (err) {
    res.status(500).json({ error: 'Server error: ' + err.message });
  }
}
