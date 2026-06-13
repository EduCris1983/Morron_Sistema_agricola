import api from '../lib/api'

export interface Pago {
  venta_id: number
  fecha: string
  monto: number
  medio?: string
  glosa?: string
}

export interface EstadoCuenta {
  cliente: {
    id: number
    razon_social: string
    rut: string
  }
  cuotas_pendientes: any[]
  cuotas_vencidas: any[]
  total_adeudado: number
  total_mora: number
  total_con_mora: number
}

const cobranzaService = {
  async listarCuotasVencidas(cliente_id?: number): Promise<any[]> {
    const response = await api.get('/cobranza/cuotas-vencidas', {
      params: { cliente_id },
    })
    return response.data
  },

  async registrarPago(pago: Pago): Promise<any> {
    const response = await api.post('/cobranza/pagos', pago)
    return response.data
  },

  async prorrogarCuota(cuota_id: number, nueva_fecha: string): Promise<any> {
    const response = await api.post(`/cobranza/cuotas/${cuota_id}/prorroga`, {
      nueva_fecha_vencimiento: nueva_fecha,
      recalcular_mora: false,
    })
    return response.data
  },

  async obtenerEstadoCuenta(cliente_id: number): Promise<EstadoCuenta> {
    const response = await api.get<EstadoCuenta>(`/cobranza/clientes/${cliente_id}/estado-cuenta`)
    return response.data
  },
}

export default cobranzaService
