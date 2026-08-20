import Navbar from './Navbar'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="pt-24 pb-16 px-4 max-w-7xl mx-auto">
        {children}
      </main>
      <footer className="border-t border-white/5 py-8 px-4 text-center">
        <p className="text-xs text-white/25 leading-relaxed">
          BloodSetu &nbsp;·&nbsp; Parul University &nbsp;·&nbsp; BCA (Hons) Mini Project-II
          <br />
          <span className="text-white/15">bloodsetu.help@gmail.com</span>
        </p>
      </footer>
    </div>
  )
}

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
      <div>
        <h1 className="sec-header">{title}</h1>
        {subtitle && <p className="text-white/50 text-sm mt-1.5 max-w-xl">{subtitle}</p>}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  )
}
