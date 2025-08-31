import React from 'react'

type Props = { id: string; online: boolean; temp?: number; hum?: number }
export default function DeviceCard({ id, online, temp, hum }: Props) {
  return (
    <div className="rounded-2xl shadow p-4 border">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{id}</h3>
        <span className={`text-sm ${online ? 'text-green-600' : 'text-gray-400'}`}>{online ? 'online' : 'offline'}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 mt-2">
        <div className="text-sm">Temp<div className="text-2xl">{temp?.toFixed(1) ?? '—'}°C</div></div>
        <div className="text-sm">Humidity<div className="text-2xl">{hum?.toFixed(1) ?? '—'}%</div></div>
      </div>
    </div>
  )
}