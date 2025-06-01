"use client"

import { useState, useEffect } from "react"
import { Settings, User, Palette, Shield, Save, Eye, EyeOff } from "lucide-react"
import { usersService } from "../../services/users-service"
import { useAuth } from "../../hooks/use-auth"
import type { User as UserType } from "../../types/users"

export function UsuariosProfiles() {
  const { user: authUser } = useAuth()
  const [currentUser, setCurrentUser] = useState<UserType | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    displayName: "",
    phone: "",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
    language: "es",
    timezone: "CET",
    theme: "dark",
    notifications: true,
    emailNotifications: true,
    pushNotifications: true,
    autoRefresh: true,
    showAdvancedMetrics: true,
    enableAnimations: true,
    compactView: false,
    realTimeNotifications: true,
    soundAlerts: true,
    vickyPersonality: "balanced",
    vickyResponseSpeed: "fast",
    vickyMemory: true,
    vickyLearning: true,
    translationDefaultSource: "auto",
    translationDefaultTarget: "en",
    translationQuality: "high",
    translationSaveHistory: true,
  })

  useEffect(() => {
    const loadData = async () => {
      try {
        const user = await usersService.getCurrentUser()
        setCurrentUser(user)
        setFormData({
          ...formData,
          username: user.username,
          email: user.email,
          displayName: user.username.toUpperCase() + " Admin",
          language: user.preferences.language,
          theme: user.preferences.theme,
          notifications: user.preferences.notifications,
        })
      } catch (error) {
        console.error("Error loading user profile:", error)
        setMessage({ type: "error", text: "Error al cargar el perfil de usuario" })
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)

    try {
      // Actualizar perfil básico
      const profileData = {
        username: formData.username,
        email: formData.email,
        preferences: {
          language: formData.language,
          theme: formData.theme,
          notifications: formData.notifications,
        },
      }

      await usersService.updateUserProfile(profileData)

      // Cambiar contraseña si se proporcionó
      if (formData.newPassword && formData.currentPassword) {
        if (formData.newPassword !== formData.confirmPassword) {
          setMessage({ type: "error", text: "Las contraseñas no coinciden" })
          setSaving(false)
          return
        }

        const passwordResult = await usersService.changePassword(formData.currentPassword, formData.newPassword)

        if (!passwordResult.success) {
          setMessage({ type: "error", text: passwordResult.message })
          setSaving(false)
          return
        }
      }

      setMessage({ type: "success", text: "Perfil actualizado correctamente" })

      // Limpiar campos de contraseña
      setFormData({
        ...formData,
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      })
    } catch (error) {
      console.error("Error saving profile:", error)
      setMessage({ type: "error", text: "Error al guardar el perfil" })
    } finally {
      setSaving(false)
    }
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value })
  }

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
      {/* Header */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-voka-white font-montserrat font-bold text-lg flex items-center">
            <Settings className="mr-2 text-voka-magenta" />
            ⚙️ CONFIGURACIÓN DE PERFIL: {currentUser?.username}
          </h3>
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-voka-green hover:bg-voka-green/80 disabled:opacity-50 text-white px-6 py-2 rounded-lg text-sm font-montserrat flex items-center"
          >
            <Save className="w-4 h-4 mr-1" />
            {saving ? "Guardando..." : "💾 Guardar Cambios"}
          </button>
        </div>

        {/* Mensaje de estado */}
        {message && (
          <div
            className={`mt-4 p-3 rounded-lg ${
              message.type === "success"
                ? "bg-voka-green/20 border border-voka-green text-voka-green"
                : "bg-voka-red/20 border border-voka-red text-voka-red"
            }`}
          >
            {message.text}
          </div>
        )}
      </div>

      {/* Información Básica */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h4 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <User className="mr-2 text-voka-blue" />
          INFORMACIÓN BÁSICA
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Nombre de Usuario</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => handleInputChange("username", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              />
            </div>
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Nombre para Mostrar</label>
              <input
                type="text"
                value={formData.displayName}
                onChange={(e) => handleInputChange("displayName", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              />
            </div>
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Teléfono</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange("phone", e.target.value)}
                placeholder="+34 XXX XXX XXX"
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Configuración de Seguridad */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h4 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Shield className="mr-2 text-voka-orange" />
          CONFIGURACIÓN DE SEGURIDAD
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-voka-gray text-sm font-montserrat mb-2">Contraseña Actual</label>
            <div className="relative">
              <input
                type={showCurrentPassword ? "text" : "password"}
                value={formData.currentPassword}
                onChange={(e) => handleInputChange("currentPassword", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 pr-10 text-voka-white focus:outline-none focus:border-voka-blue"
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-voka-gray hover:text-voka-white"
              >
                {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-voka-gray text-sm font-montserrat mb-2">Nueva Contraseña</label>
            <div className="relative">
              <input
                type={showNewPassword ? "text" : "password"}
                value={formData.newPassword}
                onChange={(e) => handleInputChange("newPassword", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 pr-10 text-voka-white focus:outline-none focus:border-voka-blue"
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-voka-gray hover:text-voka-white"
              >
                {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-voka-gray text-sm font-montserrat mb-2">Confirmar Contraseña</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 pr-10 text-voka-white focus:outline-none focus:border-voka-blue"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-voka-gray hover:text-voka-white"
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-voka-dark rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-voka-white font-montserrat font-bold">Autenticación de Dos Factores (2FA)</div>
              <div className="text-voka-gray text-sm">Añade una capa extra de seguridad a tu cuenta</div>
            </div>
            <button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat">
              Habilitar 2FA
            </button>
          </div>
        </div>

        <div className="mt-4 p-4 bg-voka-dark rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-voka-white font-montserrat font-bold">Clave API</div>
              <div className="text-voka-gray text-sm font-mono">sk-vkf-••••••••••••••••••••••••</div>
            </div>
            <button className="bg-voka-blue hover:bg-voka-blue/80 text-white px-4 py-2 rounded-lg text-sm font-montserrat">
              🔄 Regenerar
            </button>
          </div>
        </div>
      </div>

      {/* Preferencias */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h4 className="text-voka-white font-montserrat font-bold text-lg mb-4 flex items-center">
          <Palette className="mr-2 text-voka-green" />
          PREFERENCIAS
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Idioma</label>
              <select
                value={formData.language}
                onChange={(e) => handleInputChange("language", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="es">Español 🇪🇸</option>
                <option value="en">English 🇺🇸</option>
                <option value="fr">Français 🇫🇷</option>
              </select>
            </div>
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Zona Horaria</label>
              <select
                value={formData.timezone}
                onChange={(e) => handleInputChange("timezone", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="CET">CET (UTC+1)</option>
                <option value="UTC">UTC (UTC+0)</option>
                <option value="EST">EST (UTC-5)</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Tema</label>
              <select
                value={formData.theme}
                onChange={(e) => handleInputChange("theme", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="dark">Modo Oscuro</option>
                <option value="light">Modo Claro</option>
                <option value="auto">Automático</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.emailNotifications}
                  onChange={(e) => handleInputChange("emailNotifications", e.target.checked)}
                  className="rounded border-voka-border"
                />
                <span className="text-voka-white text-sm">Notificaciones por Email ☑</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.pushNotifications}
                  onChange={(e) => handleInputChange("pushNotifications", e.target.checked)}
                  className="rounded border-voka-border"
                />
                <span className="text-voka-white text-sm">Notificaciones Push ☑</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Configuración del Dashboard */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h4 className="text-voka-white font-montserrat font-bold text-lg mb-4">🎛️ PREFERENCIAS DEL DASHBOARD</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.autoRefresh}
                onChange={(e) => handleInputChange("autoRefresh", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Auto-actualizar dashboards (30s)</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.showAdvancedMetrics}
                onChange={(e) => handleInputChange("showAdvancedMetrics", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Mostrar métricas avanzadas</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.enableAnimations}
                onChange={(e) => handleInputChange("enableAnimations", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Habilitar animaciones</span>
            </label>
          </div>

          <div className="space-y-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.compactView}
                onChange={(e) => handleInputChange("compactView", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Modo vista compacta</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.realTimeNotifications}
                onChange={(e) => handleInputChange("realTimeNotifications", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Notificaciones en tiempo real</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.soundAlerts}
                onChange={(e) => handleInputChange("soundAlerts", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Alertas sonoras</span>
            </label>
          </div>
        </div>
      </div>

      {/* Configuración de Vicky AI */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h4 className="text-voka-white font-montserrat font-bold text-lg mb-4">🧠 CONFIGURACIÓN DE VICKY AI</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Personalidad</label>
              <select
                value={formData.vickyPersonality}
                onChange={(e) => handleInputChange("vickyPersonality", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="balanced">Equilibrada</option>
                <option value="professional">Profesional</option>
                <option value="friendly">Amigable</option>
                <option value="technical">Técnica</option>
              </select>
            </div>
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Velocidad de Respuesta</label>
              <select
                value={formData.vickyResponseSpeed}
                onChange={(e) => handleInputChange("vickyResponseSpeed", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="fast">Rápida</option>
                <option value="balanced">Equilibrada</option>
                <option value="detailed">Detallada</option>
              </select>
            </div>
          </div>

          <div className="space-y-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.vickyMemory}
                onChange={(e) => handleInputChange("vickyMemory", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Memoria habilitada</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.vickyLearning}
                onChange={(e) => handleInputChange("vickyLearning", e.target.checked)}
                className="rounded border-voka-border"
              />
              <span className="text-voka-white text-sm">☑ Aprendizaje habilitado</span>
            </label>
          </div>
        </div>
      </div>

      {/* Configuración de Traducción */}
      <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
        <h4 className="text-voka-white font-montserrat font-bold text-lg mb-4">🌍 CONFIGURACIÓN DE TRADUCCIÓN</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Idioma Origen por Defecto</label>
              <select
                value={formData.translationDefaultSource}
                onChange={(e) => handleInputChange("translationDefaultSource", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="auto">Auto-detectar</option>
                <option value="es">Español</option>
                <option value="en">Inglés</option>
                <option value="fr">Francés</option>
              </select>
            </div>
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Idioma Destino por Defecto</label>
              <select
                value={formData.translationDefaultTarget}
                onChange={(e) => handleInputChange("translationDefaultTarget", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="en">Inglés</option>
                <option value="es">Español</option>
                <option value="fr">Francés</option>
              </select>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-voka-gray text-sm font-montserrat mb-2">Calidad</label>
              <select
                value={formData.translationQuality}
                onChange={(e) => handleInputChange("translationQuality", e.target.value)}
                className="w-full bg-voka-dark border border-voka-border rounded-lg px-4 py-2 text-voka-white focus:outline-none focus:border-voka-blue"
              >
                <option value="high">Alta</option>
                <option value="balanced">Equilibrada</option>
                <option value="fast">Rápida</option>
              </select>
            </div>
            <div className="pt-6">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.translationSaveHistory}
                  onChange={(e) => handleInputChange("translationSaveHistory", e.target.value)}
                  className="rounded border-voka-border"
                />
                <span className="text-voka-white text-sm">☑ Guardar historial</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
