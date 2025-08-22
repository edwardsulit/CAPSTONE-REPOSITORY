import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function DashboardCharts() {
  return (
    <div className="space-y-6">
      {/* RECENT SALES TRENDS - Power BI Chart Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Sales Trends</CardTitle>
            <p className="text-sm text-muted-foreground">Weekly/monthly performance summary</p>
          </div>
          <div className="flex space-x-2">
            <button className="px-3 py-1 text-xs bg-teal-500 text-white rounded">Weekly</button>
            <button className="px-3 py-1 text-xs bg-muted text-muted-foreground rounded">Monthly</button>
          </div>
        </CardHeader>
        <CardContent>
          {/* POWER BI EMBED LOCATION - Replace this div with Power BI iframe */}
          <div className="w-full h-[300px] bg-muted rounded-lg flex items-center justify-center border-2 border-dashed border-muted-foreground/20">
            <div className="text-center">
              <span className="text-lg font-medium text-muted-foreground">Power BI Chart Placeholder</span>
              <p className="text-sm text-muted-foreground mt-2">Recent Sales Trends - Bar Chart with Trend Line</p>
            </div>
            {/* TO REPLACE: This entire div with Power BI embed */}
          </div>
        </CardContent>
      </Card>

      {/* BOTTOM SECTION - Real-time Alerts & Product Traffic */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* REAL-TIME ALERTS - Left side */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Real-time Alerts</CardTitle>
            <span className="bg-red-500 text-white text-xs px-2 py-1 rounded">3 New</span>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">System monitoring & anomaly detection</p>
            <div className="space-y-3">
              {/* ALERT ITEMS */}
              <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Item out of stock</p>
                  <p className="text-xs text-muted-foreground">15 minutes ago</p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Unusual Traffic Pattern</p>
                  <p className="text-xs text-muted-foreground">Traffic spike detected on product page</p>
                  <p className="text-xs text-muted-foreground">48 minutes ago</p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="font-medium text-sm">Inventory Alert</p>
                  <p className="text-xs text-muted-foreground">Product ID P002 is running low (5 units left)</p>
                  <p className="text-xs text-muted-foreground">2 hours ago</p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-gray-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="font-medium text-sm">System Update Complete</p>
                  <p className="text-xs text-muted-foreground">Version 2.4.1 deployed successfully</p>
                  <p className="text-xs text-muted-foreground">5 hours ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* PRODUCT TRAFFIC - Right side */}
        <Card>
          <CardHeader>
            <CardTitle>Product Traffic</CardTitle>
            <p className="text-sm text-muted-foreground">Most viewed or accessed items</p>
          </CardHeader>
          <CardContent>
            {/* TRAFFIC HEAT MAP */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground mb-2">
                <span>Low Traffic</span>
                <span>High Traffic</span>
              </div>

              {/* HEAT MAP GRID */}
              <div className="grid grid-cols-4 gap-2">
                <div className="bg-teal-800 text-white p-3 rounded text-center text-xs font-medium">
                  Prescription Medicine
                </div>
                <div className="bg-teal-600 text-white p-3 rounded text-center text-xs font-medium">Canned Goods</div>
                <div className="bg-teal-500 text-white p-3 rounded text-center text-xs font-medium">Soap</div>
                <div className="bg-teal-400 text-white p-3 rounded text-center text-xs font-medium">Shampoo</div>

                <div className="bg-teal-600 text-white p-3 rounded text-center text-xs font-medium">
                  Over-The-Counter Medicine
                </div>
                <div className="bg-teal-300 text-white p-3 rounded text-center text-xs font-medium">Chips</div>
                <div className="bg-teal-200 text-teal-800 p-3 rounded text-center text-xs font-medium">Candy</div>
                <div className="bg-teal-100 text-teal-800 p-3 rounded text-center text-xs font-medium">-</div>

                <div className="bg-teal-400 text-white p-3 rounded text-center text-xs font-medium">Water</div>
                <div className="bg-teal-300 text-white p-3 rounded text-center text-xs font-medium">Soda</div>
                <div className="bg-teal-100 text-teal-800 p-3 rounded text-center text-xs font-medium">-</div>
                <div className="bg-teal-100 text-teal-800 p-3 rounded text-center text-xs font-medium">-</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
