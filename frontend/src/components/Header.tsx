interface HeaderProps {
  titulo: string
  subtitulo: string
  busca?: string
  onBuscaChange?: (valor: string) => void
}

export function Header({ titulo, subtitulo, busca, onBuscaChange }: HeaderProps) {
  return (
    <header className="flex items-center justify-between bg-white border-b border-slate-200 px-6 py-4">
      <div>
        <h1 className="font-heading text-2xl font-semibold text-slate-900 tracking-tight">{titulo}</h1>
        <p className="text-sm text-slate-500 mt-0.5">{subtitulo}</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative">
          <input
            type="text"
            value={busca}
            onChange={(e) => onBuscaChange?.(e.target.value)}
            placeholder="Buscar..."
            className="w-56 bg-slate-100 text-sm px-4 py-2 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        <button
          type="button"
          className="relative cursor-pointer p-2 rounded-full hover:bg-slate-100 transition-colors"
          aria-label="Notificações"
        >
          <span className="w-2 h-2 bg-red-500 rounded-full absolute top-1.5 right-1.5 border border-white"></span>
          <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
        </button>
      </div>
    </header>
  )
}