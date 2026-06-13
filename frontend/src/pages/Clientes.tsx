import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import clienteService, { Cliente } from '../services/clienteService'

export default function Clientes() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<Cliente>({
    razon_social: '',
    rut: '',
  })

  const { data: clientes, isLoading } = useQuery({
    queryKey: ['clientes'],
    queryFn: () => clienteService.listar(0, 50),
  })

  const crearMutation = useMutation({
    mutationFn: (data: Cliente) => clienteService.crear(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      setShowForm(false)
      setFormData({ razon_social: '', rut: '' })
    },
  })

  const actualizarMutation = useMutation({
    mutationFn: (data: Cliente) =>
      editingId ? clienteService.actualizar(editingId, data) : Promise.reject(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      setEditingId(null)
      setFormData({ razon_social: '', rut: '' })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingId) {
      actualizarMutation.mutate(formData)
    } else {
      crearMutation.mutate(formData)
    }
  }

  if (isLoading) return <div>Cargando...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Clientes</h1>
        <button
          onClick={() => {
            setShowForm(!showForm)
            setEditingId(null)
            setFormData({ razon_social: '', rut: '' })
          }}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          {showForm ? 'Cancelar' : 'Nuevo Cliente'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Razón Social</label>
            <input
              type="text"
              value={formData.razon_social}
              onChange={(e) => setFormData({ ...formData, razon_social: e.target.value })}
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">RUT</label>
            <input
              type="text"
              value={formData.rut}
              onChange={(e) => setFormData({ ...formData, rut: e.target.value })}
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Giro</label>
            <input
              type="text"
              value={formData.giro || ''}
              onChange={(e) => setFormData({ ...formData, giro: e.target.value })}
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Teléfono</label>
              <input
                type="tel"
                value={formData.telefono || ''}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={crearMutation.isPending || actualizarMutation.isPending}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
          >
            {editingId ? 'Actualizar' : 'Guardar'}
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Razón Social</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">RUT</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Email</th>
              <th className="px-4 py-3 text-left font-medium text-gray-700">Teléfono</th>
              <th className="px-4 py-3 text-right font-medium text-gray-700">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {clientes?.map((cliente) => (
              <tr key={cliente.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3">{cliente.razon_social}</td>
                <td className="px-4 py-3 text-gray-600">{cliente.rut}</td>
                <td className="px-4 py-3 text-gray-600">{cliente.email}</td>
                <td className="px-4 py-3 text-gray-600">{cliente.telefono}</td>
                <td className="px-4 py-3 text-right">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">Editar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
