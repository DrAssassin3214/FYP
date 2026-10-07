// Thin fetch wrapper around the local API (gui/api.py). Never contacts any other host.

export async function api(method, path, body) {
  const opt = { method, headers: {} };
  if (body !== undefined) {
    opt.headers["Content-Type"] = "application/json";
    opt.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(path, opt);
  } catch (e) {
    return { ok: false, status: 0, data: { problems: [`Cannot reach the local server (${e.message}). Is "python -m gui" still running?`] } };
  }
  const ct = res.headers.get("content-type") || "";
  const attachment = /attachment/i.test(res.headers.get("content-disposition") || "");
  let data;
  try {
    if (!res.ok && !(ct.includes("application/json") && !attachment)) {
      // a non-JSON error page (e.g. the web server's HTML 500): show its text, never leave the caller waiting on a Blob
      const txt = (await res.text()).replace(/<(script|style)[\s\S]*?<\/\1>/gi, " ").replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim().slice(0, 240);
      data = { problems: [`Server error (HTTP ${res.status})${txt ? `: ${txt}` : ""}`] };
    } else {
      data = ct.includes("application/json") && !attachment ? await res.json() : await res.blob();
      if (!res.ok && data && typeof data === "object" && !Array.isArray(data.problems)) {
        // JSON error without a problems list (e.g. {"error": "..."}): normalise it
        const msg = data.error || data.message || data.detail;
        data = { ...data, problems: [`Server error (HTTP ${res.status})${msg ? `: ${typeof msg === "string" ? msg : JSON.stringify(msg)}` : ""}`] };
      }
    }
  } catch (e) {
    data = { problems: [`Unreadable server response (HTTP ${res.status}): ${e.message}`] };
  }
  return { ok: res.ok, status: res.status, data, headers: res.headers };
}

export const get = (p) => api("GET", p);
export const post = (p, b) => api("POST", p, b);
