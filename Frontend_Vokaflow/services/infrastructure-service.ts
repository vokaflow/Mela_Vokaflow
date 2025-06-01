import type {
  Server,
  NetworkDevice,
  NetworkConnection,
  Alert,
  LogEntry,
  Service,
  Backup,
  Cluster,
  SystemMetrics,
} from "../types/infrastructure"

const API_BASE_URL = "/api/infrastructure"

// Datos mock para desarrollo
const mockServers: Server[] = [
  {
    id: "srv-001",
    name: "VokaFlow-Main-01",
    ip: "192.168.1.10",
    status: "online",
    location: "Datacenter Principal",
    type: "Aplicación",
    cpu: 45,
    memory: 67,
    disk: 23,
    uptime: "15d 8h 32m",
    lastReboot: "2024-11-15 14:30:00",
    services: ["VokaFlow API", "Redis Cache", "Nginx", "PostgreSQL"],
  },
  {
    id: "srv-002",
    name: "VokaFlow-AI-02",
    ip: "192.168.1.11",
    status: "online",
    location: "Datacenter Principal",
    type: "IA/ML",
    cpu: 78,
    memory: 89,
    disk: 45,
    uptime: "12d 4h 15m",
    lastReboot: "2024-11-18 09:15:00",
    services: ["Vicky AI Core", "Translation Engine", "Voice Synthesis", "ML Models"],
  },
  {
    id: "srv-003",
    name: "VokaFlow-DB-03",
    ip: "192.168.1.12",
    status: "warning",
    location: "Datacenter Secundario",
    type: "Base de Datos",
    cpu: 23,
    memory: 91,
    disk: 78,
    uptime: "8d 12h 45m",
    lastReboot: "2024-11-22 16:20:00",
    services: ["PostgreSQL Master", "Redis Cluster", "Backup Service"],
  },
]

const mockNetworkDevices: NetworkDevice[] = [
  {
    id: "net-001",
    name: "Router Principal",
    type: "router",
    ip: "192.168.1.1",
    status: "online",
    location: "Rack A1",
    ports: 24,
    activeConnections: 18,
  },
  {
    id: "net-002",
    name: "Switch Core",
    type: "switch",
    ip: "192.168.1.2",
    status: "online",
    location: "Rack A2",
    ports: 48,
    activeConnections: 32,
  },
]

const mockAlerts: Alert[] = [
  {
    id: "alert-001",
    title: "Alto uso de memoria en VokaFlow-DB-03",
    description: "El servidor de base de datos está usando 91% de memoria RAM",
    severity: "warning",
    status: "active",
    source: "srv-003",
    timestamp: "2024-12-01 17:05:00",
    acknowledged: false,
  },
  {
    id: "alert-002",
    title: "Espacio en disco bajo en VokaFlow-DB-03",
    description: "El disco principal tiene solo 22% de espacio libre",
    severity: "critical",
    status: "active",
    source: "srv-003",
    timestamp: "2024-12-01 16:45:00",
    acknowledged: false,
  },
]

const mockLogs: LogEntry[] = [
  {
    id: "log-001",
    timestamp: "2024-12-01 17:07:15",
    level: "info",
    source: "VokaFlow API",
    message: "Usuario autenticado exitosamente: user@vokaflow.com",
    details: { userId: "usr-123", ip: "203.0.113.45" },
  },
  {
    id: "log-002",
    timestamp: "2024-12-01 17:06:58",
    level: "warning",
    source: "Vicky AI Core",
    message: "Tiempo de respuesta elevado en traducción: 2.3s",
    details: { language: "es-en", responseTime: "2.3s" },
  },
  {
    id: "log-003",
    timestamp: "2024-12-01 17:06:42",
    level: "error",
    source: "PostgreSQL",
    message: "Conexión perdida temporalmente con replica",
    details: { replica: "db-replica-02", duration: "15s" },
  },
]

