import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { FileText, Download, TrendingUp, Package } from "lucide-react"

export default function ReportsPage() {
  return (
    <div className="flex h-screen bg-background">
      {/* SIDEBAR NAVIGATION */}
      <DashboardSidebar />

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* TOP HEADER */}
        <DashboardHeader />

        {/* MAIN DASHBOARD CONTENT */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* CUSTOM FILTERS SECTION */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">Custom Filters</h2>
              <Button variant="ghost" className="text-primary hover:text-primary/80">
                Reset All
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm text-muted-foreground mb-2 block">Branch</label>
                <Select defaultValue="all-branches">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all-branches">All Branches</SelectItem>
                    <SelectItem value="main">Main Branch</SelectItem>
                    <SelectItem value="north">North Branch</SelectItem>
                    <SelectItem value="south">South Branch</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-muted-foreground mb-2 block">Product Category</label>
                <Select defaultValue="all-categories">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all-categories">All Categories</SelectItem>
                    <SelectItem value="beverages">Beverages</SelectItem>
                    <SelectItem value="pharmaceuticals">Pharmaceuticals</SelectItem>
                    <SelectItem value="food">Food Items</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-muted-foreground mb-2 block">Time Period</label>
                <Select defaultValue="december-2022">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="december-2022">December 2022</SelectItem>
                    <SelectItem value="november-2022">November 2022</SelectItem>
                    <SelectItem value="october-2022">October 2022</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-muted-foreground mb-2 block">Report Type</label>
                <Select defaultValue="all-reports">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all-reports">All Reports</SelectItem>
                    <SelectItem value="sales">Sales Reports</SelectItem>
                    <SelectItem value="inventory">Inventory Reports</SelectItem>
                    <SelectItem value="forecast">Forecast Reports</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* MAIN REPORTS GRID */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* MONTHLY SALES REPORT */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-medium">Monthly Sales Report</CardTitle>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted"></div>
                    <div className="w-2 h-2 rounded-full bg-muted"></div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">December 2022</p>
              </CardHeader>
              <CardContent>
                {/* POWER BI PLACEHOLDER FOR BAR CHART */}
                <div className="h-32 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg flex items-center justify-center mb-4 border-2 border-dashed border-blue-200">
                  <div className="text-center">
                    <TrendingUp className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                    <p className="text-sm text-blue-600 font-medium">Power BI Sales Chart</p>
                    <p className="text-xs text-blue-500">Monthly sales bar chart will be embedded here</p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Total Sales</span>
                    <span className="text-sm font-medium">₱416,514.78</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Total Profit</span>
                    <span className="text-sm font-medium">₱84,765.09</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Top Product</span>
                    <span className="text-sm font-medium">WILKINS PURE 500ML</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                  <span>Last updated: Today</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                      PDF
                    </Button>
                    <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                      Excel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* INVENTORY OPTIMIZATION */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-medium">Inventory Optimization</CardTitle>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted"></div>
                    <div className="w-2 h-2 rounded-full bg-muted"></div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">Allocation Model Results</p>
              </CardHeader>
              <CardContent>
                {/* POWER BI PLACEHOLDER FOR CIRCULAR CHART */}
                <div className="h-32 bg-gradient-to-r from-teal-50 to-teal-100 rounded-lg flex items-center justify-center mb-4 border-2 border-dashed border-teal-200">
                  <div className="text-center">
                    <Package className="h-8 w-8 text-teal-500 mx-auto mb-2" />
                    <p className="text-sm text-teal-600 font-medium">Power BI Optimization Chart</p>
                    <p className="text-xs text-teal-500">20% stock reduction circular chart</p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Stock Reduction</span>
                    <span className="text-sm font-medium">20% (₱31,515)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Stockout Incidents</span>
                    <span className="text-sm font-medium text-green-600">-15% (3 total)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Turnover Improvement</span>
                    <span className="text-sm font-medium text-green-600">+12% (3.8 turns)</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                  <span>Last updated: Today</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                      PDF
                    </Button>
                    <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                      Excel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* FORECAST ACCURACY */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-medium">Forecast Accuracy</CardTitle>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted"></div>
                    <div className="w-2 h-2 rounded-full bg-muted"></div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">Model Performance Metrics</p>
              </CardHeader>
              <CardContent>
                {/* POWER BI PLACEHOLDER FOR LINE CHART */}
                <div className="h-32 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg flex items-center justify-center mb-4 border-2 border-dashed border-purple-200">
                  <div className="text-center">
                    <TrendingUp className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                    <p className="text-sm text-purple-600 font-medium">Power BI Forecast Chart</p>
                    <p className="text-xs text-purple-500">Forecast vs actual line chart</p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">MAPE</span>
                    <span className="text-sm font-medium">14.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">RMSE</span>
                    <span className="text-sm font-medium">32 units</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Bias</span>
                    <span className="text-sm font-medium text-red-600">-3.5% (Underforecast)</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                  <span>Last updated: Today</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                      PDF
                    </Button>
                    <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                      Excel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* EXCEPTION LOGS SECTION */}
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold">Exception Logs</CardTitle>
                  <p className="text-sm text-muted-foreground">Detected Anomalies & Data Validation</p>
                </div>
                <div className="text-sm text-muted-foreground">December 2022</div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-sm text-muted-foreground">Date & Time</th>
                      <th className="text-left py-3 px-4 font-medium text-sm text-muted-foreground">Exception Type</th>
                      <th className="text-left py-3 px-4 font-medium text-sm text-muted-foreground">Description</th>
                      <th className="text-left py-3 px-4 font-medium text-sm text-muted-foreground">Product</th>
                      <th className="text-left py-3 px-4 font-medium text-sm text-muted-foreground">Severity</th>
                      <th className="text-left py-3 px-4 font-medium text-sm text-muted-foreground">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="py-3 px-4 text-sm">Dec 15, 2022 09:42 AM</td>
                      <td className="py-3 px-4 text-sm">Data Inconsistency</td>
                      <td className="py-3 px-4 text-sm">Inventory count mismatch between systems</td>
                      <td className="py-3 px-4 text-sm">WILKINS PURE 500ML</td>
                      <td className="py-3 px-4">
                        <Badge variant="destructive" className="text-xs">
                          High
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-800">
                          In Progress
                        </Badge>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 px-4 text-sm">Dec 12, 2022 02:18 PM</td>
                      <td className="py-3 px-4 text-sm">Sales Spike</td>
                      <td className="py-3 px-4 text-sm">Unusual sales volume for COCA-COLA 1.5L</td>
                      <td className="py-3 px-4 text-sm">COCA-COLA 1.5L</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="text-xs bg-orange-100 text-orange-800">
                          Medium
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                          Resolved
                        </Badge>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 px-4 text-sm">Dec 10, 2022 11:05 AM</td>
                      <td className="py-3 px-4 text-sm">Forecast Deviation</td>
                      <td className="py-3 px-4 text-sm">Actual sales 35% below forecast for Beverages</td>
                      <td className="py-3 px-4 text-sm">Multiple</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="text-xs bg-orange-100 text-orange-800">
                          Medium
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                          Resolved
                        </Badge>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* AVAILABLE REPORTS SECTION */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold">Available Reports</CardTitle>
                  <p className="text-sm text-muted-foreground">Downloadable Reports (PDF, Excel)</p>
                </div>
                <Button variant="outline" size="sm">
                  <FileText className="h-4 w-4 mr-2" />
                  Search Reports
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* MONTHLY SALES REPORT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileText className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm mb-1">Monthly Sales Report</h4>
                      <p className="text-xs text-muted-foreground mb-2">June 2023</p>
                      <p className="text-xs text-muted-foreground mb-3">
                        Comprehensive sales analysis by product, category, and location
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Generated: Jul 2, 2023</span>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <FileText className="h-3 w-3 mr-1" />
                            PDF
                          </Button>
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <Download className="h-3 w-3 mr-1" />
                            Excel
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* QUARTERLY SALES REPORT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <FileText className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm mb-1">Quarterly Sales Report</h4>
                      <p className="text-xs text-muted-foreground mb-2">Q2 2023</p>
                      <p className="text-xs text-muted-foreground mb-3">
                        Strategic overview with YoY comparisons and trend analysis
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Generated: Jul 5, 2023</span>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <FileText className="h-3 w-3 mr-1" />
                            PDF
                          </Button>
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <Download className="h-3 w-3 mr-1" />
                            Excel
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* INVENTORY STATUS REPORT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                      <Package className="h-5 w-5 text-orange-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm mb-1">Inventory Status Report</h4>
                      <p className="text-xs text-muted-foreground mb-2">As of Jul 10, 2023</p>
                      <p className="text-xs text-muted-foreground mb-3">
                        Complete inventory snapshot with aging and valuation analysis
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Generated: Jul 10, 2023</span>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <FileText className="h-3 w-3 mr-1" />
                            PDF
                          </Button>
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <Download className="h-3 w-3 mr-1" />
                            Excel
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* FORECAST ACCURACY REPORT */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <TrendingUp className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-sm mb-1">Forecast Accuracy Report</h4>
                      <p className="text-xs text-muted-foreground mb-2">Q2 2023 Review</p>
                      <p className="text-xs text-muted-foreground mb-3">
                        Detailed analysis of forecast performance with error metrics
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Generated: Jul 7, 2023</span>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <FileText className="h-3 w-3 mr-1" />
                            PDF
                          </Button>
                          <Button variant="outline" size="sm" className="h-6 px-2 text-xs bg-transparent">
                            <Download className="h-3 w-3 mr-1" />
                            Excel
                          </Button>
                        </div>
                      </div>
                    </div>
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
