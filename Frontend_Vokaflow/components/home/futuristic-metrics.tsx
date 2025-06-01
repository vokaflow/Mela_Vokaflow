"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useEffect, useState } from "react"
import { Activity, Zap, Globe, Users, Brain, Cpu, HardDrive, Wifi } from "lucide-react"

export function FuturisticMetrics() {
  const [metrics, setMetrics] = useState({
    systemHealth: 98.7,
    activeUsers: 2847,
    aiProcessing: 15234,
    globalConnections: 156,
    cpuUsage: 67,
    memoryUsage: 45,
    networkLatency: 23,
    vickyResponses: 3421,
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        systemHealth: 95 + Math.random() * 5,
        activeUsers: 2800 + Math.floor(Math.random() * 100),
        aiProcessing: 15000 + Math.floor(Math.random() * 500),
        globalConnections: 150 + Math.floor(Math.random() * 20),
        cpuUsage: 60 + Math.floor(Math.random() * 20),
        memoryUsage: 40 + Math.floor(Math.random() * 20),
        networkLatency: 20 + Math.floor(Math.random() * 10),
        vickyResponses: 3400 + Math.floor(Math.random() * 50),
      }))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const metricsData = [
    {
      title: "Estado del Sistema",
      value: `${metrics.systemHealth.toFixed(1)}%`,
      icon: Activity,
      color: "text-voka-green",
      bgColor: "bg-voka-green/10",
      progress: metrics.systemHealth,
    },
    {
      title: "Usuarios Activos",
      value: metrics.activeUsers.toLocaleString(),
      icon: Users,
      color: "text-voka-blue",
      bgColor: "bg-voka-blue/10",
      progress: (metrics.activeUsers / 3000) * 100,
    },
    {
      title: "Procesamiento IA",
      value: metrics.aiProcessing.toLocaleString(),
      icon: Brain,
      color: "text-voka-magenta",
      bgColor: "bg-voka-magenta/10",
      progress: (metrics.aiProcessing / 16000) * 100,
    },
    {
      title: "Conexiones Globales",
      value: metrics.globalConnections.toString(),
      icon: Globe,
      color: "text-voka-yellow",
      bgColor: "bg-voka-yellow/10",
      progress: (metrics.globalConnections / 200) * 100,
    },
    {
      title: "Uso CPU",
      value: `${metrics.cpuUsage}%`,
      icon: Cpu,
      color: "text-voka-orange",
      bgColor: "bg-voka-orange/10",
      progress: metrics.cpuUsage,
    },
    {
      title: "Memoria",
      value: `${metrics.memoryUsage}%`,
      icon: HardDrive,
      color: "text-voka-blue",
      bgColor: "bg-voka-blue/10",
      progress: metrics.memoryUsage,
    },
    {
      title: "Latencia Red",
      value: `${metrics.networkLatency}ms`,
      icon: Wifi,
      color: "text-voka-green",
      bgColor: "bg-voka-green/10",
      progress: 100 - (metrics.networkLatency / 50) * 100,
    },
    {
      title: "Respuestas Vicky",
      value: metrics.vickyResponses.toLocaleString(),
      icon: Zap,
      color: "text-voka-magenta",
      bgColor: "bg-voka-magenta/10",
      progress: (metrics.vickyResponses / 4000) * 100,
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metricsData.map((metric, index) => (
        <Card
          key={metric.title}
          className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-all duration-300 relative overflow-hidden group"
        >
          <div
            className={`absolute inset-0 ${metric.bgColor} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
          />

          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
            <CardTitle className="text-sm font-medium text-voka-gray font-montserrat">{metric.title}</CardTitle>
            <metric.icon className={`h-5 w-5 ${metric.color}`} />
          </CardHeader>

          <CardContent className="relative z-10">
            <div className="text-2xl font-bold text-voka-white font-montserrat mb-2">{metric.value}</div>

            <Progress value={metric.progress} className="h-2 mb-2" />

            <Badge variant="secondary" className={`${metric.color} bg-transparent border font-montserrat`}>
              {metric.progress > 80 ? "Óptimo" : metric.progress > 60 ? "Bueno" : "Atención"}
            </Badge>
          </CardContent>

          {/* Efecto de partículas */}
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className={`absolute w-1 h-1 ${metric.color.replace("text-", "bg-")} rounded-full opacity-30 animate-pulse`}
                style={{
                  left: `${20 + i * 15}%`,
                  top: `${30 + (i % 2) * 40}%`,
                  animationDelay: `${i * 0.2}s`,
                }}
              />
            ))}
          </div>
        </Card>
      ))}
    </div>
  )
}