// Función auxiliar para simular delay de red
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// Función auxiliar para manejar errores de fetch con fallback a mock
async function fetchWithErrorHandling<T>(url: string, options?: RequestInit, mockData?: T): Promise<T> {
  try {
    const response = await fetch(url, options)

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`)
    }

    return (await response.json()) as T
  } catch (error) {
    console.warn(`API no disponible para ${url}, usando datos mock:`, error)

    if (mockData) {
      await delay(500) // Simular delay de red
      return mockData
    }

    throw error
  }
}

// Servicios para servidores
export const serverService = {
  getServers: () => fetchWithErrorHandling<Server[]>(`${API_BASE_URL}/servers`, undefined, mockServers),
  getServerById: (id: string) => {
    const server = mockServers.find((s) => s.id === id)
    return fetchWithErrorHandling<Server>(`${API_BASE_URL}/servers/${id}`, undefined, server!)
  },
  getServerMetrics: (id: string) =>
    fetchWithErrorHandling<SystemMetrics[]>(`${API_BASE_URL}/servers/${id}/metrics`, undefined, []),
  restartServer: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/servers/${id}/restart`,
      {
        method: "POST",
      },
      { success: true },
    ),
  shutdownServer: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/servers/${id}/shutdown`,
      {
        method: "POST",
      },
      { success: true },
    ),
}

// Servicios para red
export const networkService = {
  getDevices: () =>
    fetchWithErrorHandling<NetworkDevice[]>(`${API_BASE_URL}/network/devices`, undefined, mockNetworkDevices),
  getConnections: () =>
    fetchWithErrorHandling<NetworkConnection[]>(`${API_BASE_URL}/network/connections`, undefined, []),
  getDeviceById: (id: string) => {
    const device = mockNetworkDevices.find((d) => d.id === id)
    return fetchWithErrorHandling<NetworkDevice>(`${API_BASE_URL}/network/devices/${id}`, undefined, device!)
  },
  getTopology: () =>
    fetchWithErrorHandling<{ devices: NetworkDevice[]; connections: NetworkConnection[] }>(
      `${API_BASE_URL}/network/topology`,
      undefined,
      { devices: mockNetworkDevices, connections: [] },
    ),
}

// Servicios para alertas
export const alertService = {
  getAlerts: () => fetchWithErrorHandling<Alert[]>(`${API_BASE_URL}/alerts`, undefined, mockAlerts),
  acknowledgeAlert: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/alerts/${id}/acknowledge`,
      {
        method: "POST",
      },
      { success: true },
    ),
  resolveAlert: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/alerts/${id}/resolve`,
      {
        method: "POST",
      },
      { success: true },
    ),
}

// Servicios para logs
export const logService = {
  getLogs: (limit = 100, level?: string) => {
    const params = new URLSearchParams()
    params.append("limit", limit.toString())
    if (level) params.append("level", level)

    let filteredLogs = mockLogs
    if (level && level !== "all") {
      filteredLogs = mockLogs.filter((log) => log.level === level)
    }

    return fetchWithErrorHandling<LogEntry[]>(
      `${API_BASE_URL}/logs?${params.toString()}`,
      undefined,
      filteredLogs.slice(0, limit),
    )
  },
  getLogsBySource: (source: string, limit = 100) => {
    const params = new URLSearchParams()
    params.append("limit", limit.toString())

    const filteredLogs = mockLogs.filter((log) => log.source === source)
    return fetchWithErrorHandling<LogEntry[]>(
      `${API_BASE_URL}/logs/source/${source}?${params.toString()}`,
      undefined,
      filteredLogs.slice(0, limit),
    )
  },
}

// Servicios para servicios del sistema
export const systemService = {
  getServices: () => fetchWithErrorHandling<Service[]>(`${API_BASE_URL}/services`, undefined, []),
  getServiceById: (id: string) =>
    fetchWithErrorHandling<Service>(`${API_BASE_URL}/services/${id}`, undefined, {} as Service),
  startService: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/services/${id}/start`,
      {
        method: "POST",
      },
      { success: true },
    ),
  stopService: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/services/${id}/stop`,
      {
        method: "POST",
      },
      { success: true },
    ),
  restartService: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/services/${id}/restart`,
      {
        method: "POST",
      },
      { success: true },
    ),
}

// Servicios para backups
export const backupService = {
  getBackups: () => fetchWithErrorHandling<Backup[]>(`${API_BASE_URL}/backups`, undefined, []),
  getBackupById: (id: string) =>
    fetchWithErrorHandling<Backup>(`${API_BASE_URL}/backups/${id}`, undefined, {} as Backup),
  startBackup: (config: Partial<Backup>) =>
    fetchWithErrorHandling<Backup>(
      `${API_BASE_URL}/backups/start`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(config),
      },
      {} as Backup,
    ),
  cancelBackup: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/backups/${id}/cancel`,
      {
        method: "POST",
      },
      { success: true },
    ),
}

// Servicios para clusters
export const clusterService = {
  getClusters: () => fetchWithErrorHandling<Cluster[]>(`${API_BASE_URL}/clusters`, undefined, []),
  getClusterById: (id: string) =>
    fetchWithErrorHandling<Cluster>(`${API_BASE_URL}/clusters/${id}`, undefined, {} as Cluster),
  failoverCluster: (id: string) =>
    fetchWithErrorHandling<{ success: boolean }>(
      `${API_BASE_URL}/clusters/${id}/failover`,
      {
        method: "POST",
      },
      { success: true },
    ),
}

// Servicio para métricas del sistema
export const metricsService = {
  getCurrentMetrics: () =>
    fetchWithErrorHandling<SystemMetrics>(`${API_BASE_URL}/metrics/current`, undefined, {} as SystemMetrics),
  getHistoricalMetrics: (hours = 24) =>
    fetchWithErrorHandling<SystemMetrics[]>(`${API_BASE_URL}/metrics/historical?hours=${hours}`, undefined, []),
}
