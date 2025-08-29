import React, { useEffect, useMemo, useState } from 'react'
import { getDevices, getTelemetry, openWs } from './api'
import DeviceCard from './components/DeviceCard'
import TelemetryChart from './components/TelemetryChart'
import Login from './components/Login'
type Device = { device_id: string; online: boolean }
type Telemetry = { id: number; device_id: string; ts: number; temp_c?: number; hum_pct?: number }
type LiveIndex = Record<string, { temp?: number; hum?: number }>
type WsMsg = { type: 'telemetry' | 'status'; data: any }
export default function App() {
  const [devices, setDevices] = useState<Device[]>([])
  const [selected, setSelected] = useState<string>('env-esp32-01')
  const [series, setSeries] = useState<Telemetry[]>([])
  const [live, setLive] = useState<LiveIndex>({})
  const [authed, setAuthed] = useState<boolean>(() => !!localStorage.getItem('token'))
  useEffect(() => { if (authed) getDevices().then(setDevices).catch(() => setAuthed(false)) }, [authed])
  useEffect(() => { if (authed && selected) getTelemetry(selected, 200).then(setSeries).catch(() => setAuthed(false)) }, [authed, selected])
  useEffect(() => {
    if (!authed) return
    const ws = openWs()
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data) as WsMsg
      if (msg.type === 'telemetry') {
        const t = msg.data
        setLive(m => ({ ...m, [t.device_id]: { temp: t.temp_c, hum: t.hum_pct } }))
        if (t.device_id === selected) setSeries(s => [...s.slice(-199), { id: Date.now(), ...t }])
      }
      if (msg.type === 'status') setDevices(ds => ds.map(d => d.device_id === msg.data.device_id ? { ...d, online: msg.data.online } : d))
    }
    return () => ws.close()
  }, [authed, selected])
  const chosen = useMemo(() => devices.find(d => d.device_id === selected) || devices[0], [devices, selected])
  if (!authed) return <Login onSuccess={() => setAuthed(true)} />
  return (<div className="p-6 max-w-6xl mx-auto space-y-6">
    <header className="flex items-center justify-between">
      <h1 className="text-2xl font-bold">IoT Dashboard</h1>
      <select className="border rounded px-2 py-1" value={selected} onChange={e => setSelected(e.target.value)}>
        {devices.map(d => <option key={d.device_id} value={d.device_id}>{d.device_id}</option>)}
      </select>
    </header>
    <div className="grid md:grid-cols-3 gap-4">
      {devices.map(d => <DeviceCard key={d.device_id} id={d.device_id} online={d.online} temp={live[d.device_id]?.temp} hum={live[d.device_id]?.hum} />)}
    </div>
    <section><h2 className="text-lg font-semibold mb-2">{chosen?.device_id} — Telemetry</h2><TelemetryChart data={series} /></section>
  </div>)
}
