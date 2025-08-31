import React, { useState } from 'react'
import { login } from '../api'
export default function Login({ onSuccess }: { onSuccess: () => void }) {
  const [u, setU] = useState('admin')
  const [p, setP] = useState('adminpass')
  const [e, setE] = useState('')
  const submit = async (ev: React.FormEvent) => { ev.preventDefault(); try { await login(u,p); onSuccess() } catch { setE('Login failed') } }
  return (
    <div className="min-h-screen grid place-items-center">
      <form onSubmit={submit} className="border rounded-2xl shadow p-6 w-80 space-y-3">
        <h1 className="text-xl font-semibold">Sign in</h1>
        <input className="w-full border rounded px-2 py-1" value={u} onChange={e=>setU(e.target.value)} placeholder="username" />
        <input className="w-full border rounded px-2 py-1" type="password" value={p} onChange={e=>setP(e.target.value)} placeholder="password" />
        {e && <div className="text-red-600 text-sm">{e}</div>}
        <button className="w-full bg-black text-white rounded py-2" type="submit">Login</button>
      </form>
    </div>
  )
}