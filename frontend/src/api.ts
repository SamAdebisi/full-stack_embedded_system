const API_BASE = import.meta.env.VITE_API_BASE || "";
const tk = () => localStorage.getItem("token") || "";
export async function login(username: string, password: string) {
  const r = await fetch(`${API_BASE}/api/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });
  if (!r.ok) throw new Error("auth");
  const d = await r.json();
  localStorage.setItem("token", d.access_token);
}
export async function getDevices() {
  const r = await fetch(`${API_BASE}/api/devices`, { headers: { Authorization: `Bearer ${tk()}` } });
  if (!r.ok) throw new Error("auth");
  return r.json();
}
export async function getTelemetry(device_id: string, limit = 200) {
  const r = await fetch(`${API_BASE}/api/telemetry?device_id=${encodeURIComponent(device_id)}&limit=${limit}`, { headers: { Authorization: `Bearer ${tk()}` } });
  if (!r.ok) throw new Error("auth");
  return r.json();
}
export function openWs() {
  const base = (API_BASE || window.location.origin).replace(/^http/, "ws");
  return new WebSocket(`${base}/ws?token=${encodeURIComponent(tk())}`);
}
export function logout() { localStorage.removeItem("token"); }
