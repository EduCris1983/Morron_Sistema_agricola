import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import authService from '../services/authService'
import Layout from './Layout'

interface ProtectedRouteProps {
  children: ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!authService.estaAutenticado()) {
    return <Navigate to="/login" replace />
  }

  return <Layout>{children}</Layout>
}
