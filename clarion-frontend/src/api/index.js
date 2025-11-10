const API_BASE = "http://localhost:5000"; // change later if deployed

export async function checkPostByUrl(url) {
  const res = await fetch(`${API_BASE}/check_url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });
  return res.json();
}


export async function getTopPosts(source = "all") {
  const res = await fetch(`${API_BASE}/top-posts?source=${source}`);
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${API_BASE}/history`);
  return res.json();
}
