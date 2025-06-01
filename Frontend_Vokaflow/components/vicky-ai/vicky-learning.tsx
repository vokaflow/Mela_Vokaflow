"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { GraduationCap, TrendingUp, Database, Cpu, Play, Pause } from "lucide-react"

export function VickyLearning() {
  return (
    <div className="space-y-6">
      {/* Learning Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Training Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-magenta font-montserrat">73%</div>
            <Progress value={73} className="h-2 mt-2" />
            <div className="text-sm text-voka-gray font-montserrat mt-1">Current session</div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Learning Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-blue font-montserrat">0.001</div>
            <div className="text-sm text-voka-gray font-montserrat">Adaptive rate</div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Models Updated</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-green font-montserrat">12</div>
            <div className="text-sm text-voka-gray font-montserrat">This week</div>
          </CardContent>
        </Card>

        <Card className="bg-voka-blue-black border-voka-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-montserrat text-voka-gray">Next Training</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-voka-yellow font-montserrat">2h</div>
            <div className="text-sm text-voka-gray font-montserrat">Scheduled</div>
          </CardContent>
        </Card>
      </div>

      {/* Current Training Session */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-voka-magenta" />
            Current Training Session
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-voka-white font-montserrat font-semibold">Emotional Intelligence Enhancement</div>
              <div className="text-voka-gray font-montserrat text-sm">
                Training on empathy and emotional recognition
              </div>
            </div>
            <Badge className="bg-voka-green/20 text-voka-green border-voka-green font-montserrat">Active</Badge>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-voka-gray font-montserrat">Progress</span>
              <span className="text-voka-white font-montserrat">73% (2,847/3,900 samples)</span>
            </div>
            <Progress value={73} className="h-3" />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-voka-gray font-montserrat">Epoch</div>
              <div className="text-voka-white font-montserrat">15/20</div>
            </div>
            <div>
              <div className="text-voka-gray font-montserrat">Loss</div>
              <div className="text-voka-white font-montserrat">0.0234</div>
            </div>
            <div>
              <div className="text-voka-gray font-montserrat">Accuracy</div>
              <div className="text-voka-white font-montserrat">94.7%</div>
            </div>
            <div>
              <div className="text-voka-gray font-montserrat">ETA</div>
              <div className="text-voka-white font-montserrat">1h 23m</div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button size="sm" variant="outline" className="border-voka-border text-voka-gray hover:text-voka-white">
              <Pause className="h-4 w-4 mr-2" />
              Pause
            </Button>
            <Button size="sm" variant="outline" className="border-voka-border text-voka-gray hover:text-voka-white">
              View Logs
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Performance Trends */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-voka-blue" />
            Performance Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="text-voka-gray font-montserrat text-sm">Accuracy Improvement (30 days)</div>
              <div className="h-32 flex items-end justify-between gap-1">
                {Array.from({ length: 30 }).map((_, i) => (
                  <div
                    key={i}
                    className="bg-voka-green rounded-t flex-1"
                    style={{ height: `${Math.random() * 80 + 20}%` }}
                  />
                ))}
              </div>
              <div className="text-voka-green font-montserrat text-sm">+12.3% improvement</div>
            </div>

            <div className="space-y-4">
              <div className="text-voka-gray font-montserrat text-sm">Response Time Optimization</div>
              <div className="h-32 flex items-end justify-between gap-1">
                {Array.from({ length: 30 }).map((_, i) => (
                  <div
                    key={i}
                    className="bg-voka-blue rounded-t flex-1"
                    style={{ height: `${Math.random() * 60 + 40}%` }}
                  />
                ))}
              </div>
              <div className="text-voka-blue font-montserrat text-sm">-23% faster responses</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Training Controls */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader>
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <Cpu className="h-5 w-5 text-voka-orange" />
            Training Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="text-voka-gray font-montserrat text-sm">Available Training Modules</div>
              <div className="space-y-2">
                {[
                  { name: "Language Understanding", status: "ready" },
                  { name: "Emotional Intelligence", status: "training" },
                  { name: "Technical Knowledge", status: "ready" },
                  { name: "Creative Writing", status: "scheduled" },
                ].map((module) => (
                  <div
                    key={module.name}
                    className="flex items-center justify-between p-2 bg-voka-dark rounded border border-voka-border"
                  >
                    <span className="text-voka-white font-montserrat text-sm">{module.name}</span>
                    <Badge
                      className={`font-montserrat text-xs ${
                        module.status === "training"
                          ? "bg-voka-green/20 text-voka-green border-voka-green"
                          : module.status === "ready"
                            ? "bg-voka-blue/20 text-voka-blue border-voka-blue"
                            : "bg-voka-yellow/20 text-voka-yellow border-voka-yellow"
                      }`}
                    >
                      {module.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <div className="text-voka-gray font-montserrat text-sm">Quick Actions</div>
              <div className="space-y-2">
                <Button className="w-full bg-voka-magenta hover:bg-voka-magenta/80 text-white font-montserrat">
                  <Play className="h-4 w-4 mr-2" />
                  Start Manual Training
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
                >
                  <Database className="h-4 w-4 mr-2" />
                  Update Training Data
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-voka-border text-voka-gray hover:text-voka-white font-montserrat"
                >
                  Export Training Report
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
