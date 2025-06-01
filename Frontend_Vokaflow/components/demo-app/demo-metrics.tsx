"use client"

import { useEffect, useState } from "react"
import type { DemoMetrics } from "@/types/demo-app"
import { DemoAppService } from "@/services/demo-app-service"

interface DemoMetricsProps {
  initialMetrics?: DemoMetrics
}

export function DemoMetrics({ initialMetrics }: DemoMetricsProps) {
  const [metrics, setMetrics] = useState<DemoMetrics>(
    initialMetrics || {
      latency: { current: 0.3, average: 0.4, history: Array(10).fill(0.4) },
      accuracy: { "es-en": 0.98, "en-es": 0.97, "fr-es": 0.94, overall: 0.96 },
      audio: { ttsStatus: "ok", sttStatus: "ok", quality: "HD", latency: 0.2 },
      translations: { total: 1247, perMinute: 15, successful: 1240, failed: 7 },
    },
  )

  useEffect(() => {
    // Actualizar métricas cada 2 segundos
    const interval = setInterval(async () => {
      try {
        const newMetrics = await DemoAppService.getMetrics()
        setMetrics((prev) => ({
          ...prev,
          ...newMetrics,
          // Mantener historial de latencia
          latency: {
            ...newMetrics.latency,
            history: [...prev.latency.history.slice(1), newMetrics.latency.current],
          },
          // Incrementar contador de traducciones
          translations: {
            ...newMetrics.translations,
            total: prev.translations.total + Math.floor(Math.random() * 3),
          },
        }))
      } catch (error) {
        console.error("Error al actualizar métricas:", error)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  // Función para renderizar el mini gráfico de latencia
  const renderLatencyChart = () => {
    const max = Math.max(...metrics.latency.history, 0.6)
    const min = Math.min(...metrics.latency.history, 0.2)
    const range = max - min

    return (
      <div className="flex items-end h-6 space-x-[2px]">
        {metrics.latency.history.map((value, index) => {
          const height = Math.max(((value - min) / range) * 100, 10)
          return (
            <div
              key={index}
              className="bg-voka-blue w-2 rounded-t-sm transition-all duration-500 ease-in-out"
              style={{ height: `${height}%` }}
            />
          )
        })}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full space-y-4 p-4 bg-voka-blue-black rounded-lg border border-voka-border">
      <h3 className="text-lg font-bold text-voka-white font-montserrat">📊 MÉTRICAS TIEMPO REAL</h3>

      {/* Latencia */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h4 className="text-sm font-medium text-voka-gray mb-1">📈 LATENCIA</h4>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-voka-white text-sm">
              Actual: <span className="text-voka-green">{metrics.latency.current.toFixed(1)}s</span>
            </p>
            <p className="text-voka-white text-sm">Promedio: {metrics.latency.average.toFixed(1)}s</p>
          </div>
          <div className="w-24">{renderLatencyChart()}</div>
        </div>
      </div>

      {/* Precisión */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h4 className="text-sm font-medium text-voka-gray mb-1">📊 PRECISIÓN</h4>
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-xs">
              <span className="text-voka-white">ES→EN:</span>
              <span className="text-voka-green">{(metrics.accuracy["es-en"] * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-voka-border rounded-full h-1.5 mt-1">
              <div
                className="bg-voka-green h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.accuracy["es-en"] * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs">
              <span className="text-voka-white">EN→ES:</span>
              <span className="text-voka-green">{(metrics.accuracy["en-es"] * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-voka-border rounded-full h-1.5 mt-1">
              <div
                className="bg-voka-green h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.accuracy["en-es"] * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs">
              <span className="text-voka-white">FR→ES:</span>
              <span className="text-voka-green">{(metrics.accuracy["fr-es"] * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-voka-border rounded-full h-1.5 mt-1">
              <div
                className="bg-voka-green h-1.5 rounded-full transition-all duration-500"
                style={{ width: `${metrics.accuracy["fr-es"] * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Audio */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h4 className="text-sm font-medium text-voka-gray mb-1">🔊 AUDIO</h4>
        <div className="grid grid-cols-2 gap-2">
          <div className="text-sm">
            <span className="text-voka-gray">TTS:</span>
            <span className="ml-1 text-voka-green">OK ✅</span>
          </div>
          <div className="text-sm">
            <span className="text-voka-gray">STT:</span>
            <span className="ml-1 text-voka-green">OK ✅</span>
          </div>
          <div className="text-sm">
            <span className="text-voka-gray">Calidad:</span>
            <span className="ml-1 text-voka-white">HD</span>
          </div>
          <div className="text-sm">
            <span className="text-voka-gray">Latencia:</span>
            <span className="ml-1 text-voka-white">{metrics.audio.latency.toFixed(1)}s</span>
          </div>
        </div>
      </div>

      {/* Traducciones */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h4 className="text-sm font-medium text-voka-gray mb-1">🔄 TRADUCCIONES</h4>
        <div className="text-center">
          <div className="text-2xl font-bold text-voka-magenta font-montserrat animate-pulse">
            {metrics.translations.total.toLocaleString()}
          </div>
          <div className="text-xs text-voka-gray mt-1">
            {metrics.translations.perMinute}/min | {metrics.translations.successful} exitosas
          </div>
        </div>
      </div>
    </div>
  )
}
