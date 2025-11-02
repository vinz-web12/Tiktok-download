export default async function handler(req, res) {
  const { url } = req.query;
  if (!url) return res.status(400).json({ error: 'URL tidak valid' });

  try {
    const api = await fetch(`https://www.tikwm.com/api/?url=${encodeURIComponent(url)}`);
    const data = await api.json();

    if (data?.data?.hdplay) {
      res.status(200).json({ hdVideoUrl: data.data.hdplay });
    } else if (data?.data?.play) {
      res.status(200).json({ hdVideoUrl: data.data.play });
    } else {
      res.status(500).json({ error: 'Tidak bisa ambil link video.' });
    }
  } catch (err) {
    res.status(500).json({ error: 'Gagal koneksi server proxy.' });
  }
}
