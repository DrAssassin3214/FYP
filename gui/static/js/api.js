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
    data = ct.includes("application/json") && !attachment ? await res.json() : await res.blob();
  } catch (e) {
    data = { problems: [`Unreadable server response (${e.message})`] };
  }
  return { ok: res.ok, status: res.status, data, headers: res.headers };
}

export const get = (p) => api("GET", p);
export const post = (p, b) => api("POST", p, b);
