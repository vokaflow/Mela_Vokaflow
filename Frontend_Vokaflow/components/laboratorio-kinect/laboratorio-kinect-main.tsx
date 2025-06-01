"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Activity, Camera, Database, Eye, Gamepad2, Hand, Monitor, Play, Settings, Users, Zap } from "lucide-react"

const tabs = [
  { id: "deteccion", label: "🎯 Detección", icon: Eye },
  { id: "tracking", label: "📍 Tracking", icon: Activity },
  { id: "gestos", label: "✋ Gestos", icon: Hand },
  { id: "calibracion", label: "⚙️ Calibración", icon: Settings },
  { id: "analytics", label: "📊 Analytics", icon: Database },
  { id: "experimentos", label: "🧪 Experimentos", icon: Gamepad2 },
]

export function LaboratorioKinectMain() {
  const [activeTab, setActiveTab] = useState("deteccion")
  const currentTab = tabs.find((tab) => tab.id === activeTab)

  return (
    <div className="min-h-screen bg-[#18181C] p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <Camera className="w-6 h-6 text-blue-400" />
            </div>
            <div className="absolute inset-0 rounded-lg bg-blue-500/20 animate-pulse"></div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">🧬 Laboratorio Kinect</h1>
            <p className="text-gray-400">Centro de Investigación y Desarrollo de Visión Computacional</p>
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex items-center gap-6 p-4 bg-[#19192A] rounded-lg border border-[#26263A]">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-white">Kinect: Conectado</span>
          </div>
          <div className="flex items-center gap-2">
            <Monitor className="w-4 h-4 text-blue-400" />
            <span className="text-gray-400">Resolución: 1920x1080</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-gray-400">FPS: 30</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-pink-400" />
            <span className="text-gray-400">Personas Detectadas: 2</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {tabs.map((tab) => {
          const IconComponent = tab.icon
          return (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? "default" : "ghost"}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all duration-200 ${
                activeTab === tab.id
                  ? "bg-pink-600 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`}
            >
              <IconComponent className="w-4 h-4" />
              {tab.label}
            </Button>
          )
        })}
      </div>

      {/* Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2">
          <Card className="bg-[#19192A] border-[#26263A]">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                {currentTab && <currentTab.icon className="w-5 h-5 text-pink-400" />}
                {currentTab?.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activeTab === "deteccion" && (
                <div className="space-y-6">
                  {/* Camera Feed Simulation */}
                  <div className="aspect-video bg-[#18181C] rounded-lg border border-[#26263A] relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-pink-500/10"></div>
                    <div className="absolute top-4 left-4 flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <span className="text-white text-sm font-mono">LIVE FEED</span>
                    </div>

                    {/* Simulated Detection Boxes */}
                    <div className="absolute top-20 left-16 w-32 h-48 border-2 border-green-400 rounded-lg">
                      <div className="absolute -top-6 left-0 bg-green-400 px-2 py-1 rounded text-xs text-black font-bold">
                        Persona 1 (95%)
                      </div>
                    </div>
                    <div className="absolute top-32 right-20 w-28 h-44 border-2 border-blue-400 rounded-lg">
                      <div className="absolute -top-6 left-0 bg-blue-400 px-2 py-1 rounded text-xs text-black font-bold">
                        Persona 2 (87%)
                      </div>
                    </div>

                    <div className="absolute bottom-4 left-4 text-gray-400 text-sm font-mono">
                      Frame: 1247 | Latencia: 33ms | Objetos: 2
                    </div>
                  </div>

                  {/* Detection Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-[#18181C] p-4 rounded-lg border border-[#26263A]">
                      <div className="text-2xl font-bold text-green-400">95%</div>
                      <div className="text-sm text-gray-400">Precisión</div>
                    </div>
                    <div className="bg-[#18181C] p-4 rounded-lg border border-[#26263A]">
                      <div className="text-2xl font-bold text-blue-400">33ms</div>
                      <div className="text-sm text-gray-400">Latencia</div>
                    </div>
                    <div className="bg-[#18181C] p-4 rounded-lg border border-[#26263A]">
                      <div className="text-2xl font-bold text-pink-400">2</div>
                      <div className="text-sm text-gray-400">Personas</div>
                    </div>
                    <div className="bg-[#18181C] p-4 rounded-lg border border-[#26263A]">
                      <div className="text-2xl font-bold text-yellow-400">30</div>
                      <div className="text-sm text-gray-400">FPS</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab !== "deteccion" && (
                <div className="space-y-6">
                  <div className="text-center py-12">
                    {currentTab && <currentTab.icon className="w-16 h-16 text-blue-400 mx-auto mb-4" />}
                    <h3 className="text-xl font-bold text-white mb-2">{currentTab?.label}</h3>
                    <p className="text-gray-400">Funcionalidad en desarrollo</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* System Status */}
          <Card className="bg-[#19192A] border-[#26263A]">
            <CardHeader>
              <CardTitle className="text-white text-lg">Estado del Sistema</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Kinect Sensor</span>
                <Badge className="bg-green-400/20 text-green-400 border-green-400/30">Conectado</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Cámara RGB</span>
                <Badge className="bg-green-400/20 text-green-400 border-green-400/30">Activa</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Sensor Profundidad</span>
                <Badge className="bg-green-400/20 text-green-400 border-green-400/30">Activo</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Micrófono Array</span>
                <Badge className="bg-yellow-400/20 text-yellow-400 border-yellow-400/30">Standby</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-[#19192A] border-[#26263A]">
            <CardHeader>
              <CardTitle className="text-white text-lg">Acciones Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full bg-pink-600 hover:bg-pink-700 text-white">
                <Play className="w-4 h-4 mr-2" />
                Iniciar Detección
              </Button>
              <Button variant="outline" className="w-full border-[#26263A] text-gray-400 hover:text-white">
                <Settings className="w-4 h-4 mr-2" />
                Calibrar Sensor
              </Button>
              <Button variant="outline" className="w-full border-[#26263A] text-gray-400 hover:text-white">
                <Camera className="w-4 h-4 mr-2" />
                Capturar Frame
              </Button>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          <Card className="bg-[#19192A] border-[#26263A]">
            <CardHeader>
              <CardTitle className="text-white text-lg">Rendimiento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">CPU</span>
                  <span className="text-white">45%</span>
                </div>
                <div className="w-full bg-[#18181C] rounded-full h-2">
                  <div className="bg-blue-400 h-2 rounded-full" style={{ width: "45%" }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">GPU</span>
                  <span className="text-white">67%</span>
                </div>
                <div className="w-full bg-[#18181C] rounded-full h-2">
                  <div className="bg-pink-400 h-2 rounded-full" style={{ width: "67%" }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Memoria</span>
                  <span className="text-white">23%</span>
                </div>
                <div className="w-full bg-[#18181C] rounded-full h-2">
                  <div className="bg-green-400 h-2 rounded-full" style={{ width: "23%" }}></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
