"use client"

import { useState, useEffect } from "react"
import { Shield, AlertTriangle, CheckCircle, XCircle, Activity, Globe, Lock, Zap } from "lucide-react"
import { InternalNavCompact } from "@/components/ui/internal-nav-compact"

interface FirewallRule {
  id: number
  name: string
  source: string
  destination: string
  port: number
  protocol: string
  action: "allow" | "deny"
  status: "active" | "inactive"
}

const initialFirewallRules: FirewallRule[] = [
  {
    id: 1,
    name: "Allow SSH from trusted network",
    source: "192.168.1.0/24",
    destination: "Any",
    port: 22,
    protocol: "TCP",
    action: "allow",
    status: "active",
  },
  {
    id: 2,
    name: "Deny all traffic to database port",
    source: "Any",
    destination: "10.0.0.10",
    port: 5432,
    protocol: "TCP",
    action: "deny",
    status: "active",
  },
  {
    id: 3,
    name: "Allow HTTP traffic",
    source: "Any",
    destination: "Any",
    port: 80,
    protocol: "TCP",
    action: "allow",
    status: "active",
  },
  {
    id: 4,
    name: "Allow HTTPS traffic",
    source: "Any",
    destination: "Any",
    port: 443,
    protocol: "TCP",
    action: "allow",
    status: "active",
  },
  {
    id: 5,
    name: "Block suspicious IP",
    source: "203.0.113.45",
    destination: "Any",
    port: "Any",
    protocol: "Any",
    action: "deny",
    status: "active",
  },
]

export default function SeguridadFirewall() {
  const [firewallRules, setFirewallRules] = useState<FirewallRule[]>(initialFirewallRules)

  useEffect(() => {
    // Simulate fetching firewall rules from an API
    // In a real application, you would fetch data from an API endpoint here
    // For now, we're using the initialFirewallRules
  }, [])

  const navItems = [
    {
      title: "Overview",
      href: "/seguridad/firewall",
      icon: Shield,
    },
    {
      title: "Logs",
      href: "/seguridad/firewall/logs",
      icon: Activity,
    },
    {
      title: "Geo-IP Filtering",
      href: "/seguridad/firewall/geo-ip",
      icon: Globe,
    },
    {
      title: "Port Forwarding",
      href: "/seguridad/firewall/port-forwarding",
      icon: Zap,
    },
    {
      title: "Intrusion Detection",
      href: "/seguridad/firewall/intrusion-detection",
      icon: AlertTriangle,
    },
    {
      title: "Access Control",
      href: "/seguridad/firewall/access-control",
      icon: Lock,
    },
  ]

  return (
    <div>
      <InternalNavCompact items={navItems} />
      <div className="container mx-auto py-10">
        <h1 className="text-3xl font-semibold mb-5">Firewall Rules</h1>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 border-b">Name</th>
                <th className="py-2 px-4 border-b">Source</th>
                <th className="py-2 px-4 border-b">Destination</th>
                <th className="py-2 px-4 border-b">Port</th>
                <th className="py-2 px-4 border-b">Protocol</th>
                <th className="py-2 px-4 border-b">Action</th>
                <th className="py-2 px-4 border-b">Status</th>
              </tr>
            </thead>
            <tbody>
              {firewallRules.map((rule) => (
                <tr key={rule.id}>
                  <td className="py-2 px-4 border-b">{rule.name}</td>
                  <td className="py-2 px-4 border-b">{rule.source}</td>
                  <td className="py-2 px-4 border-b">{rule.destination}</td>
                  <td className="py-2 px-4 border-b">{rule.port}</td>
                  <td className="py-2 px-4 border-b">{rule.protocol}</td>
                  <td className="py-2 px-4 border-b">
                    {rule.action === "allow" ? (
                      <span className="text-green-500 flex items-center gap-1">
                        <CheckCircle className="h-4 w-4" />
                        Allow
                      </span>
                    ) : (
                      <span className="text-red-500 flex items-center gap-1">
                        <XCircle className="h-4 w-4" />
                        Deny
                      </span>
                    )}
                  </td>
                  <td className="py-2 px-4 border-b">{rule.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
