"use client"

import { useState, type ReactNode } from "react"
import type { LucideIcon } from "lucide-react"
import { InternalNavCompact } from "./internal-nav-compact"

interface TabItem {
  id: string
  label: string
  icon: LucideIcon
  color?: string
  badge?: string | number
  component: ReactNode
}

interface SectionTabsProps {
  title: string
  subtitle: string
  tabs: TabItem[]
  defaultTab?: string
  className?: string
  navColumns?: number
}

export function SectionTabs({ title, subtitle, tabs, defaultTab, className = "", navColumns = 3 }: SectionTabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || "")

  const activeTabData = tabs.find((tab) => tab.id === activeTab)

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-voka-white font-montserrat bg-gradient-to-r from-voka-magenta to-voka-blue bg-clip-text text-transparent">
          {title}
        </h1>
        <p className="text-xl text-voka-gray font-montserrat">{subtitle}</p>
      </div>

      {/* Navigation */}
      <InternalNavCompact items={tabs} activeTab={activeTab} onTabChange={setActiveTab} columns={navColumns} />

      {/* Content Area */}
      <div className="min-h-[600px]">{activeTabData?.component}</div>
    </div>
  )
}
