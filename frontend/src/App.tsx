import { Route, Routes } from "react-router-dom"
import AppLayout from "@/layouts/AppLayout"
import AuthLayout from "@/layouts/AuthLayout"
import Dashboard from "@/pages/Dashboard"
import Jobs from "@/pages/Jobs"
import Login from "@/pages/Login"
import NotFound from "@/pages/NotFound"
import Register from "@/pages/Register"
import Roadmap from "@/pages/Roadmap"
import GuestOnlyRoute from "@/routes/GuestOnlyRoute"
import ProtectedRoute from "@/routes/ProtectedRoute"

export default function App() {
  return (
    <Routes>
      <Route element={<GuestOnlyRoute />}>
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/roadmap" element={<Roadmap />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
