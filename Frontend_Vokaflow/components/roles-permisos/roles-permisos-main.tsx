"use client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Shield, Key, Settings } from "lucide-react"

export function RolesPermisosMain() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-white font-montserrat">👥 Roles y Permisos</h1>
        <p className="text-xl text-slate-400 font-montserrat">Gestión de roles de usuario y control de permisos</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Usuarios Activos</CardTitle>
            <Users className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">1,247</div>
            <p className="text-xs text-slate-400">+12% desde el mes pasado</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Roles Definidos</CardTitle>
            <Shield className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">8</div>
            <p className="text-xs text-slate-400">Roles configurados</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Permisos Activos</CardTitle>
            <Key className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">156</div>
            <p className="text-xs text-slate-400">Permisos únicos</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Configuraciones</CardTitle>
            <Settings className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">24</div>
            <p className="text-xs text-slate-400">Políticas activas</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-slate-900 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Roles del Sistema</CardTitle>
            <CardDescription className="text-slate-400">Roles predefinidos y sus permisos</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: "Super Admin", users: 2, color: "bg-red-500" },
                { name: "Admin", users: 8, color: "bg-orange-500" },
                { name: "Moderador", users: 24, color: "bg-yellow-500" },
                { name: "Usuario Premium", users: 156, color: "bg-blue-500" },
                { name: "Usuario Estándar", users: 1057, color: "bg-green-500" },
              ].map((role) => (
                <div key={role.name} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${role.color}`}></div>
                    <span className="text-white font-medium">{role.name}</span>
                  </div>
                  <Badge variant="outline" className="text-slate-300">
                    {role.users} usuarios
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Actividad Reciente</CardTitle>
            <CardDescription className="text-slate-400">Cambios recientes en roles y permisos</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { action: "Nuevo rol creado", detail: "Rol 'Traductor' añadido", time: "Hace 2h" },
                { action: "Permisos modificados", detail: "Usuario Premium actualizado", time: "Hace 4h" },
                { action: "Usuario promovido", detail: "juan.perez → Admin", time: "Hace 6h" },
                { action: "Política aplicada", detail: "Restricción API activada", time: "Hace 1d" },
              ].map((activity, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-slate-800 rounded-lg">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">{activity.action}</p>
                    <p className="text-slate-400 text-xs">{activity.detail}</p>
                    <p className="text-slate-500 text-xs mt-1">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
