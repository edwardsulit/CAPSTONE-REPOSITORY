import { Card, CardContent } from "@/components/ui/card"

export function DashboardStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* OVERALL SUCCESS RATE - Green indicator */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <div>
              <p className="text-sm text-muted-foreground">Overall Success Rate</p>
              <p className="text-2xl font-bold">98.7%</p>
              <p className="text-xs text-green-600">+0.5% from previous period</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FAILED TRANSACTIONS - Red indicator */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div>
              <p className="text-sm text-muted-foreground">Failed Transactions</p>
              <p className="text-2xl font-bold">42</p>
              <p className="text-xs text-red-600">-8% from previous period</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* SYSTEM UPTIME - Blue indicator */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <div>
              <p className="text-sm text-muted-foreground">System Uptime</p>
              <p className="text-2xl font-bold">99.99%</p>
              <p className="text-xs text-muted-foreground">Last outage: 14 days ago</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
