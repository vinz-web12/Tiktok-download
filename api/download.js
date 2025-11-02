// /api/download.js  (for Vercel serverless functions - Node 18+)
// Place this file in your project under /api/download.js and deploy to Vercel.

export default async function handler(req, res) {
  const url = req.query.url;
  if (!url) return res.status(400).json({ error: 'No url' });

  try {
    // fetch the TikTok page HTML (server-side)
    const pageResp = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
      },
    });
    if (!pageResp.ok) throw new Error('Failed to fetch page');

    const html = await pageResp.text();

    // Try several regex patterns to extract video urls from the page JSON blobs
    // We'll try: "playAddr":"...","playAddrH265":"...", and also parse window['SIGI_STATE']
    function unescapeStr(s){
      if(!s) return s;
      return s.replace(/\\u0026/g, "&").replace(/\\\//g, "/").replace(/\\\\/g, "\\");
    }

    // pattern 1: playAddrH265
    let match = html.match(/"playAddrH264":"(.*?)"/) || html.match(/"playAddrH265":"(.*?)"/) || html.match(/"playAddr":"(.*?)"/);
    let videoUrl = match ? unescapeStr(decodeURIComponent(match[1])) : null;

    // pattern 2: look inside HTML for "dash" or "progressive" manifest (some pages include JSON)
    if(!videoUrl){
      const sigMatch = html.match(/<script id="SIGI_STATE" type="application\/json">(.+?)<\/script>/s);
      if(sigMatch){
        try{
          const state = JSON.parse(sigMatch[1]);
          // Try to find video URL in state
          // Navigate common paths
          const videoData = state?.ItemModule && Object.values(state.ItemModule)[0];
          if(videoData){
            // Try no watermark highest quality
            videoUrl = videoData?.video?.downloadAddr || videoData?.video?.playAddr || videoData?.video?.playAddrH265 || videoData?.video?.playAddrH264 || null;
          }
        }catch(e){}
      }
    }

    // pattern 3: fallback - search for "vid:" or other direct urls in HTML
    if(!videoUrl){
      const anyUrlMatch = html.match(/(https:\\/\\/v[0-9]+\.akamaized\.net\/[^"\\\s]+)/) || html.match(/(https:\/\/api.amemvod.com\/[^"'\s]+)/);
      if(anyUrlMatch){
        videoUrl = unescapeStr(anyUrlMatch[1]).replace(/\\\//g, "/");
      }
    }

    // Optional: try remove watermark param or change to 'source' domain
    if(videoUrl){
      // Some extracted URLs are encoded, attempt decode
      try { videoUrl = decodeURIComponent(videoUrl); } catch(e){}
      videoUrl = videoUrl.replace(/watermark=1/g, 'watermark=0'); // best-effort to prefer no-watermark if possible
    }

    // Try to find cover image (for photo preview)
    let coverMatch = html.match(/"cover":"(.*?)"/) || html.match(/"originCover":"(.*?)"/);
    let coverUrl = coverMatch ? unescapeStr(decodeURIComponent(coverMatch[1])) : null;

    // If still nothing, return what we have (error)
    if(!videoUrl && !coverUrl){
      // Also try hitting a public API (tikwm) as fallback
      try{
        const apiResp = await fetch(`https://www.tikwm.com/api/?url=${encodeURIComponent(url)}`, { headers: { 'User-Agent':'Mozilla/5.0' }});
        if(apiResp.ok){
          const j = await apiResp.json();
          const d = j?.data;
          if(d){
            videoUrl = d.hdplay || d.play || d.wmplay || null;
            coverUrl = d?.cover || d?.video_cover || coverUrl;
          }
        }
      }catch(e){}
    }

    // Prepare response
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=300'); // lightweight cache
    return res.status(200).json({
      videoUrl: videoUrl || null,
      imageUrl: coverUrl || null,
      audioUrl: null, // optional: could also extract audio stream if desired
      source: videoUrl ? 'tiktok-direct' : 'none'
    });

  } catch (err) {
    console.error('proxy error', err);
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(500).json({ error: 'server failed', detail: String(err && err.message ? err.message : err) });
  }
}
