import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function SalesPage() {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* SIDEBAR NAVIGATION */}
      <DashboardSidebar />

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* TOP HEADER */}
        <DashboardHeader />

        {/* MAIN DASHBOARD CONTENT */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* PAGE HEADER */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Sales Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">Sales Trends, Forecasting & Product Performance</p>
            </div>
            <div className="flex items-center gap-3">
              <Select defaultValue="30days">
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="30days">Last 30 Days</SelectItem>
                  <SelectItem value="90days">Last 90 Days</SelectItem>
                  <SelectItem value="1year">Last Year</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                Export
              </Button>
            </div>
          </div>

          {/* FILTERS */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Branch:</span>
              <Select defaultValue="all-branches">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-branches">All Branches</SelectItem>
                  <SelectItem value="north">North Branch</SelectItem>
                  <SelectItem value="south">South Branch</SelectItem>
                  <SelectItem value="east">East Branch</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Product Type:</span>
              <Select defaultValue="all-products">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all-products">All Products</SelectItem>
                  <SelectItem value="electronics">Electronics</SelectItem>
                  <SelectItem value="clothing">Clothing</SelectItem>
                  <SelectItem value="home">Home & Garden</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* KEY METRICS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Total Revenue */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Revenue</CardTitle>
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">$684,200</div>
                <p className="text-xs text-green-600 mt-1">+12.5% from previous period</p>
              </CardContent>
            </Card>

            {/* Total Profit */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Profit</CardTitle>
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">$245,800</div>
                <p className="text-xs text-green-600 mt-1">+8.2% from previous period</p>
              </CardContent>
            </Card>

            {/* Total Sales */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Sales</CardTitle>
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">4,328</div>
                <p className="text-xs text-green-600 mt-1">+5.3% from previous period</p>
              </CardContent>
            </Card>

            {/* Conversion Rate */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Conversion Rate</CardTitle>
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">3.2%</div>
                <p className="text-xs text-red-600 mt-1">-0.8% from previous period</p>
              </CardContent>
            </Card>
          </div>

          {/* TAB NAVIGATION */}
          <div className="flex items-center gap-6 mb-6 border-b border-gray-200">
            <button className="pb-3 px-1 border-b-2 border-primary text-primary font-medium text-sm">
              Sales Trends
            </button>
            <button className="pb-3 px-1 text-gray-500 hover:text-gray-700 font-medium text-sm">
              Best-selling Products
            </button>
            <button className="pb-3 px-1 text-gray-500 hover:text-gray-700 font-medium text-sm">Sales Forecast</button>
          </div>

          {/* REVENUE & PROFIT TRENDS CHART */}
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-gray-900">Revenue & Profit Trends</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">Track revenue and profit performance over time</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="bg-primary text-white">
                    Line
                  </Button>
                  <Button variant="outline" size="sm">
                    Bar
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* POWER BI CHART PLACEHOLDER */}
              <div className="h-80 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="text-gray-400 mb-2">
                    <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>
                  <p className="text-gray-600 font-medium">Power BI Chart Placeholder</p>
                  <p className="text-sm text-gray-500 mt-1">Revenue & Profit Trends Chart</p>
                  <p className="text-xs text-gray-400 mt-2">Replace this div with your Power BI embed code</p>
                </div>
              </div>

              {/* INSIGHTS SECTION */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-3">Insights</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-700">Highest revenue month: December ($95,000)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <span className="text-gray-700">Seasonal spike in Q4 (Oct-Dec)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    <span className="text-gray-700">Summer slump in July ($40,000)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-700">Average profit margin: 35.9%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}
