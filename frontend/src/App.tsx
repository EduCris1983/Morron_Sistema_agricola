import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Tablero from './pages/Tablero'
import Clientes from './pages/Clientes'
import ProtectedRoute from './components/ProtectedRoute'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/tablero"
            element={
              <ProtectedRoute>
                <Tablero />
              </ProtectedRoute>
            }
          />

          <Route
            path="/clientes"
            element={
              <ProtectedRoute>
                <Clientes />
              </ProtectedRoute>
            }
          />

          <Route path="/" element={<Navigate to="/tablero" replace />} />
          <Route path="*" element={<Navigate to="/tablero" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
