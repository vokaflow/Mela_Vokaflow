"use client"

import { TrendingUp, DollarSign, PieChart, BarChart, CreditCard, Target } from "lucide-react"
import { SectionTabs } from "../ui/section-tabs"

// Componentes placeholder para cada pestaña
const FinancialOverview = () => (
  <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
    <p className="text-voka-white font-montserrat">Financial Overview - Resumen financiero</p>
  </div>
)

const RevenueAnalysis = () => (
  <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
    <p className="text-voka-white font-montserrat">Revenue Analysis - Análisis de ingresos</p>
  </div>
)

const ExpenseTracking = () => (
  <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
    <p className="text-voka-white font-montserrat">Expense Tracking - Seguimiento de gastos</p>
  </div>
)

const ProfitMargins = () => (
  <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
    <p className="text-voka-white font-montserrat">Profit Margins - Márgenes de ganancia</p>
  </div>
)

const PaymentSystems = () => (
  <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
    <p className="text-voka-white font-montserrat">Payment Systems - Sistemas de pago</p>
  </div>
)

const BusinessGoals = () => (
  <div className="bg-voka-blue-black border border-voka-border rounded-lg p-6">
    <p className="text-voka-white font-montserrat">Business Goals - Objetivos de negocio</p>
  </div>
)

const estadoEconomicoTabs = [
  {
    id: "overview",
    label: "Resumen",
    icon: TrendingUp,
    component: <FinancialOverview />,
  },
  {
    id: "revenue",
    label: "Ingresos",
    icon: DollarSign,
    badge: "+12%",
    component: <RevenueAnalysis />,
  },
  {
    id: "expenses",
    label: "Gastos",
    icon: PieChart,
    component: <ExpenseTracking />,
  },
  {
    id: "profits",
    label: "Ganancias",
    icon: BarChart,
    badge: "23%",
    component: <ProfitMargins />,
  },
  {
    id: "payments",
    label: "Pagos",
    icon: CreditCard,
    component: <PaymentSystems />,
  },
  {
    id: "goals",
    label: "Objetivos",
    icon: Target,
    badge: "8/12",
    component: <BusinessGoals />,
  },
]

export function EstadoEconomicoMain() {
  return (
    <SectionTabs
      title="📈 ECONOMIC CONTROL"
      subtitle="Analíticas Financieras e Inteligencia de Negocio"
      tabs={estadoEconomicoTabs}
      defaultTab="overview"
    />
  )
}
