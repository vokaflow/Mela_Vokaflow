"use client"

import { useState } from "react"
import type { LucideIcon } from "lucide-react"

interface NavItem {
  id: string
  label: string
  icon: LucideIcon
  color?: string
  badge?: string | number
}

interface InternalNavProps {
  items: NavItem[]
  activeTab: string
  onTabChange: (tabId: string) => void
  className?: string
}

export function InternalNav({ items, activeTab, onTabChange, className = "" }: InternalNavProps) {
  const [hoveredTab, setHoveredTab] = useState<string | null>(null)

  return (
    <div className={`flex flex-wrap gap-3 ${className}`}>
      {items.map((item) => {
        const isActive = activeTab === item.id
        const isHovered = hoveredTab === item.id

        return (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            onMouseEnter={() => setHoveredTab(item.id)}
            onMouseLeave={() => setHoveredTab(null)}
            className={`
              relative flex items-center gap-3 px-4 py-3 rounded-lg font-montserrat font-medium 
              transition-all duration-200 ease-out min-w-[140px]
              ${
                isActive
                  ? "bg-gradient-to-r from-voka-magenta to-voka-blue text-white shadow-lg"
                  : "bg-voka-blue-black border border-voka-border text-voka-gray hover:text-white hover:border-voka-magenta/50"
              }
            `}
          >
            {/* Icon */}
            <item.icon
              className={`
                h-5 w-5 flex-shrink-0 transition-colors duration-200
                ${isActive ? "text-white" : isHovered ? "text-voka-magenta" : "text-voka-gray"}
              `}
            />

            {/* Label */}
            <div className="flex-1 text-left">
              <div
                className={`
                  text-sm font-semibold leading-tight transition-colors duration-200
                  ${isActive ? "text-white" : ""}
                `}
              >
                {item.label}
              </div>
            </div>

            {/* Badge */}
            {item.badge && (
              <div
                className={`
                  px-2 py-1 rounded-full text-xs font-bold transition-all duration-200
                  ${isActive ? "bg-white/20 text-white" : "bg-voka-magenta/20 text-voka-magenta"}
                `}
              >
                {item.badge}
              </div>
            )}
          </button>
        )
      })}
    </div>
  )
}
