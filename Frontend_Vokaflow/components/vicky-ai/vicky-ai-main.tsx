"use client"

import { Brain, Activity, Settings, History, GraduationCap, FlaskConical } from "lucide-react"
import { SectionTabs } from "../ui/section-tabs"
import { VickyStatus } from "./vicky-status"
import { VickyCore } from "./vicky-core"
import { VickyPersonality } from "./vicky-personality"
import { VickyHistory } from "./vicky-history"
import { VickyLearning } from "./vicky-learning"
import { VickyExperimental } from "./vicky-experimental"

const vickyTabs = [
  {
    id: "status",
    label: "Estado",
    icon: Activity,
    component: <VickyStatus />,
  },
  {
    id: "core",
    label: "Núcleo",
    icon: Brain,
    component: <VickyCore />,
  },
  {
    id: "personality",
    label: "Personalidad",
    icon: Settings,
    component: <VickyPersonality />,
  },
  {
    id: "history",
    label: "Historial",
    icon: History,
    badge: "247",
    component: <VickyHistory />,
  },
  {
    id: "learning",
    label: "Aprendizaje",
    icon: GraduationCap,
    badge: "73%",
    component: <VickyLearning />,
  },
  {
    id: "experimental",
    label: "Experimental",
    icon: FlaskConical,
    badge: "NEW",
    component: <VickyExperimental />,
  },
]

export function VickyAIMain() {
  return (
    <SectionTabs
      title="🧠 VICKY AI CONTROL"
      subtitle="Gestión Avanzada de Redes Neuronales"
      tabs={vickyTabs}
      defaultTab="status"
    />
  )
}
