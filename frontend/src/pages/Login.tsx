import { useState } from "react"
import { useForm } from "react-hook-form"
import { Link, useLocation, useNavigate } from "react-router-dom"
import Button from "@/components/ui/Button"
import { login } from "@/services/authApi"
import { normalizeApiError } from "@/services/errors"
import { useAuthStore } from "@/store/auth"

interface LoginForm {
  email: string
  password: string
}

export default function Login() {
  const { register, handleSubmit, formState } = useForm<LoginForm>()
  const setToken = useAuthStore((s) => s.setToken)
  const navigate = useNavigate()
  const location = useLocation()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const registeredNotice = (location.state as { registered?: boolean } | null)?.registered

  const onSubmit = async (values: LoginForm) => {
    setError(null)
    setSubmitting(true)
    try {
      const { access_token } = await login(values)
      setToken(access_token)
      const from = (location.state as { from?: Location } | null)?.from
      navigate(from ? `${from.pathname}${from.search}` : "/", { replace: true })
    } catch (err) {
      setError(normalizeApiError(err).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bg-stone-raised border border-stone-line rounded p-7">
      <h1 className="font-display text-xl mb-5 text-center">Log in</h1>

      {registeredNotice && (
        <p className="text-good text-sm mb-4 text-center">Account created — log in to continue.</p>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1.5 text-sm">
          Email
          <input
            type="email"
            className="border border-stone-line rounded px-3 py-2 bg-stone"
            {...register("email", { required: true })}
          />
          {formState.errors.email && <span className="text-warn text-xs">Email is required.</span>}
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          Password
          <input
            type="password"
            className="border border-stone-line rounded px-3 py-2 bg-stone"
            {...register("password", { required: true })}
          />
          {formState.errors.password && <span className="text-warn text-xs">Password is required.</span>}
        </label>

        {error && <p className="text-warn text-sm">{error}</p>}

        <Button type="submit" disabled={submitting} className="w-full mt-2">
          {submitting ? "Logging in…" : "Log in"}
        </Button>
      </form>

      <p className="text-center text-sm text-text-dim mt-5">
        No account?{" "}
        <Link to="/register" className="text-brass-strong underline">
          Register
        </Link>
      </p>
    </div>
  )
}
