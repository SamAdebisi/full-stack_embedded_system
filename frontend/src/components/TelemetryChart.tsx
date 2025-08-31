import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

type Row = { ts: number; temp_c?: number; hum_pct?: number }
export default function TelemetryChart({ data }: { data: Row[] }) {
  const fmt = (ts: number) => new Date(ts).toLocaleTimeString()
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ts" tickFormatter={fmt} />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip labelFormatter={(v) => new Date(Number(v)).toLocaleString()} />
          <Line type="monotone" dataKey="temp_c" yAxisId="left" dot={false} />
          <Line type="monotone" dataKey="hum_pct" yAxisId="right" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}