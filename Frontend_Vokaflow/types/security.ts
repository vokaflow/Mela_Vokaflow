export interface FirewallRule {
  id: string
  name: string
  action: "allow" | "deny" | "reject"
  protocol: "tcp" | "udp" | "icmp" | "any"
  source_ip?: string
  destination_ip?: string
  source_port?: string
  destination_port?: string
  enabled: boolean
  priority: number
  created_at: string
  last_modified: string
  hit_count: number
}

export interface SecurityThreat {
  id: string
  ip_address: string
  country: string
  city: string
  threat_type: "brute_force" | "ddos" | "malware" | "suspicious" | "intrusion"
  severity: "low" | "medium" | "high" | "critical"
  attempts: number
  first_seen: string
  last_seen: string
  blocked: boolean
  user_agent?: string
  endpoint?: string
  description: string
}

export interface SecurityLog {
  id: string
  timestamp: string
  level: "info" | "warning" | "error" | "critical"
  source: "firewall" | "intrusion_detection" | "rate_limiter" | "auth" | "system"
  ip_address?: string
  user_id?: string
  action: string
  details: string
  blocked: boolean
}

export interface RateLimitRule {
  id: string
  endpoint: string
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | "ALL"
  limit: number
  window_seconds: number
  current_usage: number
  enabled: boolean
  whitelist_ips: string[]
  created_at: string
}

export interface SecurityMetrics {
  threats_blocked_today: number
  active_connections: number
  firewall_cpu_usage: number
  firewall_memory_usage: number
  active_rules: number
  blacklisted_ips: number
  rate_limit_hits: number
  intrusion_attempts: number
  backup_status: "healthy" | "warning" | "error"
  last_backup: string
}

export interface IntrusionAlert {
  id: string
  timestamp: string
  ip_address: string
  country: string
  attack_type: string
  severity: "low" | "medium" | "high" | "critical"
  details: string
  actions_taken: string[]
  status: "active" | "resolved" | "investigating"
}

export interface BackupStatus {
  id: string
  type: "full" | "incremental" | "differential"
  status: "running" | "completed" | "failed" | "scheduled"
  start_time: string
  end_time?: string
  size_mb: number
  files_count: number
  encryption_enabled: boolean
  integrity_verified: boolean
  location: string
}

export interface SecurityConfig {
  firewall_enabled: boolean
  intrusion_detection_enabled: boolean
  rate_limiting_enabled: boolean
  auto_block_enabled: boolean
  geo_blocking_enabled: boolean
  honeypot_enabled: boolean
  backup_encryption: boolean
  alert_email: string
  alert_slack_webhook?: string
  fortress_mode: boolean
  detection_sensitivity: "low" | "medium" | "high" | "paranoid"
}
