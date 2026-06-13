import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ventaService, { Venta, VentaLinea } from '../services/ventaService'
import clienteService from '../services/clienteService'
import productoService from '../services/productoService'

export default function Ventas() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [lineas, setLineas] = useState<VentaLinea[]>([])
  const [formData, setFormData] = useState<Venta>({
    cliente_id: 0,
    fecha_emision: new Date().toISOString().split('T')[0],
    plazo_dias: 0,
    n_cuotas: 1,
    base_cobranza: 'TOTAL',
  })

  const { data: ventas, isLoading: ventasLoading } = useQuery({
    queryKey: ['ventas'],
    queryFn: () => ventaService.listar(0, 50),
  })

  const { data: clientes } = useQuery({
    queryKey: ['clientes'],
    queryFn: () => clienteService.listar(0, 100),
  })

  const { data: productos } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productoService.listar(0, 100),
  })

  const crearMutation = useMutation({
    mutationFn: (data: Venta) => ventaService.crear({ ...data, venta_lineas: lineas }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ventas'] })
      setShowForm(false)
      setLineas([])
      setFormData({
        cliente_id: 0,
        fecha_emision: new Date().toISOString().split('T')[0],
        plazo_dias: 0,
        n_cuotas: 1,
        base_cobranza: 'TOTAL',
      })
    },
  })

  const handleAgregarLinea = () => {
    setLineas([
      ...lineas,
      {
        producto_id: 0,
        cantidad: 1,
        precio_unitario: 0,
      },
    ])
  }

  const handleQuitarLinea = (idx: number) => {
    setLineas(lineas.filter((_, i) => i !== idx))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (lineas.length === 0) {
      alert('Debe agregar al menos una línea')
      return
    }
    crearMutation.mutate(formData)
  }

  if (ventasLoading) return <div>Cargando...</div>

  const formatCLP = (value: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
    }).format(value)
  }

  // Calcular totales de vista previa
  const neto = lineas.reduce((sum, l) => sum + (l.cantidad * l.precio_unitario || 0), 0)
  const iva = neto * 0.19
  const total = neto + iva

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Ventas</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          {showForm ? 'Cancelar' : 'Nueva Venta'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-6">
          {/* Cabecera */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Cliente</label>
              <select
                value={formData.cliente_id}
                onChange={(e) => setFormData({ ...formData, cliente_id: parseInt(e.target.value) })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              >
                <option value={0}>Seleccionar cliente...</option>
                {clientes?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.razon_social}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Fecha Emisión</label>
              <input
                type="date"
                value={formData.fecha_emision}
                onChange={(e) => setFormData({ ...formData, fecha_emision: e.target.value })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Plazo (días)</label>
              <input
                type="number"
                value={formData.plazo_dias}
                onChange={(e) => setFormData({ ...formData, plazo_dias: parseInt(e.target.value) })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Número de Cuotas</label>
              <input
                type="number"
                value={formData.n_cuotas}
                onChange={(e) => setFormData({ ...formData, n_cuotas: parseInt(e.target.value) })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                min="1"
                required
              />
            </div>
          </div>

          {/* Líneas */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Líneas de Venta</h3>
              <button
                type="button"
                onClick={handleAgregarLinea}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
              >
                + Agregar línea
              </button>
            </div>

            <div className="space-y-4">
              {lineas.map((linea, idx) => (
                <div key={idx} className="grid grid-cols-5 gap-2 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <label className="block text-xs font-medium">Producto</label>
                    <select
                      value={linea.producto_id}
                      onChange={(e) => {
                        const producto = productos?.find((p) => p.id === parseInt(e.target.value))
                        const nuevasLineas = [...lineas]
                        nuevasLineas[idx] = {
                          ...linea,
                          producto_id: parseInt(e.target.value),
                          precio_unitario: producto?.precio_unitario || linea.precio_unitario,
                        }
                        setLineas(nuevasLineas)
                      }}
                      className="mt-1 block w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    >
                      <option value={0}>Seleccionar...</option>
                      {productos?.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.nombre}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium">Cantidad</label>
                    <input
                      type="number"
                      step="0.001"
                      value={linea.cantidad}
                      onChange={(e) => {
                        const nuevasLineas = [...lineas]
                        nuevasLineas[idx].cantidad = parseFloat(e.target.value)
                        setLineas(nuevasLineas)
                      }}
                      className="mt-1 block w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium">Precio Unit.</label>
                    <input
                      type="number"
                      step="0.01"
                      value={linea.precio_unitario}
                      onChange={(e) => {
                        const nuevasLineas = [...lineas]
                        nuevasLineas[idx].precio_unitario = parseFloat(e.target.value)
                        setLineas(nuevasLineas)
                      }}
                      className="mt-1 block w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium">Subtotal</label>
                    <input
                      type="text"
                      value={formatCLP(linea.cantidad * linea.precio_unitario)}
                      disabled
                      className="mt-1 block w-full px-2 py-1 bg-gray-200 rounded text-sm"
                    />
                  </div>

                  <div className="flex items-end">
                    <button
                      type="button"
                      onClick={() => handleQuitarLinea(idx)}
                      className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm"
                    >
                      Quitar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Resumen */}
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <div className="flex justify-between">
              <span>Neto:</span>
              <span className="font-bold">{formatCLP(neto)}</span>
            </div>
            <div className="flex justify-between">
              <span>IVA (19%):</span>
              <span className="font-bold">{formatCLP(iva)}</span>
            </div>
            <div className="flex justify-between text-lg">
              <span>Total:</span>
              <span className="font-bold text-blue-600">{formatCLP(total)}</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={crearMutation.isPending}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
          >
            Crear Venta
          </button>
        </form>
      )}

      {/* Listado de ventas */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Folio</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Cliente</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Fecha</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Total</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Estado</th>
            </tr>
          </thead>
          <tbody>
            {ventas?.map((venta) => (
              <tr key={venta.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3">{venta.folio || venta.id}</td>
                <td className="px-4 py-3">{venta.cliente_id}</td>
                <td className="px-4 py-3">{venta.fecha_emision}</td>
                <td className="px-4 py-3 text-right font-bold">{formatCLP(venta.total || 0)}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    venta.estado === 'VIGENTE' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {venta.estado}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
