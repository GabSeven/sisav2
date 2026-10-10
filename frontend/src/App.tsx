import { useEffect, useState } from 'react'

type ApiStatus = 'indo' | 'ok' | 'erro'

export default function App() {
  const [status, setStatus] = useState<ApiStatus>('indo')

  useEffect(() => {
    fetch('/health')
      .then((r) => setStatus(r.ok ? 'ok' : 'erro'))
      .catch(() => setStatus('erro'))
  }, [])

  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 text-neutral-900">
      <main className="text-center">
        <h1 className="text-2xl font-semibold">SISAV 2</h1>
        <p className="mt-2 text-sm text-neutral-500">
          API: <span className={status === 'ok' ? 'text-green-600' : 'text-red-600'}>{status}</span>
        </p>
      </main>
    </div>
  )
}