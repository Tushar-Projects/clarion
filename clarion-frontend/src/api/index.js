const API_BASE = "http://localhost:5000"; // change later if deployed

export async function checkPostByUrl(url, recalculate = false) {
  const res = await fetch(`${API_BASE}/check-post`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, recalculate })
  });
  return res.json();
}


export async function getTopPosts(source = "all", forceRefresh = false) {
  const res = await fetch(`${API_BASE}/top-posts?source=${source}&force_refresh=${forceRefresh}&_t=${Date.now()}`, {
    headers: { "Cache-Control": "no-cache" }
  });
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/history`);
  return res.json();
}
