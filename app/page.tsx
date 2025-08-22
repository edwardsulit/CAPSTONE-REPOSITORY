import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { DashboardStats } from "@/components/dashboard-stats"
import { DashboardCharts } from "@/components/dashboard-charts"

export default function DashboardPage() {
  return (
    // MAIN LAYOUT CONTAINER - Full screen height with background
    <div className="flex h-screen bg-background">
      {/* LEFT SIDEBAR - Navigation menu (fixed width: 256px) */}
      <DashboardSidebar />

      {/* RIGHT CONTENT AREA - Header + Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* TOP HEADER - Search, language, notifications, user profile */}
        <DashboardHeader />

        {/* MAIN CONTENT AREA - Scrollable dashboard content */}
        <main className="flex-1 overflow-auto p-6">
          {/* PAGE HEADER - Home title and controls */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-foreground">Home</h1>
              <p className="text-sm text-muted-foreground">General Overview & Executive Dashboard</p>
            </div>
            <div className="flex items-center gap-2">
              <select className="px-3 py-1 text-sm border rounded-md bg-background">
                <option>Last 30 Days</option>
                <option>Last 7 Days</option>
                <option>Last 90 Days</option>
              </select>
              <button className="px-3 py-1 text-sm border rounded-md bg-background hover:bg-muted">Export</button>
            </div>
          </div>

          {/* DASHBOARD GRID LAYOUT - Updated for new design */}
          <div className="space-y-6">
            {/* TOP METRICS - Three key performance indicators */}
            <DashboardStats />

            {/* MAIN CHART SECTION - Recent Sales Trends with Real-time Alerts and Product Traffic */}
            <DashboardCharts />
          </div>
        </main>
      </div>
    </div>
  )
}
