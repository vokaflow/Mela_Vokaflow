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

interface InternalNavCompactProps {
  items: NavItem[]
  activeTab: string
  onTabChange: (tabId: string) => void
  className?: string
  columns?: number
}

export function InternalNavCompact({
  items,
  activeTab,
  onTabChange,
  className = "",
  columns = 3,
}: InternalNavCompactProps) {
  const [hoveredTab, setHoveredTab] = useState<string | null>(null)

  return (
    <div className={`grid gap-3 ${className}`} style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
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
              relative flex flex-col items-center gap-2 p-4 rounded-lg font-montserrat 
              transition-all duration-200 ease-out min-h-[80px] group
              ${
                isActive
                  ? "bg-gradient-to-br from-voka-magenta to-voka-blue text-white shadow-lg"
                  : "bg-voka-blue-black border border-voka-border text-voka-gray hover:text-white hover:border-voka-magenta/50"
              }
            `}
          >
            {/* Icon */}
            <div className="relative">
              <item.icon
                className={`
                  h-6 w-6 transition-all duration-200
                  ${
                    isActive
                      ? "text-white"
                      : isHovered
                        ? "text-voka-magenta"
                        : "text-voka-gray group-hover:text-voka-magenta"
                  }
                `}
              />

              {/* Badge positioned on icon */}
              {item.badge && (
                <div
                  className={`
                    absolute -top-2 -right-2 px-1.5 py-0.5 rounded-full text-xs font-bold
                    transition-all duration-200 min-w-[20px] text-center
                    ${isActive ? "bg-white/20 text-white" : "bg-voka-magenta text-white"}
                  `}
                >
                  {item.badge}
                </div>
              )}
            </div>

            {/* Label - centered, two lines if needed */}
            <div className="text-center">
              <div
                className={`
                  text-sm font-medium leading-tight transition-colors duration-200
                  ${isActive ? "text-white" : ""}
                `}
              >
                {item.label}
              </div>
            </div>
          </button>
        )
      })}
    </div>
  )
}
