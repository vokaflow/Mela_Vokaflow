"use client"

import { useState, useEffect } from "react"
import { Users, Search, Plus, Edit, Lock, BarChart3, Mail } from "lucide-react"
import { usersService } from "../../services/users-service"
import type { User } from "../../types/users"

export function UsuariosList() {
  const [users, setUsers] = useState<User[]>([])
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    const loadData = async () => {
      try {
        const [allUsers, current] = await Promise.all([usersService.getAllUsers(), usersService.getCurrentUser()])
        setUsers(allUsers)
        setCurrentUser(current)
      } catch (error) {
        console.error("Error loading users:", error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const filteredUsers = users.filter(
    (user) =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  if (loading) {
    return (
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-voka-border rounded w-1/4"></div>
          <div className="h-32 bg-voka-border rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con controles */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <h3 className="text-voka-white font-montserrat font-bold text-lg flex items-center">
            <Users className="mr-2 text-voka-blue" />👥 DIRECTORIO DE USUARIOS
          </h3>
          <div className="flex space-x-2">
            <button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat flex items-center">
              <Plus className="w-4 h-4 mr-1" />
              Añadir Usuario
            </button>
            <button className="bg-voka-blue hover:bg-voka-blue/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat flex items-center">
              <Mail className="w-4 h-4 mr-1" />
              Invitar Usuarios
            </button>
          </div>
        </div>
      </div>

      {/* Barra de búsqueda y filtros */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
        <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-voka-gray w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar usuarios..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-voka-dark border border-voka-border rounded-lg pl-10 pr-4 py-2 text-voka-white placeholder-voka-gray focus:outline-none focus:border-voka-blue"
            />
          </div>
          <select className="bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white">
            <option>Todos los usuarios</option>
            <option>Solo activos</option>
            <option>Solo administradores</option>
          </select>
          <select className="bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white">
            <option>Ordenar por: Última actividad</option>
            <option>Ordenar por: Nombre</option>
            <option>Ordenar por: Fecha de registro</option>
          </select>
        </div>
      </div>

      {/* Tabla de usuarios */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-voka-dark">
              <tr>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">AVATAR</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">USUARIO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ROL</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ESTADO</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ÚLTIMA ACTIVIDAD</th>
                <th className="text-left p-4 text-voka-gray font-montserrat text-sm">ACCIONES</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-t border-voka-border hover:bg-voka-dark/50">
                  <td className="p-4">
                    <div className="w-10 h-10 bg-voka-magenta rounded-full flex items-center justify-center text-white font-bold">
                      👤
                    </div>
                  </td>
                  <td className="p-4">
                    <div>
                      <div className="text-voka-white font-montserrat font-bold">{user.username}</div>
                      <div className="text-voka-gray text-sm">{user.email}</div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-1 rounded text-xs font-montserrat ${
                        user.role === "admin" ? "bg-voka-magenta text-white" : "bg-voka-blue text-white"
                      }`}
                    >
                      {user.role === "admin" ? "👑 Admin" : "👤 Usuario"}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          user.status === "online" ? "bg-voka-green animate-pulse" : "bg-voka-gray"
                        }`}
                      ></div>
                      <span className="text-voka-white text-sm">
                        {user.status === "online" ? "🟢 EN LÍNEA" : "⚫ DESCONECTADO"}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div>
                      <div className="text-voka-white text-sm">
                        {user.status === "online" ? "Ahora" : new Date(user.last_activity).toLocaleDateString()}
                      </div>
                      <div className="text-voka-gray text-xs">
                        ({Math.floor((user.session_duration || 0) / 3600)}h{" "}
                        {Math.floor(((user.session_duration || 0) % 3600) / 60)}m)
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex space-x-2">
                      <button className="text-voka-blue hover:text-voka-blue/80" title="Editar">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="text-voka-orange hover:text-voka-orange/80" title="Seguridad">
                        <Lock className="w-4 h-4" />
                      </button>
                      <button className="text-voka-green hover:text-voka-green/80" title="Analytics">
                        <BarChart3 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="p-8 text-center">
            <div className="text-voka-gray mb-4">No se encontraron usuarios</div>
            <div className="space-x-4">
              <button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat">
                📧 Invitar Usuarios
              </button>
              <button className="bg-voka-blue hover:bg-voka-blue/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat">
                📝 Importar Masivo
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
          <h4 className="text-voka-white font-montserrat font-bold mb-2">📊 ESTADÍSTICAS DE USUARIOS</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-voka-gray">Total Usuarios:</span>
              <span className="text-voka-white">{users.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-voka-gray">Activos:</span>
              <span className="text-voka-green">{users.filter((u) => u.status === "online").length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-voka-gray">Nuevos Hoy:</span>
              <span className="text-voka-blue">0</span>
            </div>
          </div>
        </div>

        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
          <h4 className="text-voka-white font-montserrat font-bold mb-2">👑 ROLES</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-voka-gray">Administradores:</span>
              <span className="text-voka-magenta">{users.filter((u) => u.role === "admin").length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-voka-gray">Usuarios Estándar:</span>
              <span className="text-voka-blue">{users.filter((u) => u.role === "user").length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-voka-gray">Suspendidos:</span>
              <span className="text-voka-orange">0</span>
            </div>
          </div>
        </div>

        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
          <h4 className="text-voka-white font-montserrat font-bold mb-2">📈 ACTIVIDAD</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-voka-gray">Total Sesiones:</span>
              <span className="text-voka-white">{currentUser?.stats.total_sessions || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-voka-gray">Duración Promedio:</span>
              <span className="text-voka-green">2.5h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-voka-gray">Pico Concurrente:</span>
              <span className="text-voka-blue">1</span>
            </div>
          </div>
        </div>
      </div>

      {/* Perfil detallado del usuario actual */}
      {currentUser && (
        <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
          <h3 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
            👤 PERFIL DETALLADO: {currentUser.username}
            <button className="ml-auto bg-voka-blue hover:bg-voka-blue/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat">
              Editar Perfil
            </button>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-voka-gray">Usuario:</span>
                  <div className="text-voka-white">{currentUser.username}</div>
                </div>
                <div>
                  <span className="text-voka-gray">Tipo de Cuenta:</span>
                  <div className="text-voka-magenta">Administrador</div>
                </div>
                <div>
                  <span className="text-voka-gray">Email:</span>
                  <div className="text-voka-white">{currentUser.email}</div>
                </div>
                <div>
                  <span className="text-voka-gray">Creado:</span>
                  <div className="text-voka-white">{new Date(currentUser.created_at).toLocaleDateString()}</div>
                </div>
                <div>
                  <span className="text-voka-gray">Contraseña:</span>
                  <div className="text-voka-white">••••••••</div>
                </div>
                <div>
                  <span className="text-voka-gray">Último Login:</span>
                  <div className="text-voka-white">{new Date(currentUser.last_login).toLocaleString()}</div>
                </div>
                <div>
                  <span className="text-voka-gray">País:</span>
                  <div className="text-voka-white">{currentUser.location.country} 🇪🇸</div>
                </div>
                <div>
                  <span className="text-voka-gray">Zona Horaria:</span>
                  <div className="text-voka-white">{currentUser.location.timezone} (UTC+1)</div>
                </div>
                <div>
                  <span className="text-voka-gray">Idioma:</span>
                  <div className="text-voka-white">Español/Inglés</div>
                </div>
                <div>
                  <span className="text-voka-gray">2FA:</span>
                  <div className="text-voka-orange">❌ Deshabilitado</div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-voka-white font-montserrat font-bold mb-4">ESTADÍSTICAS DE USO</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-voka-gray">Sesiones:</span>
                  <div className="text-voka-white">{currentUser.stats.total_sessions}</div>
                </div>
                <div>
                  <span className="text-voka-gray">Traducciones:</span>
                  <div className="text-voka-green">{currentUser.stats.total_translations.toLocaleString()}</div>
                </div>
                <div>
                  <span className="text-voka-gray">Sesión Promedio:</span>
                  <div className="text-voka-blue">2.5h</div>
                </div>
                <div>
                  <span className="text-voka-gray">Llamadas API:</span>
                  <div className="text-voka-magenta">{currentUser.stats.total_api_calls.toLocaleString()}</div>
                </div>
                <div>
                  <span className="text-voka-gray">Interacciones Vicky:</span>
                  <div className="text-voka-orange">234</div>
                </div>
                <div>
                  <span className="text-voka-gray">Archivos:</span>
                  <div className="text-voka-white">1,247</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
