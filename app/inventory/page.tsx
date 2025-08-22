import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Search, Filter, ChevronLeft, ChevronRight, Eye, AlertTriangle, Package } from "lucide-react"

export default function InventoryPage() {
  return (
    <div className="flex h-screen bg-background">
      {/* SIDEBAR NAVIGATION */}
      <DashboardSidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* HEADER */}
        <DashboardHeader />

        {/* MAIN CONTENT */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* PAGE HEADER */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-foreground">Inventory</h1>
              <p className="text-sm text-muted-foreground">Live Stock Monitoring & Allocation Logic</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm">
                All Locations
              </Button>
              <Button variant="outline" size="sm">
                Export
              </Button>
            </div>
          </div>

          {/* KEY METRICS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Total Products */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Products</p>
                    <p className="text-2xl font-bold text-foreground">1,248</p>
                    <p className="text-xs text-muted-foreground mt-1">Across 5 locations</p>
                  </div>
                  <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>

            {/* Low Stock Items */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Low Stock Items</p>
                    <p className="text-2xl font-bold text-foreground">42</p>
                    <p className="text-xs text-orange-600 mt-1">-8 since yesterday</p>
                  </div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>

            {/* Out of Stock */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Out of Stock</p>
                    <p className="text-2xl font-bold text-foreground">18</p>
                    <p className="text-xs text-red-600 mt-1">+3 since yesterday</p>
                  </div>
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>

            {/* Expiring Soon */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Expiring Soon</p>
                    <p className="text-2xl font-bold text-foreground">24</p>
                    <p className="text-xs text-muted-foreground mt-1">Within next 30 days</p>
                  </div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* INVENTORY STATUS TABLE */}
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Inventory Status</CardTitle>
                  <p className="text-sm text-muted-foreground">Quantity, threshold values, and expiry dates</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Search className="w-4 h-4 mr-2" />
                    Search
                  </Button>
                  <Button variant="outline" size="sm">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Product ID</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Product Name</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Quantity</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Threshold</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Expiry Date</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Status</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Movement</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="py-3 px-4">INV-1001</td>
                      <td className="py-3 px-4">Acetaminophen 500mg</td>
                      <td className="py-3 px-4">250</td>
                      <td className="py-3 px-4">100</td>
                      <td className="py-3 px-4">Dec 15, 2025</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          In Stock
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">Fast</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 px-4">INV-1002</td>
                      <td className="py-3 px-4">Ibuprofen 200mg</td>
                      <td className="py-3 px-4">45</td>
                      <td className="py-3 px-4">50</td>
                      <td className="py-3 px-4">Aug 30, 2025</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                          Low Stock
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">Fast</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-orange-600 hover:bg-orange-700">
                          Reorder
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 px-4">INV-1003</td>
                      <td className="py-3 px-4">Amoxicillin 250mg</td>
                      <td className="py-3 px-4">0</td>
                      <td className="py-3 px-4">30</td>
                      <td className="py-3 px-4">-</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-red-100 text-red-800">
                          Out of Stock
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">Fast</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-orange-600 hover:bg-orange-700">
                          Reorder
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 px-4">INV-1004</td>
                      <td className="py-3 px-4">Loratadine 10mg</td>
                      <td className="py-3 px-4">120</td>
                      <td className="py-3 px-4">40</td>
                      <td className="py-3 px-4">Mar 15, 2026</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          In Stock
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">Moderate</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-3 px-4">INV-1005</td>
                      <td className="py-3 px-4">Cetirizine 5mg</td>
                      <td className="py-3 px-4">85</td>
                      <td className="py-3 px-4">30</td>
                      <td className="py-3 px-4">Jun 10, 2023</td>
                      <td className="py-3 px-4">
                        <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                          Expiring Soon
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">Slow</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Discount
                        </Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-muted-foreground">Showing 5 of 1,248 items</p>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <ChevronLeft className="w-4 h-4 mr-1" />
                    Previous
                  </Button>
                  <Button size="sm" className="bg-orange-600 hover:bg-orange-700">
                    Next
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* BOTTOM SECTION */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* INVENTORY CLUSTERING */}
            <Card>
              <CardHeader>
                <CardTitle>Inventory Clustering</CardTitle>
                <p className="text-sm text-muted-foreground">Segmentation and stocking logic</p>
              </CardHeader>
              <CardContent>
                {/* POWER BI PLACEHOLDER FOR DONUT CHART */}
                <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-6">
                  <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Inventory Clustering Chart</h3>
                  <p className="text-sm text-gray-600 mb-4">Power BI donut chart will be embedded here</p>
                  <div className="text-xs text-gray-500">
                    <p>Fast-Moving: 485 (39%)</p>
                    <p>Moderate: 512 (41%)</p>
                    <p>Slow-Moving: 251 (20%)</p>
                  </div>
                </div>

                {/* CLUSTERING INSIGHTS */}
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full mt-1.5"></div>
                    <div>
                      <p className="font-medium text-sm">Fast-Moving Items</p>
                      <p className="text-xs text-muted-foreground">
                        Maintain higher safety stock (30-40% above threshold) and set up auto-reorder.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-3 h-3 bg-gray-400 rounded-full mt-1.5"></div>
                    <div>
                      <p className="font-medium text-sm">Moderate Items</p>
                      <p className="text-xs text-muted-foreground">
                        Standard safety stock (15-20% above threshold) with regular review cycles.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full mt-1.5"></div>
                    <div>
                      <p className="font-medium text-sm">Slow-Moving Items</p>
                      <p className="text-xs text-muted-foreground">
                        Minimal safety stock (5-10% above threshold) and consider discount strategies.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ALLOCATION SUGGESTIONS */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Allocation Suggestions</CardTitle>
                    <p className="text-sm text-muted-foreground">Reallocation between branches</p>
                  </div>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    5 New
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Ibuprofen Transfer */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Ibuprofen 400mg</h4>
                      <Badge variant="outline" className="text-blue-600 border-blue-600">
                        High Priority
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                      <div>
                        <p className="text-muted-foreground">Source Location</p>
                        <p className="font-medium">Bacnotan</p>
                        <p className="text-xs text-muted-foreground">Current Stock: 120 units</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Destination Location</p>
                        <p className="font-medium">Westside Branch</p>
                        <p className="text-xs text-muted-foreground">Current Stock: 5 units (Low)</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm">
                        <span className="font-medium">Suggested Transfer:</span> 30 units
                      </p>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          Ignore
                        </Button>
                        <Button size="sm" className="bg-orange-600 hover:bg-orange-700">
                          Transfer
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Acetaminophen Transfer */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Acetaminophen 500mg</h4>
                      <Badge variant="outline" className="text-yellow-600 border-yellow-600">
                        Medium Priority
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                      <div>
                        <p className="text-muted-foreground">Source Location</p>
                        <p className="font-medium">Balaoang</p>
                        <p className="text-xs text-muted-foreground">Current Stock: 200 units</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Destination Location</p>
                        <p className="font-medium">Eastside Branch</p>
                        <p className="text-xs text-muted-foreground">Current Stock: 25 units (Low)</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm">
                        <span className="font-medium">Suggested Transfer:</span> 50 units
                      </p>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          Ignore
                        </Button>
                        <Button size="sm" className="bg-orange-600 hover:bg-orange-700">
                          Transfer
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Cetirizine Transfer */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Cetirizine 5mg</h4>
                      <Badge variant="outline" className="text-purple-600 border-purple-600">
                        Expiring Soon
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                      <div>
                        <p className="text-muted-foreground">Source Location</p>
                        <p className="font-medium">Bauang</p>
                        <p className="text-xs text-muted-foreground">Current Stock: 85 units (Expires: Jun 10, 2023)</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Destination Location</p>
                        <p className="font-medium">High-Traffic Locations</p>
                        <p className="text-xs text-muted-foreground">To accelerate sales before expiry</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-sm">
                        <span className="font-medium">Suggested Transfer:</span> All units
                      </p>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          Ignore
                        </Button>
                        <Button size="sm" className="bg-orange-600 hover:bg-orange-700">
                          Transfer
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* SUBSTITUTION RECOMMENDATIONS */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Substitution Recommendations</CardTitle>
                  <p className="text-sm text-muted-foreground">Alternative medications for out-of-stock items</p>
                </div>
                <Badge variant="outline" className="text-purple-600 border-purple-600">
                  Bonus Feature
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {/* Amoxicillin Substitutions */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <h4 className="font-medium">Amoxicillin 250mg</h4>
                  </div>
                  <p className="text-xs text-red-600 mb-4">Out of Stock</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <p className="text-sm">Amoxicillin 500mg (half dose)</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <p className="text-sm">Ampicillin 250mg</p>
                    </div>
                  </div>
                  <Button className="w-full bg-orange-600 hover:bg-orange-700" size="sm">
                    View Details
                  </Button>
                </div>

                {/* Lisinopril Substitutions */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <h4 className="font-medium">Lisinopril 10mg</h4>
                  </div>
                  <p className="text-xs text-red-600 mb-4">Out of Stock</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <p className="text-sm">Enalapril 5mg</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <p className="text-sm">Ramipril 5mg</p>
                    </div>
                  </div>
                  <Button className="w-full bg-orange-600 hover:bg-orange-700" size="sm">
                    View Details
                  </Button>
                </div>

                {/* Metformin Substitutions */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <h4 className="font-medium">Metformin 500mg</h4>
                  </div>
                  <p className="text-xs text-red-600 mb-4">Out of Stock</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <p className="text-sm">Metformin 250mg (double dose)</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                      <p className="text-sm">Gliclazide 80mg (different class)</p>
                    </div>
                  </div>
                  <Button className="w-full bg-orange-600 hover:bg-orange-700" size="sm">
                    View Details
                  </Button>
                </div>
              </div>

              {/* Substitution Guidelines */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <AlertTriangle className="w-3 h-3 text-white" />
                  </div>
                  <div>
                    <h4 className="font-medium text-blue-900 mb-1">Substitution Guidelines</h4>
                    <p className="text-sm text-blue-800">
                      All substitutions are based on therapeutic equivalence and should be verified by a pharmacist
                      before dispensing. Green indicators show direct alternatives, while amber indicates different drug
                      classes with similar therapeutic effects.
                    </p>
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
