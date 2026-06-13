import api from '../lib/api'

export interface Cliente {
  id?: number
  razon_social: string
  rut: string
  giro?: string
  email?: string
  telefono?: string
  direccion?: string
  activo?: boolean
  creado_en?: string
  actualizado_en?: string
}

const clienteService = {
  async listar(skip = 0, limit = 10, activosSolo = true): Promise<Cliente[]> {
    const response = await api.get<Cliente[]>('/clientes', {
      params: { skip, limit, activos_solo: activosSolo },
    })
    return response.data
  },

  async obtener(id: number): Promise<Cliente> {
    const response = await api.get<Cliente>(`/clientes/${id}`)
    return response.data
  },

  async crear(cliente: Cliente): Promise<Cliente> {
    const response = await api.post<Cliente>('/clientes', cliente)
    return response.data
  },

  async actualizar(id: number, cliente: Partial<Cliente>): Promise<Cliente> {
    const response = await api.put<Cliente>(`/clientes/${id}`, cliente)
    return response.data
  },

  async darDeBaja(id: number): Promise<void> {
    await api.delete(`/clientes/${id}`)
  },
}

export default clienteService
