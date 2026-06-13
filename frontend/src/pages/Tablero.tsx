import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import tableroService from '../services/tableroService'

export default function Tablero() {
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['kpis'],
    queryFn: () => tableroService.obtenerKPIs(30),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-600">Cargando KPIs...</p>
      </div>
    )
  }

  const formatCLP = (value: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
    }).format(value)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Tablero</h1>

      {/* KPIs principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">Margen Acumulado</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">
            {formatCLP(kpis?.margen_acumulado || 0)}
          </p>
          <p className="text-gray-500 text-xs mt-1">Últimos 30 días</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">CxC Vigente</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">
            {formatCLP(kpis?.cxc_vigente || 0)}
          </p>
          <p className="text-gray-500 text-xs mt-1">Total adeudado</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">Cuotas Vencidas</h3>
          <p className="text-2xl font-bold text-red-600 mt-2">{kpis?.cuotas_vencidas?.cantidad || 0}</p>
          <p className="text-gray-500 text-xs mt-1">
            Mora: {formatCLP(kpis?.cuotas_vencidas?.mora_total || 0)}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-600 text-sm font-medium">Ingresos Período</h3>
          <p className="text-2xl font-bold text-purple-600 mt-2">
            {formatCLP(kpis?.ingresos_periodo || 0)}
          </p>
          <p className="text-gray-500 text-xs mt-1">Pagos realizados</p>
        </div>
      </div>

      {/* Top 5 deudores */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Top 5 Deudores</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Cliente</th>
                <th className="px-4 py-2 text-left font-medium text-gray-700">RUT</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Deuda</th>
              </tr>
            </thead>
            <tbody>
              {kpis?.top_5_deudores?.map((deudor: any, idx: number) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-3">{deudor.razon_social}</td>
                  <td className="px-4 py-3 text-gray-600">{deudor.rut}</td>
                  <td className="px-4 py-3 text-right font-semibold text-red-600">
                    {formatCLP(deudor.deuda_total)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
