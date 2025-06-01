"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Terminal, Square, RotateCcw } from "lucide-react"

interface TerminalLine {
  id: number
  type: "command" | "output" | "error" | "info"
  content: string
  timestamp: Date
}

const predefinedCommands = {
  help: "Comandos disponibles: ps aux, df -h, free -h, curl localhost:8000/health, clear",
  "ps aux":
    "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\ndw7       8988  2.1  3.4 125648 34567 ?        S    23:51   0:01 python src/main.py\ndw7       9001  0.5  1.2  45123 12345 ?        S    20:30   5:32 redis-server\ndw7       9123  0.1  0.8  23456  8901 ?        S    21:15   2:15 nginx worker",
  "df -h":
    "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        20G  12G  7.2G  63% /\n/dev/sda2       100G  45G   50G  48% /opt",
  "free -h":
    "              total        used        free      shared  buff/cache   available\nMem:           8.0G        2.1G        3.2G        256M        2.7G        5.4G\nSwap:          2.0G          0B        2.0G",
  "curl localhost:8000/health":
    '{"status":"ok","version":"1.0.0","timestamp":"2025-01-31T23:52:45Z","uptime":"5h 32m"}',
  "curl localhost:8000/api/vicky/vicky/status":
    '{"status":"active","confidence":94,"balance":{"technical":67,"emotional":33},"performance":"optimal"}',
  "systemctl status vokaflow":
    "● vokaflow.service - VokaFlow Backend Service\n   Loaded: loaded (/etc/systemd/system/vokaflow.service; enabled)\n   Active: active (running) since Fri 2025-01-31 18:20:15 UTC; 5h 32min ago\n   Main PID: 8988 (python)\n   Memory: 34.5M\n   CGroup: /system.slice/vokaflow.service\n           └─8988 python src/main.py",
  clear: "CLEAR_TERMINAL",
}

export function TerminalConsole() {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      id: 1,
      type: "info",
      content: "Welcome to VokaFlow Backend Terminal",
      timestamp: new Date(),
    },
    {
      id: 2,
      type: "info",
      content: "Type 'help' for available commands",
      timestamp: new Date(),
    },
  ])
  const [currentCommand, setCurrentCommand] = useState("")
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [isConnected, setIsConnected] = useState(true)
  const terminalRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [lines])

  const executeCommand = async (command: string) => {
    if (!command.trim()) return

    // Add command to history
    setCommandHistory((prev) => [...prev, command])
    setHistoryIndex(-1)

    // Add command line
    const commandLine: TerminalLine = {
      id: Date.now(),
      type: "command",
      content: `dw7@vokaflowbackend:/opt/vokaflow$ ${command}`,
      timestamp: new Date(),
    }

    setLines((prev) => [...prev, commandLine])

    // Handle clear command
    if (command.trim() === "clear") {
      setTimeout(() => {
        setLines([
          {
            id: Date.now(),
            type: "info",
            content: "Terminal cleared",
            timestamp: new Date(),
          },
        ])
      }, 100)
      return
    }

    // Simulate command execution
    setTimeout(
      () => {
        const output = predefinedCommands[command.trim() as keyof typeof predefinedCommands]

        if (output) {
          const outputLine: TerminalLine = {
            id: Date.now() + 1,
            type: "output",
            content: output,
            timestamp: new Date(),
          }
          setLines((prev) => [...prev, outputLine])
        } else {
          const errorLine: TerminalLine = {
            id: Date.now() + 1,
            type: "error",
            content: `bash: ${command}: command not found`,
            timestamp: new Date(),
          }
          setLines((prev) => [...prev, errorLine])
        }
      },
      Math.random() * 500 + 200,
    ) // Simulate network delay
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      executeCommand(currentCommand)
      setCurrentCommand("")
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1)
        setHistoryIndex(newIndex)
        setCurrentCommand(commandHistory[newIndex])
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault()
      if (historyIndex !== -1) {
        const newIndex = historyIndex + 1
        if (newIndex >= commandHistory.length) {
          setHistoryIndex(-1)
          setCurrentCommand("")
        } else {
          setHistoryIndex(newIndex)
          setCurrentCommand(commandHistory[newIndex])
        }
      }
    }
  }

  const getLineColor = (type: string) => {
    switch (type) {
      case "command":
        return "text-voka-blue"
      case "output":
        return "text-voka-white"
      case "error":
        return "text-voka-red"
      case "info":
        return "text-voka-green"
      default:
        return "text-voka-white"
    }
  }

  return (
    <div className="space-y-4">
      {/* Terminal Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Badge
            className={`${isConnected ? "bg-voka-green/20 text-voka-green border-voka-green" : "bg-voka-red/20 text-voka-red border-voka-red"} font-montserrat`}
          >
            {isConnected ? "🟢 SSH Connected" : "🔴 Disconnected"}
          </Badge>
          <span className="text-voka-gray font-montserrat text-sm">dw7@vokaflowbackend:/opt/vokaflow</span>
        </div>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className="border-voka-border text-voka-gray hover:text-voka-white"
            onClick={() => setLines([])}
          >
            <Square className="h-4 w-4 mr-2" />
            Clear
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="border-voka-border text-voka-gray hover:text-voka-white"
            onClick={() => setIsConnected(!isConnected)}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reconnect
          </Button>
        </div>
      </div>

      {/* Terminal Window */}
      <Card className="bg-voka-blue-black border-voka-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-voka-white font-montserrat flex items-center gap-2">
            <Terminal className="h-5 w-5 text-voka-magenta" />
            VokaFlow Terminal
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Terminal Output */}
          <div
            ref={terminalRef}
            className="bg-voka-dark rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm border border-voka-border"
            style={{ fontFamily: "'Fira Code', 'Consolas', monospace" }}
          >
            {lines.map((line) => (
              <div key={line.id} className={`${getLineColor(line.type)} whitespace-pre-wrap mb-1`}>
                {line.content}
              </div>
            ))}

            {/* Current prompt */}
            <div className="flex items-center text-voka-blue mt-2">
              <span>dw7@vokaflowbackend:/opt/vokaflow$ </span>
              <Input
                ref={inputRef}
                value={currentCommand}
                onChange={(e) => setCurrentCommand(e.target.value)}
                onKeyDown={handleKeyDown}
                className="bg-transparent border-none text-voka-white font-mono p-0 h-auto focus:ring-0 focus:border-none"
                placeholder=""
                disabled={!isConnected}
              />
              <span className="animate-pulse text-voka-white">█</span>
            </div>
          </div>

          {/* Quick Commands */}
          <div className="mt-4 flex flex-wrap gap-2">
            {Object.keys(predefinedCommands)
              .slice(0, 6)
              .map((cmd) => (
                <Button
                  key={cmd}
                  size="sm"
                  variant="outline"
                  className="border-voka-border text-voka-gray hover:text-voka-white font-mono text-xs"
                  onClick={() => {
                    setCurrentCommand(cmd)
                    inputRef.current?.focus()
                  }}
                >
                  {cmd}
                </Button>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
