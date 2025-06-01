"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Clock, Search, Filter, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import { vickyService } from "@/services/vicky-service"
import type { VickyDecision } from "@/types/vicky"
import { useToast } from "@/hooks/use-toast"

export function VickyHistory() {
  const [decisions, setDecisions] = useState<VickyDecision[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterType, setFilterType] = useState("all")
  const { toast } = useToast()

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        const data = await vickyService.getDecisions()
        setDecisions(data)
      } catch (error) {
        console.error("Error fetching Vicky decisions:", error)
        toast({
          title: "Error",
          description: "No se pudieron cargar las decisiones de Vicky AI",
          variant: "destructive",
        })
        // Usar datos mock si falla
        setDecisions([
          {
            id: 1,
            timestamp: "15:32:45",
            confidence: 94,
            type: "Translation",
            context: "User asked for Spanish to English translation",
            decision: "Use NLLB model with context preservation",
            result: "success",
            responseTime: "1.2s",
          },
          {
            id: 2,
            timestamp: "15:28:12",
            confidence: 87,
            type: "Personality",
            context: "User requested more technical assistance",
            decision: "Switch to Technical personality mode",
            result: "success",
            responseTime: "0.8s",
          },
          {
            id: 3,
            timestamp: "15:25:33",
            confidence: 76,
            type: "Content",
            context: "Complex multi-language query detected",
            decision: "Activate enhanced context analysis",
            result: "warning",
            responseTime: "2.1s",
          },
          {
            id: 4,
            timestamp: "15:22:18",
            confidence: 98,
            type: "Emotion",
            context: "User expressed frustration in message",
            decision: "Increase empathy level and provide reassurance",
            result: "success",
            responseTime: "0.9s",
          },
          {
            id: 5,
            timestamp: "15:19:45",
            confidence: 82,
            type: "Translation",
            context: "Technical document translation requested",
            decision: "Use specialized technical vocabulary model",
            result: "success",
            responseTime: "1.7s",
          },
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchDecisions()
  }, [toast])

  // Filtrar decisiones
  const filteredDecisions = decisions.filter((decision) => {
    const matchesSearch =
      decision.context.toLowerCase().includes(searchTerm.toLowerCase()) ||
      decision.decision.toLowerCase().includes(searchTerm.toLowerCase()) ||
      decision.type.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesType = filterType === "all" || decision.type.toLowerCase() === filterType.toLowerCase()

    return matchesSearch && matchesType
  })

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-voka-gray" />
                <Input
                  placeholder="Search decisions..."
                  className="pl-10 bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <Select defaultValue="all" onValueChange={setFilterType}>
              <SelectTrigger className="w-full md:w-48 bg-voka-dark border-voka-border text-voka-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-voka-blue-black border-voka-border">
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="translation">Translation</SelectItem>
                <SelectItem value="personality">Personality</SelectItem>
                <SelectItem value="content">Content</SelectItem>
                <SelectItem value="emotion">Emotion</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="border-voka-border text-voka-gray hover:text-voka-white">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Decision Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-green font-montserrat">
              {loading
                ? "..."
                : `${Math.round((decisions.filter((d) => d.result === "success").length / decisions.length) * 100)}%`}
            </div>
            <div className="text-sm text-voka-gray font-montserrat">Last 24 hours</div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Avg Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-blue font-montserrat">
              {loading
                ? "..."
                : `${Math.round(decisions.reduce((acc, d) => acc + d.confidence, 0) / decisions.length)}%`}
            </div>
            <div className="text-sm text-voka-gray font-montserrat">All decisions</div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Avg Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-yellow font-montserrat">
              {loading
                ? "..."
                : `${decisions.reduce((acc, d) => acc + Number.parseFloat(d.responseTime), 0) / decisions.length}s`}
            </div>
            <div className="text-sm text-voka-gray font-montserrat">Processing time</div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <Clock className="h-5 w-5 text-voka-magenta" />
            Decision Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-voka-magenta"></div>
            </div>
          ) : filteredDecisions.length === 0 ? (
            <div className="text-center py-8 text-voka-gray">No decisions found matching your criteria</div>
          ) : (
            <div className="space-y-4">
              {filteredDecisions.map((decision) => (
                <div key={decision.id} className="border-l-2 border-voka-border pl-4 pb-4 relative">
                  <div className="absolute -left-2 top-0 w-4 h-4 rounded-full bg-voka-magenta border-2 border-voka-dark" />

                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-voka-gray font-montserrat text-sm">🕐 {decision.timestamp}</span>
                      <Badge
                        className={`font-montserrat ${
                          decision.confidence >= 90
                            ? "bg-voka-green/20 text-voka-green border-voka-green"
                            : decision.confidence >= 80
                              ? "bg-voka-yellow/20 text-voka-yellow border-voka-yellow"
                              : "bg-voka-orange/20 text-voka-orange border-voka-orange"
                        }`}
                      >
                        Confidence: {decision.confidence}%
                      </Badge>
                      <Badge className="bg-voka-blue/20 text-voka-blue border-voka-blue font-montserrat">
                        {decision.type}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2">
                      {decision.result === "success" && <CheckCircle className="h-4 w-4 text-voka-green" />}
                      {decision.result === "warning" && <AlertCircle className="h-4 w-4 text-voka-yellow" />}
                      {decision.result === "error" && <XCircle className="h-4 w-4 text-voka-red" />}
                      <span className="text-voka-gray font-montserrat text-sm">({decision.responseTime})</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-voka-gray font-montserrat text-sm">
                      <strong>Context:</strong> {decision.context}
                    </div>
                    <div className="text-voka-white font-montserrat text-sm">
                      <strong>Decision:</strong> {decision.decision}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
