import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import InventoryPage from './pages/InventoryPage'
import SalesPage from './pages/SalesPage'
import POSPage from './pages/POSPage'
import EmployeesPage from './pages/EmployeesPage'
import ReportsPage from './pages/ReportsPage'
import CompanyPage from './pages/CompanyPage'
import UsersPage from './pages/UsersPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="sales" element={<SalesPage />} />
        <Route path="pos" element={<POSPage />} />
        <Route path="employees" element={<EmployeesPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="company" element={<CompanyPage />} />
        <Route path="users" element={<UsersPage />} />
      </Route>
    </Routes>
  )
}
