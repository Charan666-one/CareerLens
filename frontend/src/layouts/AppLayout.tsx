import { Link, Outlet, useLocation } from "react-router-dom"
import StageTracker from "@/components/pipeline/StageTracker"
import { useBootstrapAuth } from "@/hooks/useBootstrapAuth"
import { useAuthStore } from "@/store/auth"
import { logoutAndReset } from "@/store/session"

const NAV_LINKS = [
  { to: "/", label: "Overview" },
  { to: "/jobs", label: "Jobs" },
  { to: "/roadmap", label: "Roadmap" },
]

export default function AppLayout() {
  useBootstrapAuth()
  const user = useAuthStore((s) => s.user)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-stone text-text font-body">
      <div className="bg-ink text-ink-text">
        <nav className="max-w-[1180px] mx-auto px-8 h-[68px] flex items-center justify-between">
          <div className="flex items-center gap-2.5 font-display text-[1.28rem]">
            <svg viewBox="0 0 26 26" className="w-[26px] h-[26px] flex-none" fill="none">
              <circle cx="13" cy="13" r="12" stroke="var(--brass)" strokeWidth="1.2" />
              <path
                d="M13 5 L15.6 11 L21.5 11.5 L16.8 15.4 L18.3 21.2 L13 17.8 L7.7 21.2 L9.2 15.4 L4.5 11.5 L10.4 11 Z"
                fill="var(--brass)"
              />
            </svg>
            CareerLens
          </div>
          <div className="flex gap-7 text-[0.86rem]">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`pb-1.5 border-b ${
                  location.pathname === link.to
                    ? "text-brass border-brass"
                    : "text-ink-text-dim border-transparent hover:text-ink-text"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-2.5 text-[0.84rem] text-ink-text-dim">
            <span>{user?.name ?? user?.email ?? ""}</span>
            <div className="w-[30px] h-[30px] rounded-full bg-gradient-to-br from-brass to-brass-strong text-[#1a1207] font-display text-[0.8rem] flex items-center justify-center">
              {(user?.name ?? user?.email ?? "?").slice(0, 1).toUpperCase()}
            </div>
            <button onClick={logoutAndReset} className="ml-2 underline underline-offset-2 hover:text-ink-text">
              Log out
            </button>
          </div>
        </nav>
      </div>

      <StageTracker />

      <main className="max-w-[1180px] mx-auto px-8 py-10">
        <Outlet />
      </main>
    </div>
  )
}
