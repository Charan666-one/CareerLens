import { Outlet } from "react-router-dom"

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-stone text-text font-body flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2.5 font-display text-2xl justify-center mb-8">
          <svg viewBox="0 0 26 26" className="w-7 h-7 flex-none" fill="none">
            <circle cx="13" cy="13" r="12" stroke="var(--brass)" strokeWidth="1.2" />
            <path
              d="M13 5 L15.6 11 L21.5 11.5 L16.8 15.4 L18.3 21.2 L13 17.8 L7.7 21.2 L9.2 15.4 L4.5 11.5 L10.4 11 Z"
              fill="var(--brass)"
            />
          </svg>
          CareerLens
        </div>
        <Outlet />
      </div>
    </div>
  )
}
