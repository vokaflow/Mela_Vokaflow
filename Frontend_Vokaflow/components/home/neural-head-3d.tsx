"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"

export function NeuralHead3D() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isAnimating, setIsAnimating] = useState(true)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Configurar canvas
    canvas.width = 400
    canvas.height = 500

    // Puntos de la cabeza femenina
    const headPoints = [
      // Contorno facial
      { x: 200, y: 100 },
      { x: 180, y: 120 },
      { x: 165, y: 150 },
      { x: 155, y: 180 },
      { x: 150, y: 210 },
      { x: 155, y: 240 },
      { x: 165, y: 270 },
      { x: 180, y: 300 },
      { x: 200, y: 320 },
      { x: 220, y: 300 },
      { x: 235, y: 270 },
      { x: 245, y: 240 },
      { x: 250, y: 210 },
      { x: 245, y: 180 },
      { x: 235, y: 150 },
      { x: 220, y: 120 },
      // Cabello
      { x: 200, y: 80 },
      { x: 170, y: 90 },
      { x: 140, y: 110 },
      { x: 120, y: 140 },
      { x: 260, y: 140 },
      { x: 280, y: 110 },
      { x: 230, y: 90 },
      // Ojos
      { x: 180, y: 160 },
      { x: 220, y: 160 },
      // Nariz
      { x: 200, y: 190 },
      // Boca
      { x: 200, y: 220 },
    ]

    // Neuronas (puntos adicionales para el efecto neural)
    const neurons = []
    for (let i = 0; i < 50; i++) {
      neurons.push({
        x: Math.random() * 400,
        y: Math.random() * 500,
        pulse: Math.random() * Math.PI * 2,
        speed: 0.02 + Math.random() * 0.03,
      })
    }

    // Conexiones neurales
    const connections = []
    for (let i = 0; i < headPoints.length; i++) {
      for (let j = i + 1; j < headPoints.length; j++) {
        const distance = Math.sqrt(
          Math.pow(headPoints[i].x - headPoints[j].x, 2) + Math.pow(headPoints[i].y - headPoints[j].y, 2),
        )
        if (distance < 80) {
          connections.push({
            from: headPoints[i],
            to: headPoints[j],
            opacity: Math.random(),
          })
        }
      }
    }

    let animationFrame: number

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Fondo con gradiente
      const gradient = ctx.createRadialGradient(200, 250, 0, 200, 250, 300)
      gradient.addColorStop(0, "rgba(216, 64, 159, 0.1)")
      gradient.addColorStop(1, "rgba(24, 24, 44, 0.8)")
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Dibujar conexiones neurales
      connections.forEach((conn, index) => {
        const pulse = Math.sin(Date.now() * 0.001 + index * 0.1) * 0.5 + 0.5
        ctx.strokeStyle = `rgba(53, 255, 131, ${pulse * 0.6})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(conn.from.x, conn.from.y)
        ctx.lineTo(conn.to.x, conn.to.y)
        ctx.stroke()
      })

      // Dibujar contorno de la cabeza
      ctx.strokeStyle = "#D8409F"
      ctx.lineWidth = 3
      ctx.beginPath()
      headPoints.slice(0, 16).forEach((point, index) => {
        if (index === 0) {
          ctx.moveTo(point.x, point.y)
        } else {
          ctx.lineTo(point.x, point.y)
        }
      })
      ctx.closePath()
      ctx.stroke()

      // Dibujar cabello
      ctx.strokeStyle = "#0078FF"
      ctx.lineWidth = 2
      ctx.beginPath()
      headPoints.slice(16, 23).forEach((point, index) => {
        if (index === 0) {
          ctx.moveTo(point.x, point.y)
        } else {
          ctx.lineTo(point.x, point.y)
        }
      })
      ctx.stroke()

      // Dibujar ojos
      ctx.fillStyle = "#35FF83"
      headPoints.slice(23, 25).forEach((point) => {
        ctx.beginPath()
        ctx.arc(point.x, point.y, 4, 0, Math.PI * 2)
        ctx.fill()
      })

      // Dibujar nariz
      ctx.strokeStyle = "#FFA700"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(headPoints[25].x, headPoints[25].y - 10)
      ctx.lineTo(headPoints[25].x, headPoints[25].y + 10)
      ctx.stroke()

      // Dibujar boca
      ctx.strokeStyle = "#FF3366"
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(headPoints[26].x, headPoints[26].y, 8, 0, Math.PI)
      ctx.stroke()

      // Dibujar neuronas pulsantes
      neurons.forEach((neuron) => {
        neuron.pulse += neuron.speed
        const size = 2 + Math.sin(neuron.pulse) * 1.5
        const opacity = 0.3 + Math.sin(neuron.pulse) * 0.4

        ctx.fillStyle = `rgba(255, 251, 0, ${opacity})`
        ctx.beginPath()
        ctx.arc(neuron.x, neuron.y, size, 0, Math.PI * 2)
        ctx.fill()
      })

      // Efecto de partículas
      const time = Date.now() * 0.001
      for (let i = 0; i < 20; i++) {
        const x = 200 + Math.sin(time + i) * 150
        const y = 250 + Math.cos(time + i * 0.5) * 100
        const opacity = Math.sin(time * 2 + i) * 0.3 + 0.2

        ctx.fillStyle = `rgba(216, 64, 159, ${opacity})`
        ctx.beginPath()
        ctx.arc(x, y, 1, 0, Math.PI * 2)
        ctx.fill()
      }

      if (isAnimating) {
        animationFrame = requestAnimationFrame(animate)
      }
    }

    animate()

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame)
      }
    }
  }, [isAnimating])

  return (
    <Card className="bg-voka-blue-black border-voka-border p-6 relative overflow-hidden">
      <div className="text-center mb-4">
        <h3 className="text-2xl font-bold text-voka-white font-montserrat mb-2">🧠 Vicky AI Neural Core</h3>
        <p className="text-voka-gray font-montserrat">Inteligencia Artificial Central VokaFlow</p>
      </div>

      <div className="flex justify-center">
        <canvas
          ref={canvasRef}
          className="border border-voka-border/30 rounded-lg"
          style={{ maxWidth: "100%", height: "auto" }}
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-center">
        <div>
          <div className="text-voka-magenta font-bold text-lg">98.7%</div>
          <div className="text-voka-gray text-sm">Precisión Neural</div>
        </div>
        <div>
          <div className="text-voka-green font-bold text-lg">45ms</div>
          <div className="text-voka-gray text-sm">Latencia</div>
        </div>
      </div>

      <button
        onClick={() => setIsAnimating(!isAnimating)}
        className="absolute top-4 right-4 text-voka-gray hover:text-voka-magenta transition-colors"
      >
        {isAnimating ? "⏸️" : "▶️"}
      </button>
    </Card>
  )
}
