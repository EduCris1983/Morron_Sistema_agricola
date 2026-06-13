import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import productoService, { Producto } from '../services/productoService'

export default function Productos() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<Producto>({
    nombre: '',
    unidad: 'KG',
    costo_unitario: 0,
    precio_unitario: 0,
  })

  const { data: productos, isLoading } = useQuery({
    queryKey: ['productos'],
    queryFn: () => productoService.listar(0, 50),
  })

  const crearMutation = useMutation({
    mutationFn: (data: Producto) => productoService.crear(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productos'] })
      setShowForm(false)
      setFormData({ nombre: '', unidad: 'KG', costo_unitario: 0, precio_unitario: 0 })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    crearMutation.mutate(formData)
  }

  if (isLoading) return <div>Cargando...</div>

  const formatCLP = (value: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
    }).format(value)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Productos</h1>
        <button
          onClick={() => {
            setShowForm(!showForm)
            setFormData({ nombre: '', unidad: 'KG', costo_unitario: 0, precio_unitario: 0 })
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          {showForm ? 'Cancelar' : 'Nuevo Producto'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nombre</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Formulación</label>
            <input
              type="text"
              value={formData.formulacion || ''}
              onChange={(e) => setFormData({ ...formData, formulacion: e.target.value })}
              placeholder="ej: 8-25-15-0,1B"
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Unidad</label>
              <select
                value={formData.unidad}
                onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="KG">Kilogramos</option>
                <option value="LTS">Litros</option>
                <option value="TON">Toneladas</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Costo Unitario</label>
              <input
                type="number"
                step="0.01"
                value={formData.costo_unitario}
                onChange={(e) => setFormData({ ...formData, costo_unitario: parseFloat(e.target.value) })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Precio Unitario</label>
              <input
                type="number"
                step="0.01"
                value={formData.precio_unitario}
                onChange={(e) => setFormData({ ...formData, precio_unitario: parseFloat(e.target.value) })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={crearMutation.isPending}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
          >
            Guardar
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Nombre</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Formulación</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Unidad</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Costo</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Precio</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Margen</th>
            </tr>
          </thead>
          <tbody>
            {productos?.map((producto) => {
              const margen = (producto.precio_unitario || 0) - (producto.costo_unitario || 0)
              return (
                <tr key={producto.id} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-3">{producto.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{producto.formulacion || '-'}</td>
                  <td className="px-4 py-3">{producto.unidad}</td>
                  <td className="px-4 py-3 text-right">{formatCLP(producto.costo_unitario || 0)}</td>
                  <td className="px-4 py-3 text-right">{formatCLP(producto.precio_unitario || 0)}</td>
                  <td className="px-4 py-3 text-right font-semibold text-green-600">{formatCLP(margen)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
