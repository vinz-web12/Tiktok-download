const input = document.getElementById("inputUrl");
const fetchBtn = document.getElementById("fetchBtn");
const status = document.getElementById("status");
const previewVideo = document.getElementById("previewVideo");
const previewImg = document.getElementById("previewImg");
const downloadNow = document.getElementById("downloadNow");
const audioBtn = document.getElementById("audioBtn");
const slideContainer = document.getElementById("slideContainer");

function randomName(prefix, ext) {
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let r = "";
  for (let i = 0; i < 8; i++) r += chars[Math.floor(Math.random() * chars.length)];
  return `${prefix}_${r}.${ext}`;
}

async function downloadFile(url, name) {
  try {
    const res = await fetch(url);
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
  } catch (e) {
    alert("Gagal mendownload file!");
  }
}

fetchBtn.onclick = async () => {
  const url = input.value.trim();
  if (!url) return alert("Masukkan link TikTok!");

  status.textContent = "⏳ Mengambil data...";
  previewVideo.style.display = "none";
  previewImg.style.display = "none";
  downloadNow.style.display = "none";
  audioBtn.style.display = "none";
  slideContainer.innerHTML = "";

  try {
    const res = await fetch(`https://www.tikwm.com/api/?url=${encodeURIComponent(url)}`);
    const data = await res.json();

    if (!data || !data.data) throw new Error("Video tidak ditemukan!");

    const d = data.data;

    // Jika konten berupa slide foto
    if (d.images && d.images.length > 0) {
      status.textContent = "📸 Slide foto siap!";
      previewImg.style.display = "block";
      previewImg.src = d.images[0];

      d.images.forEach((img, i) => {
        const item = document.createElement("div");
        item.className = "slideItem";
        item.textContent = `Download Slide ${i + 1}`;
        item.onclick = () => downloadFile(img, randomName("slide", "jpg"));
        slideContainer.appendChild(item);
      });

      if (d.music && d.music.play_url) {
        audioBtn.style.display = "inline-block";
        audioBtn.onclick = () =>
          downloadFile(d.music.play_url, randomName("sound", "mp3"));
      }

      return;
    }

    // Jika konten berupa video
    status.textContent = "🎬 Video siap!";
    previewVideo.style.display = "block";
    previewVideo.src = d.play;
    previewVideo.load();

    downloadNow.style.display = "inline-block";
    downloadNow.onclick = () => downloadFile(d.play, randomName("video", "mp4"));

    if (d.music && d.music.play_url) {
      audioBtn.style.display = "inline-block";
      audioBtn.onclick = () =>
        downloadFile(d.music.play_url, randomName("sound", "mp3"));
    }

  } catch (e) {
    console.error(e);
    status.textContent = "❌ Gagal memuat video HD";
  }
};  try {
    const res = await fetch(`https://www.tikwm.com/api/?url=${encodeURIComponent(url)}`);
    const data = await res.json();

    if (!data || !data.data) throw new Error("Video tidak ditemukan!");

    const d = data.data;

    // Cek tipe konten
    if (d.images && d.images.length > 0) {
      status.textContent = "📸 Slide foto siap!";
      previewImg.style.display = "block";
      previewImg.src = d.images[0];

      d.images.forEach((img, i) => {
        const item = document.createElement("div");
        item.className = "slideItem";
        item.textContent = `Download Slide ${i + 1}`;
        item.onclick = () => downloadFile(img, randomName("slide", "jpg"));
        slideContainer.appendChild(item);
      });

      // Tombol audio kalau ada
      if (d.music && d.music.play_url) {
        audioBtn.style.display = "inline-block";
        audioBtn.onclick = () =>
          downloadFile(d.music.play_url, randomName("sound", "mp3"));
      }

      return;
    }

    // Jika video
    status.textContent = "🎬 Video siap!";
    previewVideo.style.display = "block";
    previewVideo.src = d.play;
    previewVideo.load();

    // Tombol download video
    downloadNow.style.display = "inline-block";
    downloadNow.onclick = () => downloadFile(d.play, randomName("video", "mp4"));

    // Tombol audio
    if (d.music && d.music.play_url) {
      audioBtn.style.display = "inline-block";
      audioBtn.onclick = () =>
        downloadFile(d.music.play_url, randomName("sound", "mp3"));
    }

  } catch (e) {
    console.error(e);
    status.textContent = "❌ Gagal memuat video.";
  }
};
