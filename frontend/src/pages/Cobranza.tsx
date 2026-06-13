import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import cobranzaService from '../services/cobranzaService'
import clienteService from '../services/clienteService'

export default function Cobranza() {
  const queryClient = useQueryClient()
  const [selectedClienteId, setSelectedClienteId] = useState<number | null>(null)
  const [showPagoForm, setShowPagoForm] = useState(false)
  const [pagoData, setPagoData] = useState({
    venta_id: 0,
    fecha: new Date().toISOString().split('T')[0],
    monto: 0,
    medio: 'transferencia',
  })

  const { data: clientes } = useQuery({
    queryKey: ['clientes'],
    queryFn: () => clienteService.listar(0, 100),
  })

  const { data: estadoCuenta } = useQuery({
    queryKey: ['estado-cuenta', selectedClienteId],
    queryFn: () => (selectedClienteId ? cobranzaService.obtenerEstadoCuenta(selectedClienteId) : null),
    enabled: !!selectedClienteId,
  })

  const registrarPagoMutation = useMutation({
    mutationFn: (data: any) => cobranzaService.registrarPago(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['estado-cuenta'] })
      setShowPagoForm(false)
      setPagoData({
        venta_id: 0,
        fecha: new Date().toISOString().split('T')[0],
        monto: 0,
        medio: 'transferencia',
      })
    },
  })

  const handleRegistrarPago = (e: React.FormEvent) => {
    e.preventDefault()
    registrarPagoMutation.mutate(pagoData)
  }

  const formatCLP = (value: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
    }).format(value)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00')
    return date.toLocaleDateString('es-CL')
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Cobranza</h1>

      {/* Selector de cliente */}
      <div className="bg-white p-6 rounded-lg shadow">
        <label className="block text-sm font-medium text-gray-700 mb-2">Seleccionar Cliente</label>
        <select
          value={selectedClienteId || 0}
          onChange={(e) => setSelectedClienteId(e.target.value ? parseInt(e.target.value) : null)}
          className="block w-full px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value={0}>-- Seleccionar cliente --</option>
          {clientes?.map((c) => (
            <option key={c.id} value={c.id}>
              {c.razon_social} ({c.rut})
            </option>
          ))}
        </select>
      </div>

      {selectedClienteId && estadoCuenta && (
        <>
          {/* Resumen del cliente */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Total Adeudado</h3>
              <p className="text-2xl font-bold text-blue-600 mt-2">
                {formatCLP(estadoCuenta.total_adeudado)}
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Total Mora</h3>
              <p className="text-2xl font-bold text-red-600 mt-2">
                {formatCLP(estadoCuenta.total_mora)}
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Total + Mora</h3>
              <p className="text-2xl font-bold text-orange-600 mt-2">
                {formatCLP(estadoCuenta.total_con_mora)}
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-gray-600 text-sm font-medium">Cuotas Vencidas</h3>
              <p className="text-2xl font-bold text-red-700 mt-2">{estadoCuenta.cuotas_vencidas.length}</p>
            </div>
          </div>

          {/* Botón para registrar pago */}
          <div className="flex">
            <button
              onClick={() => setShowPagoForm(!showPagoForm)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
            >
              {showPagoForm ? 'Cancelar' : 'Registrar Pago'}
            </button>
          </div>

          {/* Formulario de pago */}
          {showPagoForm && (
            <form onSubmit={handleRegistrarPago} className="bg-white p-6 rounded-lg shadow space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Venta</label>
                  <select
                    value={pagoData.venta_id}
                    onChange={(e) => setPagoData({ ...pagoData, venta_id: parseInt(e.target.value) })}
                    className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                    required
                  >
                    <option value={0}>Seleccionar venta...</option>
                    {/* Las ventas estarían disponibles aquí */}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Monto</label>
                  <input
                    type="number"
                    step="0.01"
                    value={pagoData.monto}
                    onChange={(e) => setPagoData({ ...pagoData, monto: parseFloat(e.target.value) })}
                    className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Fecha</label>
                  <input
                    type="date"
                    value={pagoData.fecha}
                    onChange={(e) => setPagoData({ ...pagoData, fecha: e.target.value })}
                    className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Medio</label>
                  <select
                    value={pagoData.medio}
                    onChange={(e) => setPagoData({ ...pagoData, medio: e.target.value })}
                    className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="transferencia">Transferencia</option>
                    <option value="efectivo">Efectivo</option>
                    <option value="cheque">Cheque</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={registrarPagoMutation.isPending}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
              >
                Registrar Pago
              </button>
            </form>
          )}

          {/* Cuotas vencidas */}
          {estadoCuenta.cuotas_vencidas.length > 0 && (
            <div className="bg-white rounded-lg shadow overflow-x-auto">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-bold">Cuotas Vencidas</h2>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-red-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Cuota</th>
                    <th className="px-4 py-3 text-left font-medium">Vencimiento</th>
                    <th className="px-4 py-3 text-right font-medium">Capital</th>
                    <th className="px-4 py-3 text-right font-medium">Mora</th>
                    <th className="px-4 py-3 text-right font-medium">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {estadoCuenta.cuotas_vencidas.map((cuota: any, idx: number) => (
                    <tr key={idx} className="border-b hover:bg-red-50">
                      <td className="px-4 py-3">#{cuota.numero}</td>
                      <td className="px-4 py-3">{formatDate(cuota.fecha_vencimiento)}</td>
                      <td className="px-4 py-3 text-right">{formatCLP(cuota.saldo_capital)}</td>
                      <td className="px-4 py-3 text-right text-red-600 font-semibold">
                        {formatCLP(cuota.mora_acumulada)}
                      </td>
                      <td className="px-4 py-3 text-right font-bold">
                        {formatCLP(cuota.saldo_capital + cuota.mora_acumulada)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Cuotas pendientes */}
          {estadoCuenta.cuotas_pendientes.length > 0 && (
            <div className="bg-white rounded-lg shadow overflow-x-auto">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-bold">Cuotas Pendientes</h2>
              </div>
              <table className="w-full text-sm">
                <thead className="bg-blue-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Cuota</th>
                    <th className="px-4 py-3 text-left font-medium">Vencimiento</th>
                    <th className="px-4 py-3 text-right font-medium">Capital</th>
                    <th className="px-4 py-3 text-right font-medium">Saldo</th>
                  </tr>
                </thead>
                <tbody>
                  {estadoCuenta.cuotas_pendientes.map((cuota: any, idx: number) => (
                    <tr key={idx} className="border-b hover:bg-blue-50">
                      <td className="px-4 py-3">#{cuota.numero}</td>
                      <td className="px-4 py-3">{formatDate(cuota.fecha_vencimiento)}</td>
                      <td className="px-4 py-3 text-right">{formatCLP(cuota.monto_capital)}</td>
                      <td className="px-4 py-3 text-right text-blue-600 font-semibold">
                        {formatCLP(cuota.saldo_capital)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
