import api from '../lib/api'

export interface VentaLinea {
  producto_id: number
  cantidad: number
  precio_unitario: number
  costo_unitario?: number
}

export interface Venta {
  id?: number
  folio?: string
  cliente_id: number
  fecha_emision: string
  plazo_dias: number
  n_cuotas: number
  base_cobranza: string
  neto?: number
  iva?: number
  total?: number
  estado?: string
  venta_lineas?: VentaLinea[]
  cuotas?: any[]
  creado_en?: string
  actualizado_en?: string
}

const ventaService = {
  async listar(skip = 0, limit = 10, estado?: string, cliente_id?: number): Promise<Venta[]> {
    const response = await api.get<Venta[]>('/ventas', {
      params: { skip, limit, estado, cliente_id },
    })
    return response.data
  },

  async obtener(id: number): Promise<Venta> {
    const response = await api.get<Venta>(`/ventas/${id}`)
    return response.data
  },

  async crear(venta: Venta): Promise<Venta> {
    const response = await api.post<Venta>('/ventas', venta)
    return response.data
  },

  async actualizar(id: number, venta: Partial<Venta>): Promise<Venta> {
    const response = await api.put<Venta>(`/ventas/${id}`, venta)
    return response.data
  },

  async anular(id: number): Promise<any> {
    const response = await api.post(`/ventas/${id}/anular`)
    return response.data
  },
}

export default ventaService
