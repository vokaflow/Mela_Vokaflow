"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { FlaskConical, Play, Download, BarChart3, Zap } from "lucide-react"

const experiments = [
  {
    id: 1,
    name: "Personality Comparison A/B",
    status: "running",
    progress: 67,
    participants: 234,
    significance: 0.85,
  },
  {
    id: 2,
    name: "Response Time Optimization",
    status: "completed",
    progress: 100,
    participants: 156,
    significance: 0.92,
  },
  {
    id: 3,
    name: "Emotional Context Enhancement",
    status: "scheduled",
    progress: 0,
    participants: 0,
    significance: 0,
  },
]

export function VickyExperimental() {
  const [testQuery, setTestQuery] = useState("")
  const [selectedPersonalities, setSelectedPersonalities] = useState(["balanced", "technical"])

  return (
    <div className="space-y-6">
      {/* Experiment Playground */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-voka-magenta" />
            Experiment Playground
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <label className="text-voka-gray font-montserrat text-sm">Test Query</label>
            <Textarea
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder="Enter your test query here..."
              className="bg-voka-dark border-voka-border text-voka-white placeholder:text-voka-gray font-montserrat"
              rows={4}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <label className="text-voka-gray font-montserrat text-sm">Personality A</label>
              <Select defaultValue="balanced">
                <SelectTrigger className="bg-voka-dark border-voka-border text-voka-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-voka-blue-black border-voka-border">
                  <SelectItem value="balanced">⚖️ Balanced</SelectItem>
                  <SelectItem value="technical">🔧 Technical</SelectItem>
                  <SelectItem value="creative">🎨 Creative</SelectItem>
                  <SelectItem value="analytical">📊 Analytical</SelectItem>
                  <SelectItem value="empathetic">💝 Empathetic</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-3">
              <label className="text-voka-gray font-montserrat text-sm">Personality B</label>
              <Select defaultValue="technical">
                <SelectTrigger className="bg-voka-dark border-voka-border text-voka-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-voka-blue-black border-voka-border">
                  <SelectItem value="balanced">⚖️ Balanced</SelectItem>
                  <SelectItem value="technical">🔧 Technical</SelectItem>
                  <SelectItem value="creative">🎨 Creative</SelectItem>
                  <SelectItem value="analytical">📊 Analytical</SelectItem>
                  <SelectItem value="empathetic">💝 Empathetic</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button className="w-full bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat">
            <Play className="h-4 w-4 mr-2" />
            Run Comparison Test
          </Button>
        </CardContent>
      </Card>

      {/* Side-by-side Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-blue font-montserrat">⚖️ Balanced Response</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-voka-dark rounded-lg p-4 border border-voka-border min-h-32">
              <div className="text-voka-gray font-montserrat text-sm mb-2">Response will appear here...</div>
              <div className="text-voka-white font-montserrat text-sm">
                Run a test query to see the balanced personality response.
              </div>
            </div>
            <div className="mt-4 flex justify-between text-sm">
              <span className="text-voka-gray font-montserrat">Response time: --</span>
              <span className="text-voka-gray font-montserrat">Confidence: --%</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader>
            <CardTitle className="text-voka-orange font-montserrat">🔧 Technical Response</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-voka-dark rounded-lg p-4 border border-voka-border min-h-32">
              <div className="text-voka-gray font-montserrat text-sm mb-2">Response will appear here...</div>
              <div className="text-voka-white font-montserrat text-sm">
                Run a test query to see the technical personality response.
              </div>
            </div>
            <div className="mt-4 flex justify-between text-sm">
              <span className="text-voka-gray font-montserrat">Response time: --</span>
              <span className="text-voka-gray font-montserrat">Confidence: --%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* A/B Testing Dashboard */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-voka-blue" />
            A/B Testing Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {experiments.map((experiment) => (
              <div key={experiment.id} className="p-4 bg-voka-dark rounded-lg border border-voka-border">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="text-voka-white font-montserrat font-semibold">{experiment.name}</div>
                    <div className="text-voka-gray font-montserrat text-sm">{experiment.participants} participants</div>
                  </div>
                  <Badge
                    className={`font-montserrat ${
                      experiment.status === "running"
                        ? "bg-voka-green/20 text-voka-green border-voka-green"
                        : experiment.status === "completed"
                          ? "bg-voka-blue/20 text-voka-blue border-voka-blue"
                          : "bg-voka-yellow/20 text-voka-yellow border-voka-yellow"
                    }`}
                  >
                    {experiment.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <div className="text-voka-gray font-montserrat">Progress</div>
                    <div className="text-voka-white font-montserrat">{experiment.progress}%</div>
                  </div>
                  <div>
                    <div className="text-voka-gray font-montserrat">Statistical Significance</div>
                    <div className="text-voka-white font-montserrat">
                      {experiment.significance > 0 ? `${(experiment.significance * 100).toFixed(1)}%` : "--"}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {experiment.status === "completed" && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-voka-border text-voka-gray hover:text-voka-white"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Export
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-voka-border text-voka-gray hover:text-voka-white"
                    >
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex gap-4">
            <Button className="bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat">
              <Zap className="h-4 w-4 mr-2" />
              Create New Experiment
            </Button>
            <Button
              variant="outline"
              className="border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
            >
              Export All Results
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Advanced Features */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat">Advanced Experimental Features</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="text-voka-gray font-montserrat text-sm">Custom Prompt Templates</div>
              <div className="space-y-2">
                {["System Prompt Variations", "Context Injection Tests", "Response Format Experiments"].map(
                  (template) => (
                    <div key={template} className="p-2 bg-voka-dark rounded border border-voka-border">
                      <span className="text-voka-white font-montserrat text-sm">{template}</span>
                    </div>
                  ),
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="text-voka-gray font-montserrat text-sm">Performance Benchmarks</div>
              <div className="space-y-2">
                {["Response Quality Score", "Coherence Analysis", "Factual Accuracy Test"].map((benchmark) => (
                  <div key={benchmark} className="p-2 bg-voka-dark rounded border border-voka-border">
                    <span className="text-voka-white font-montserrat text-sm">{benchmark}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
