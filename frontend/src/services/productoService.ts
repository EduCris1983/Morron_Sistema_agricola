import api from '../lib/api'

export interface Producto {
  id?: number
  nombre: string
  formulacion?: string
  unidad: string
  costo_unitario: number
  precio_unitario: number
  activo?: boolean
  creado_en?: string
  actualizado_en?: string
}

const productoService = {
  async listar(skip = 0, limit = 10, activosSolo = true): Promise<Producto[]> {
    const response = await api.get<Producto[]>('/productos', {
      params: { skip, limit, activos_solo: activosSolo },
    })
    return response.data
  },

  async obtener(id: number): Promise<Producto> {
    const response = await api.get<Producto>(`/productos/${id}`)
    return response.data
  },

  async crear(producto: Producto): Promise<Producto> {
    const response = await api.post<Producto>('/productos', producto)
    return response.data
  },

  async actualizar(id: number, producto: Partial<Producto>): Promise<Producto> {
    const response = await api.put<Producto>(`/productos/${id}`, producto)
    return response.data
  },

  async darDeBaja(id: number): Promise<void> {
    await api.delete(`/productos/${id}`)
  },
}

export default productoService
