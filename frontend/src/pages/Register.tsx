import { useState } from "react"
import { useForm } from "react-hook-form"
import { Link, useNavigate } from "react-router-dom"
import Button from "@/components/ui/Button"
import { register as registerUser } from "@/services/authApi"
import { normalizeApiError } from "@/services/errors"

interface RegisterForm {
  name: string
  email: string
  password: string
}

export default function Register() {
  const { register, handleSubmit, formState } = useForm<RegisterForm>()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (values: RegisterForm) => {
    setError(null)
    setSubmitting(true)
    try {
      await registerUser(values)
      // register doesn't return a token - sign in separately.
      navigate("/login", { state: { registered: true }, replace: true })
    } catch (err) {
      setError(normalizeApiError(err).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bg-stone-raised border border-stone-line rounded p-7">
      <h1 className="font-display text-xl mb-5 text-center">Create an account</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1.5 text-sm">
          Name
          <input
            type="text"
            className="border border-stone-line rounded px-3 py-2 bg-stone"
            {...register("name", { required: true })}
          />
          {formState.errors.name && <span className="text-warn text-xs">Name is required.</span>}
        </label>
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
            {...register("password", { required: true, minLength: 8 })}
          />
          {formState.errors.password && (
            <span className="text-warn text-xs">Password must be at least 8 characters.</span>
          )}
        </label>

        {error && <p className="text-warn text-sm">{error}</p>}

        <Button type="submit" disabled={submitting} className="w-full mt-2">
          {submitting ? "Creating account…" : "Register"}
        </Button>
      </form>

      <p className="text-center text-sm text-text-dim mt-5">
        Already have an account?{" "}
        <Link to="/login" className="text-brass-strong underline">
          Log in
        </Link>
      </p>
    </div>
  )
}
