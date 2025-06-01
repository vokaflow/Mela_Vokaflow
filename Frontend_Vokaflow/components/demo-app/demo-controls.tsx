"use client"

import { useState } from "react"
import type { DemoConfig } from "@/types/demo-app"

interface DemoControlsProps {
  config: DemoConfig
  onConfigChange: (config: DemoConfig) => void
  onRunTest: (testType: string) => void
  onRunScenario: (scenario: string) => void
}

export function DemoControls({ config, onConfigChange, onRunTest, onRunScenario }: DemoControlsProps) {
  // Estado local para tracking de cambios
  const [localConfig, setLocalConfig] = useState<DemoConfig>(config)

  // Manejar cambios en la configuración
  const handleConfigChange = (key: keyof DemoConfig, value: any) => {
    const newConfig = { ...localConfig, [key]: value }
    setLocalConfig(newConfig)
    onConfigChange(newConfig)
  }

  // Manejar cambios en toggles
  const handleToggleChange = (key: keyof DemoConfig) => {
    const newValue = !localConfig[key]
    handleConfigChange(key, newValue)
  }

  return (
    <div className="flex flex-col h-full space-y-4 p-4 bg-voka-blue-black rounded-lg border border-voka-border">
      {/* Tests Rápidos */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-3">🎯 TEST RÁPIDOS</h3>
        <div className="grid grid-cols-1 gap-2">
          <button
            onClick={() => onRunTest("chat")}
            className="bg-voka-blue-black text-voka-white py-2 px-4 rounded-md hover:bg-voka-blue transition-colors"
          >
            💬 Chat Test
          </button>
          <button
            onClick={() => onRunTest("voice")}
            className="bg-voka-blue-black text-voka-white py-2 px-4 rounded-md hover:bg-voka-blue transition-colors"
          >
            🗣️ Voice Test
          </button>
          <button
            onClick={() => onRunTest("ocr")}
            className="bg-voka-blue-black text-voka-white py-2 px-4 rounded-md hover:bg-voka-blue transition-colors"
          >
            📷 OCR Test
          </button>
          <button
            onClick={() => onRunTest("auto")}
            className="bg-voka-blue-black text-voka-white py-2 px-4 rounded-md hover:bg-voka-blue transition-colors"
          >
            🔄 Auto Demo
          </button>
          <button
            onClick={() => onRunTest("stress")}
            className="bg-voka-blue-black text-voka-white py-2 px-4 rounded-md hover:bg-voka-blue transition-colors"
          >
            📊 Stress Test
          </button>
        </div>
      </div>

      {/* Configuración */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-3">⚙️ CONFIGURACIÓN</h3>
        <div className="space-y-3">
          {/* Idioma Demo */}
          <div>
            <label className="text-sm text-voka-gray block mb-1">Idioma Demo:</label>
            <select
              value={localConfig.language}
              onChange={(e) => handleConfigChange("language", e.target.value)}
              className="w-full bg-voka-blue-black text-voka-white rounded-md px-3 py-1 focus:outline-none focus:ring-1 focus:ring-voka-magenta"
            >
              <option value="es">Español</option>
              <option value="en">English</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
            </select>
          </div>

          {/* Velocidad */}
          <div>
            <label className="text-sm text-voka-gray block mb-1">Velocidad:</label>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="0.5"
                max="4"
                step="0.5"
                value={localConfig.speed}
                onChange={(e) => handleConfigChange("speed", Number.parseFloat(e.target.value))}
                className="flex-1"
              />
              <span className="text-voka-white">{localConfig.speed}x</span>
            </div>
          </div>

          {/* Auto-scroll */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-voka-gray">Auto-scroll:</span>
            <button
              onClick={() => handleToggleChange("autoScroll")}
              className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors ${
                localConfig.autoScroll ? "bg-voka-magenta" : "bg-voka-border"
              }`}
            >
              <span
                className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${
                  localConfig.autoScroll ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          {/* Sonidos */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-voka-gray">Sonidos:</span>
            <button
              onClick={() => handleToggleChange("sounds")}
              className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors ${
                localConfig.sounds ? "bg-voka-magenta" : "bg-voka-border"
              }`}
            >
              <span
                className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${
                  localConfig.sounds ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          {/* Debug */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-voka-gray">Debug:</span>
            <button
              onClick={() => handleToggleChange("debug")}
              className={`relative inline-flex items-center h-6 rounded-full w-11 transition-colors ${
                localConfig.debug ? "bg-voka-magenta" : "bg-voka-border"
              }`}
            >
              <span
                className={`inline-block w-4 h-4 transform bg-white rounded-full transition-transform ${
                  localConfig.debug ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Scenarios */}
      <div className="bg-voka-dark p-3 rounded-lg">
        <h3 className="text-lg font-bold text-voka-white font-montserrat mb-3">📝 SCENARIOS</h3>
        <div className="space-y-2">
          <div className="flex items-center">
            <input
              type="radio"
              id="scenario-casual"
              name="scenario"
              checked={localConfig.scenario === "casual"}
              onChange={() => handleConfigChange("scenario", "casual")}
              className="mr-2"
            />
            <label htmlFor="scenario-casual" className="text-voka-white">
              Chat Casual
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="radio"
              id="scenario-business"
              name="scenario"
              checked={localConfig.scenario === "business"}
              onChange={() => handleConfigChange("scenario", "business")}
              className="mr-2"
            />
            <label htmlFor="scenario-business" className="text-voka-white">
              Business Call
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="radio"
              id="scenario-emergency"
              name="scenario"
              checked={localConfig.scenario === "emergency"}
              onChange={() => handleConfigChange("scenario", "emergency")}
              className="mr-2"
            />
            <label htmlFor="scenario-emergency" className="text-voka-white">
              Emergency
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="radio"
              id="scenario-technical"
              name="scenario"
              checked={localConfig.scenario === "technical"}
              onChange={() => handleConfigChange("scenario", "technical")}
              className="mr-2"
            />
            <label htmlFor="scenario-technical" className="text-voka-white">
              Technical
            </label>
          </div>

          <div className="flex items-center">
            <input
              type="radio"
              id="scenario-custom"
              name="scenario"
              checked={localConfig.scenario === "custom"}
              onChange={() => handleConfigChange("scenario", "custom")}
              className="mr-2"
            />
            <label htmlFor="scenario-custom" className="text-voka-white">
              Custom
            </label>
          </div>

          <button
            onClick={() => onRunScenario(localConfig.scenario)}
            className="w-full mt-2 bg-voka-magenta text-white py-2 px-4 rounded-md hover:bg-opacity-80 transition-colors"
          >
            ▶️ Ejecutar Scenario
          </button>
        </div>
      </div>
    </div>
  )
}
