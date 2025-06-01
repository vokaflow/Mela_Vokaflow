import type {
  FirewallRule,
  SecurityThreat,
  SecurityLog,
  RateLimitRule,
  SecurityMetrics,
  IntrusionAlert,
  BackupStatus,
  SecurityConfig,
} from "@/types/security"

class SecurityService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

  // Firewall Management
  async getFirewallStatus(): Promise<{ enabled: boolean; rules_count: number; threats_blocked: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/firewall/status`)
      if (!response.ok) throw new Error("Failed to fetch firewall status")
      return await response.json()
    } catch (error) {
      console.error("Error fetching firewall status:", error)
      // Fallback to mock data
      return {
        enabled: true,
        rules_count: 1247,
        threats_blocked: 15689,
      }
    }
  }

  async getFirewallRules(): Promise<FirewallRule[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/firewall/rules`)
      if (!response.ok) throw new Error("Failed to fetch firewall rules")
      return await response.json()
    } catch (error) {
      console.error("Error fetching firewall rules:", error)
      // Fallback to mock data
      return this.getMockFirewallRules()
    }
  }

  async createFirewallRule(
    rule: Omit<FirewallRule, "id" | "created_at" | "last_modified" | "hit_count">,
  ): Promise<FirewallRule> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/firewall/rules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rule),
      })
      if (!response.ok) throw new Error("Failed to create firewall rule")
      return await response.json()
    } catch (error) {
      console.error("Error creating firewall rule:", error)
      throw error
    }
  }

  async updateFirewallRule(id: string, rule: Partial<FirewallRule>): Promise<FirewallRule> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/firewall/rules/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rule),
      })
      if (!response.ok) throw new Error("Failed to update firewall rule")
      return await response.json()
    } catch (error) {
      console.error("Error updating firewall rule:", error)
      throw error
    }
  }

  async deleteFirewallRule(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/firewall/rules/${id}`, {
        method: "DELETE",
      })
      if (!response.ok) throw new Error("Failed to delete firewall rule")
    } catch (error) {
      console.error("Error deleting firewall rule:", error)
      throw error
    }
  }

  // Security Logs
  async getSecurityLogs(limit = 100, level?: string): Promise<SecurityLog[]> {
    try {
      const params = new URLSearchParams({ limit: limit.toString() })
      if (level) params.append("level", level)

      const response = await fetch(`${this.baseUrl}/api/security/logs?${params}`)
      if (!response.ok) throw new Error("Failed to fetch security logs")
      return await response.json()
    } catch (error) {
      console.error("Error fetching security logs:", error)
      return this.getMockSecurityLogs()
    }
  }

  // Threat Management
  async getThreats(): Promise<SecurityThreat[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/threats`)
      if (!response.ok) throw new Error("Failed to fetch threats")
      return await response.json()
    } catch (error) {
      console.error("Error fetching threats:", error)
      return this.getMockThreats()
    }
  }

  async blockIP(ip: string, reason: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/threats/${ip}/block`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason }),
      })
      if (!response.ok) throw new Error("Failed to block IP")
    } catch (error) {
      console.error("Error blocking IP:", error)
      throw error
    }
  }

  // Intrusion Detection
  async getIntrusionAlerts(): Promise<IntrusionAlert[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/intrusion/alerts`)
      if (!response.ok) throw new Error("Failed to fetch intrusion alerts")
      return await response.json()
    } catch (error) {
      console.error("Error fetching intrusion alerts:", error)
      return this.getMockIntrusionAlerts()
    }
  }

  async updateIntrusionConfig(config: Partial<SecurityConfig>): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/intrusion/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      })
      if (!response.ok) throw new Error("Failed to update intrusion config")
    } catch (error) {
      console.error("Error updating intrusion config:", error)
      throw error
    }
  }

  // Rate Limiting
  async getRateLimitStatus(): Promise<{ enabled: boolean; rules_count: number; blocked_requests: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/ratelimit/status`)
      if (!response.ok) throw new Error("Failed to fetch rate limit status")
      return await response.json()
    } catch (error) {
      console.error("Error fetching rate limit status:", error)
      return {
        enabled: true,
        rules_count: 45,
        blocked_requests: 2847,
      }
    }
  }

  async getRateLimitRules(): Promise<RateLimitRule[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/ratelimit/rules`)
      if (!response.ok) throw new Error("Failed to fetch rate limit rules")
      return await response.json()
    } catch (error) {
      console.error("Error fetching rate limit rules:", error)
      return this.getMockRateLimitRules()
    }
  }

  async updateRateLimitRules(rules: RateLimitRule[]): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/ratelimit/rules`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rules),
      })
      if (!response.ok) throw new Error("Failed to update rate limit rules")
    } catch (error) {
      console.error("Error updating rate limit rules:", error)
      throw error
    }
  }

  // Backup Management
  async getBackupStatus(): Promise<BackupStatus[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/backup/status`)
      if (!response.ok) throw new Error("Failed to fetch backup status")
      return await response.json()
    } catch (error) {
      console.error("Error fetching backup status:", error)
      return this.getMockBackupStatus()
    }
  }

  async createBackup(type: "full" | "incremental" | "differential"): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/backup/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type }),
      })
      if (!response.ok) throw new Error("Failed to create backup")
    } catch (error) {
      console.error("Error creating backup:", error)
      throw error
    }
  }

  // Security Metrics
  async getSecurityMetrics(): Promise<SecurityMetrics> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/metrics`)
      if (!response.ok) throw new Error("Failed to fetch security metrics")
      return await response.json()
    } catch (error) {
      console.error("Error fetching security metrics:", error)
      return this.getMockSecurityMetrics()
    }
  }

  // Emergency Actions
  async activateFortressMode(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/fortress/activate`, {
        method: "POST",
      })
      if (!response.ok) throw new Error("Failed to activate fortress mode")
    } catch (error) {
      console.error("Error activating fortress mode:", error)
      throw error
    }
  }

  async emergencyLockdown(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/security/emergency/lockdown`, {
        method: "POST",
      })
      if (!response.ok) throw new Error("Failed to activate emergency lockdown")
    } catch (error) {
      console.error("Error activating emergency lockdown:", error)
      throw error
    }
  }

  // Mock Data Methods
  private getMockFirewallRules(): FirewallRule[] {
    return [
      {
        id: "1",
        name: "Block Suspicious IPs",
        action: "deny",
        protocol: "tcp",
        source_ip: "192.168.1.0/24",
        destination_port: "22",
        enabled: true,
        priority: 1,
        created_at: "2025-01-30T10:00:00Z",
        last_modified: "2025-01-30T10:00:00Z",
        hit_count: 1247,
      },
      {
        id: "2",
        name: "Allow HTTP Traffic",
        action: "allow",
        protocol: "tcp",
        destination_port: "80,443",
        enabled: true,
        priority: 2,
        created_at: "2025-01-30T10:00:00Z",
        last_modified: "2025-01-30T10:00:00Z",
        hit_count: 45892,
      },
      {
        id: "3",
        name: "Block DDoS Attempts",
        action: "reject",
        protocol: "any",
        source_ip: "203.45.67.0/24",
        enabled: true,
        priority: 0,
        created_at: "2025-01-30T09:30:00Z",
        last_modified: "2025-01-30T11:15:00Z",
        hit_count: 8934,
      },
    ]
  }

  private getMockSecurityLogs(): SecurityLog[] {
    const logs: SecurityLog[] = []
    const sources = ["firewall", "intrusion_detection", "rate_limiter", "auth", "system"] as const
    const levels = ["info", "warning", "error", "critical"] as const
    const actions = [
      "Blocked suspicious IP",
      "Rate limit exceeded",
      "Failed login attempt",
      "Intrusion detected",
      "Firewall rule triggered",
      "Authentication successful",
      "System backup completed",
    ]

    for (let i = 0; i < 50; i++) {
      const timestamp = new Date(Date.now() - i * 60000).toISOString()
      logs.push({
        id: `log_${i}`,
        timestamp,
        level: levels[Math.floor(Math.random() * levels.length)],
        source: sources[Math.floor(Math.random() * sources.length)],
        ip_address: `192.168.1.${Math.floor(Math.random() * 255)}`,
        action: actions[Math.floor(Math.random() * actions.length)],
        details: `Security event detected at ${timestamp}`,
        blocked: Math.random() > 0.3,
      })
    }

    return logs
  }

  private getMockThreats(): SecurityThreat[] {
    return [
      {
        id: "1",
        ip_address: "203.45.67.89",
        country: "China",
        city: "Beijing",
        threat_type: "brute_force",
        severity: "high",
        attempts: 127,
        first_seen: "2025-01-30T08:00:00Z",
        last_seen: "2025-01-30T11:45:00Z",
        blocked: true,
        user_agent: "Mozilla/5.0 (compatible; scanner)",
        endpoint: "/api/auth/login",
        description: "Multiple failed login attempts detected",
      },
      {
        id: "2",
        ip_address: "45.123.89.45",
        country: "Russia",
        city: "Moscow",
        threat_type: "ddos",
        severity: "critical",
        attempts: 5847,
        first_seen: "2025-01-30T10:30:00Z",
        last_seen: "2025-01-30T11:50:00Z",
        blocked: true,
        description: "DDoS attack pattern detected",
      },
      {
        id: "3",
        ip_address: "78.234.156.78",
        country: "Unknown",
        city: "Unknown",
        threat_type: "suspicious",
        severity: "medium",
        attempts: 23,
        first_seen: "2025-01-30T11:00:00Z",
        last_seen: "2025-01-30T11:30:00Z",
        blocked: false,
        endpoint: "/api/admin",
        description: "Suspicious access pattern to admin endpoints",
      },
    ]
  }

  private getMockIntrusionAlerts(): IntrusionAlert[] {
    return [
      {
        id: "1",
        timestamp: "2025-01-30T11:45:00Z",
        ip_address: "203.45.67.89",
        country: "China",
        attack_type: "SQL Injection Attempt",
        severity: "high",
        details: "Malicious SQL payload detected in request parameters",
        actions_taken: ["Blocked IP", "Logged incident", "Notified admin"],
        status: "resolved",
      },
      {
        id: "2",
        timestamp: "2025-01-30T11:30:00Z",
        ip_address: "45.123.89.45",
        country: "Russia",
        attack_type: "Port Scanning",
        severity: "medium",
        details: "Systematic port scanning detected from this IP",
        actions_taken: ["Rate limited", "Monitoring increased"],
        status: "investigating",
      },
    ]
  }

  private getMockRateLimitRules(): RateLimitRule[] {
    return [
      {
        id: "1",
        endpoint: "/api/auth/login",
        method: "POST",
        limit: 5,
        window_seconds: 300,
        current_usage: 3,
        enabled: true,
        whitelist_ips: ["192.168.1.100"],
        created_at: "2025-01-30T10:00:00Z",
      },
      {
        id: "2",
        endpoint: "/api/vicky/process",
        method: "POST",
        limit: 100,
        window_seconds: 3600,
        current_usage: 67,
        enabled: true,
        whitelist_ips: [],
        created_at: "2025-01-30T10:00:00Z",
      },
      {
        id: "3",
        endpoint: "/api/translate",
        method: "POST",
        limit: 1000,
        window_seconds: 3600,
        current_usage: 234,
        enabled: true,
        whitelist_ips: ["192.168.1.0/24"],
        created_at: "2025-01-30T10:00:00Z",
      },
    ]
  }

  private getMockBackupStatus(): BackupStatus[] {
    return [
      {
        id: "1",
        type: "full",
        status: "completed",
        start_time: "2025-01-30T02:00:00Z",
        end_time: "2025-01-30T02:45:00Z",
        size_mb: 2048,
        files_count: 15847,
        encryption_enabled: true,
        integrity_verified: true,
        location: "/backups/full_20250130_020000.tar.gz",
      },
      {
        id: "2",
        type: "incremental",
        status: "running",
        start_time: "2025-01-30T11:00:00Z",
        size_mb: 156,
        files_count: 234,
        encryption_enabled: true,
        integrity_verified: false,
        location: "/backups/inc_20250130_110000.tar.gz",
      },
    ]
  }

  private getMockSecurityMetrics(): SecurityMetrics {
    return {
      threats_blocked_today: 1247,
      active_connections: 456,
      firewall_cpu_usage: 23,
      firewall_memory_usage: 45,
      active_rules: 1247,
      blacklisted_ips: 15689,
      rate_limit_hits: 2847,
      intrusion_attempts: 89,
      backup_status: "healthy",
      last_backup: "2025-01-30T02:45:00Z",
    }
  }
}

export const securityService = new SecurityService()
