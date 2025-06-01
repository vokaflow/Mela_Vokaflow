// Tipos para servidores
export interface Server {
  id: string
  name: string
  status: "online" | "offline" | "warning" | "maintenance"
  ip: string
  location: string
  type: string
  cpu: number
  memory: number
  disk: number
  uptime: string
  lastReboot: string
  services: string[]
}

// Tipos para red
export interface NetworkDevice {
  id: string
  name: string
  type: "router" | "switch" | "firewall" | "loadbalancer" | "gateway"
  status: "online" | "offline" | "warning"
  ip: string
  location: string
  throughput: number
  connections: number
  latency: number
}

export interface NetworkConnection {
  source: string
  target: string
  status: "active" | "inactive" | "degraded"
  bandwidth: number
  latency: number
  packetLoss: number
}

// Tipos para alertas
export interface Alert {
  id: string
  timestamp: string
  level: "critical" | "warning" | "info"
  source: string
  message: string
  acknowledged: boolean
  resolved: boolean
}

// Tipos para logs
export interface LogEntry {
  id: string
  timestamp: string
  level: "error" | "warning" | "info" | "debug"
  source: string
  message: string
  details?: string
}

// Tipos para servicios
export interface Service {
  id: string
  name: string
  status: "running" | "stopped" | "warning" | "restarting"
  type: string
  server: string
  port: number
  uptime: string
  memory: number
  cpu: number
  dependencies: string[]
}

// Tipos para backups
export interface Backup {
  id: string
  name: string
  type: "full" | "incremental" | "differential"
  status: "completed" | "in-progress" | "failed" | "scheduled"
  source: string
  destination: string
  size: number
  startTime: string
  endTime?: string
  nextScheduled?: string
}

// Tipos para clusters
export interface ClusterNode {
  id: string
  name: string
  status: "active" | "standby" | "failed"
  role: "primary" | "secondary" | "arbiter"
  ip: string
  cpu: number
  memory: number
  lastHeartbeat: string
}

export interface Cluster {
  id: string
  name: string
  type: string
  status: "healthy" | "degraded" | "critical"
  nodes: ClusterNode[]
  services: string[]
}

// Tipos para métricas
export interface SystemMetrics {
  timestamp: string
  cpu: number
  memory: number
  disk: number
  network: number
  activeUsers: number
  activeProcesses: number
  temperature: number
}
