"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Brain, Cpu, Heart, Zap } from "lucide-react"
import { vickyService } from "@/services/vicky-service"
import type { VickyStatus as VickyStatusType } from "@/types/vicky"
import { useToast } from "@/hooks/use-toast"

export function VickyStatus() {
  const [status, setStatus] = useState<VickyStatusType | null>(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await vickyService.getStatus()
        setStatus(data)
      } catch (error) {
        console.error("Error fetching Vicky status:", error)
        toast({
          title: "Error",
          description: "No se pudo obtener el estado de Vicky AI",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()

    // Actualizar cada 30 segundos
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [toast])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-voka-magenta"></div>
      </div>
    )
  }

  if (!status) {
    return (
      <div className="text-center p-6">
        <p className="text-voka-red">No se pudo cargar el estado de Vicky AI</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Visual - Female Head with Neural Network */}
      <div className="flex justify-center mb-8">
        <div className="relative">
          <div className="w-80 h-80 bg-gradient-to-br from-voka-magenta/20 to-voka-blue/20 rounded-full flex items-center justify-center border-2 border-voka-magenta/30">
            <div className="w-64 h-64 bg-gradient-to-br from-voka-magenta/10 to-voka-blue/10 rounded-full flex items-center justify-center relative overflow-hidden">
              {/* Neural Network Animation */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="grid grid-cols-6 gap-4 opacity-60">
                  {Array.from({ length: 24 }).map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded-full animate-pulse ${
                        i % 3 === 0 ? "bg-voka-magenta" : i % 3 === 1 ? "bg-voka-blue" : "bg-voka-green"
                      }`}
                      style={{
                        animationDelay: `${i * 0.1}s`,
                        animationDuration: "2s",
                      }}
                    />
                  ))}
                </div>
              </div>
              {/* Head Silhouette */}
              <Brain className="w-32 h-32 text-voka-magenta/80 z-10" />
            </div>
          </div>
          {/* Status Indicator */}
          <div className="absolute top-4 right-4">
            <div
              className={`w-4 h-4 rounded-full animate-pulse shadow-lg ${
                status.status === "online"
                  ? "bg-voka-green shadow-voka-green/50"
                  : status.status === "processing"
                    ? "bg-voka-yellow shadow-voka-yellow/50"
                    : "bg-voka-red shadow-voka-red/50"
              }`}
            />
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray flex items-center gap-2">
              <Cpu className="h-4 w-4 text-voka-blue" />
              TECHNICAL BALANCE
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-voka-white font-montserrat">{status.technicalBalance}%</div>
              <Progress value={status.technicalBalance} className="h-2" />
              <Badge className="bg-voka-blue/20 text-voka-blue border-voka-blue font-montserrat">
                {status.technicalBalance > 80 ? "High" : status.technicalBalance > 50 ? "Optimal" : "Low"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray flex items-center gap-2">
              <Heart className="h-4 w-4 text-voka-magenta" />
              EMOTIONAL BALANCE
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-2xl font-bold text-voka-white font-montserrat">{status.emotionalBalance}%</div>
              <Progress value={status.emotionalBalance} className="h-2" />
              <Badge className="bg-voka-magenta/20 text-voka-magenta border-voka-magenta font-montserrat">
                {status.emotionalBalance > 80 ? "High" : status.emotionalBalance > 50 ? "Optimal" : "Low"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray flex items-center gap-2">
              <Zap className="h-4 w-4 text-voka-yellow" />
              PERFORMANCE METRICS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="text-lg font-bold text-voka-white font-montserrat">{status.processingQueue} tok/s</div>
              <div className="text-sm text-voka-gray font-montserrat">{(status.cpuUsage * 100).toFixed(1)}% CPU</div>
              <div className="text-sm text-voka-gray font-montserrat">
                {(status.memoryUsage.used / 1024).toFixed(1)}GB RAM
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border hover:border-voka-magenta/50 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray flex items-center gap-2">
              <Brain className="h-4 w-4 text-voka-green" />
              HEALTH STATUS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div
                  className={`w-3 h-3 rounded-full animate-pulse ${
                    status.status === "online"
                      ? "bg-voka-green"
                      : status.status === "processing"
                        ? "bg-voka-yellow"
                        : "bg-voka-red"
                  }`}
                />
                <span
                  className={`font-montserrat font-semibold ${
                    status.status === "online"
                      ? "text-voka-green"
                      : status.status === "processing"
                        ? "text-voka-yellow"
                        : "text-voka-red"
                  }`}
                >
                  {status.status === "online" ? "OPTIMAL" : status.status === "processing" ? "BUSY" : "OFFLINE"}
                </span>
              </div>
              <div className="text-sm text-voka-gray font-montserrat">
                {status.status === "online"
                  ? "All systems operational"
                  : status.status === "processing"
                    ? "Processing requests"
                    : "System needs attention"}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-white font-montserrat">Balance Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48 flex items-end justify-between gap-2">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="flex flex-col items-center gap-1 flex-1">
                  <div className="w-full bg-voka-blue rounded-t" style={{ height: `${Math.random() * 80 + 20}%` }} />
                  <div className="w-full bg-voka-magenta rounded-b" style={{ height: `${Math.random() * 60 + 10}%` }} />
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-voka-blue rounded" />
                <span className="text-sm text-voka-gray font-montserrat">Technical</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-voka-magenta rounded" />
                <span className="text-sm text-voka-gray font-montserrat">Emotional</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-white font-montserrat">Memory Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-voka-gray font-montserrat">Neural Networks</span>
                  <span className="text-voka-white font-montserrat">
                    {((status.memoryUsage.used * 0.6) / 1024).toFixed(1)}GB
                  </span>
                </div>
                <Progress value={60} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-voka-gray font-montserrat">Context Cache</span>
                  <span className="text-voka-white font-montserrat">
                    {((status.memoryUsage.used * 0.3) / 1024).toFixed(1)}GB
                  </span>
                </div>
                <Progress value={30} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-voka-gray font-montserrat">System</span>
                  <span className="text-voka-white font-montserrat">
                    {((status.memoryUsage.used * 0.1) / 1024).toFixed(1)}GB
                  </span>
                </div>
                <Progress value={10} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
