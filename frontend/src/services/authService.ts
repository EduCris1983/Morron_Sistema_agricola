import api from '../lib/api'

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UsuarioResponse {
  id: number
  email: string
  nombre: string
  activo: boolean
}

const authService = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', credentials)
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('refresh_token', response.data.refresh_token)
    return response.data
  },

  async registro(data: { email: string; nombre: string; password: string }): Promise<UsuarioResponse> {
    const response = await api.post<UsuarioResponse>('/auth/registro', data)
    return response.data
  },

  async obtenerUsuarioActual(): Promise<UsuarioResponse> {
    const response = await api.get<UsuarioResponse>('/auth/me')
    return response.data
  },

  logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  obtenerToken(): string | null {
    return localStorage.getItem('access_token')
  },

  estaAutenticado(): boolean {
    return !!this.obtenerToken()
  },
}

export default authService
