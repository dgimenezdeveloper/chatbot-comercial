import { Button } from '@/components/ui/button/button'
import Link from 'next/link'

export default function Navbar() {
  return (
    <header className="flex items-center justify-between px-8 py-4 bg-white border-b">
      <div className="flex items-center gap-2">
        <div className="w-24 px-4 py-2 rounded-full flex items-center justify-center font-bold">
          PYMIO
        </div>
      </div>
      <nav className="hidden md:flex items-center gap-8">
        <a href="#home" className="text-sm text-gray-700 hover:text-black">Home</a>
        <a href="#propuesta" className="text-sm text-gray-700 hover:text-black">Propuesta</a>
        <a href="#beneficios" className="text-sm text-gray-700 hover:text-black">Beneficios</a>
        <a href="#indicaciones" className="text-sm text-gray-700 hover:text-black">Indicaciones</a>
      </nav>
      <div className="flex items-center gap-6 border-l pl-6">
        <Button variant="ghost" className="text-sm text-gray-500 hover:text-gray-900">
          <Link href="/register">Register</Link>
        </Button>

        <Button>
          <Link href="/login">Log In</Link>
        </Button>
      </div>
    </header>
  )
}