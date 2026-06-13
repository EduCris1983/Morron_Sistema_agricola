import api from '../lib/api'

export interface KPIs {
  periodo: {
    dias: number
    desde: string
    hasta: string
  }
  margen_acumulado: number
  cxc_vigente: number
  cuotas_vencidas: {
    cantidad: number
    mora_total: number
  }
  ingresos_periodo: number
  top_5_deudores: any[]
  timestamp: string
}

export interface ResumenVentas {
  periodo: {
    desde: string
    hasta: string
  }
  cantidad_ventas: number
  total_neto: number
  total_iva: number
  total_ingresos: number
  promedio_venta: number
}

const tableroService = {
  async obtenerKPIs(periodo_dias = 30): Promise<KPIs> {
    const response = await api.get<KPIs>('/tablero', {
      params: { periodo_dias },
    })
    return response.data
  },

  async obtenerResumenVentas(fecha_inicio?: string, fecha_fin?: string): Promise<ResumenVentas> {
    const response = await api.get<ResumenVentas>('/tablero/resumen-ventas', {
      params: { fecha_inicio, fecha_fin },
    })
    return response.data
  },
}

export default tableroService
