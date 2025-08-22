"use client"

import { useState } from "react"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function PurchasesPage() {
  const [selectedCategory, setSelectedCategory] = useState("")
  const [selectedScenario, setSelectedScenario] = useState("")
  const [increaseFactor, setIncreaseFactor] = useState("")
  const [duration, setDuration] = useState("")

  return (
    <div className="flex h-screen bg-gray-50">
      {/* SIDEBAR NAVIGATION */}
      <DashboardSidebar />

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* HEADER */}
        <DashboardHeader />

        {/* MAIN DASHBOARD CONTENT */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
          {/* PAGE TITLE */}
          <div className="mb-6">
            <h1 className="text-2xl font-semibold text-gray-900">Purchases</h1>
            <p className="text-sm text-gray-600">Inventory Management & Procurement Analytics</p>
          </div>

          {/* TOP METRICS CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Items to Reorder */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Items to Reorder</p>
                    <p className="text-2xl font-bold text-gray-900">24</p>
                    <p className="text-xs text-red-600 mt-1">5 items below safety stock</p>
                  </div>
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>

            {/* Pending Orders */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Pending Orders</p>
                    <p className="text-2xl font-bold text-gray-900">18</p>
                    <p className="text-xs text-blue-600 mt-1">$42,850 total value</p>
                  </div>
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>

            {/* Avg Lead Time */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Avg Lead Time</p>
                    <p className="text-2xl font-bold text-gray-900">14.2 days</p>
                    <p className="text-xs text-green-600 mt-1">-2.3 days from last month</p>
                  </div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>

            {/* Slow-Moving Items */}
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Slow-Moving Items</p>
                    <p className="text-2xl font-bold text-gray-900">32</p>
                    <p className="text-xs text-purple-600 mt-1">12 with discount opportunities</p>
                  </div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* REORDER POINT & EOQ TABLE */}
          <Card className="mb-8">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Reorder Point (ROP) & EOQ Table</CardTitle>
                <p className="text-sm text-gray-600 mt-1">Shows what, when, and how much to reorder</p>
              </div>
              <Button variant="outline" size="sm">
                Filter
              </Button>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Product ID</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Product Name</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Current Stock</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Reorder Point</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">EOQ</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Lead Time</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Status</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">PRD-1234</td>
                      <td className="py-3 px-4">Biogesic</td>
                      <td className="py-3 px-4">12</td>
                      <td className="py-3 px-4">20</td>
                      <td className="py-3 px-4">50</td>
                      <td className="py-3 px-4">14 days</td>
                      <td className="py-3 px-4">
                        <Badge variant="destructive">Reorder Now</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Order
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">PRD-2345</td>
                      <td className="py-3 px-4">Cefuroxime</td>
                      <td className="py-3 px-4">8</td>
                      <td className="py-3 px-4">15</td>
                      <td className="py-3 px-4">30</td>
                      <td className="py-3 px-4">7 days</td>
                      <td className="py-3 px-4">
                        <Badge variant="destructive">Reorder Now</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Order
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">PRD-3456</td>
                      <td className="py-3 px-4">Bioflu</td>
                      <td className="py-3 px-4">22</td>
                      <td className="py-3 px-4">20</td>
                      <td className="py-3 px-4">40</td>
                      <td className="py-3 px-4">10 days</td>
                      <td className="py-3 px-4">
                        <Badge className="bg-yellow-100 text-yellow-800">Approaching ROP</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" variant="outline">
                          Plan
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">PRD-4567</td>
                      <td className="py-3 px-4">Amoxicillin</td>
                      <td className="py-3 px-4">45</td>
                      <td className="py-3 px-4">25</td>
                      <td className="py-3 px-4">50</td>
                      <td className="py-3 px-4">12 days</td>
                      <td className="py-3 px-4">
                        <Badge className="bg-green-100 text-green-800">In Stock</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" variant="outline">
                          Plan
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">PRD-5678</td>
                      <td className="py-3 px-4">Cetirizine</td>
                      <td className="py-3 px-4">120</td>
                      <td className="py-3 px-4">50</td>
                      <td className="py-3 px-4">100</td>
                      <td className="py-3 px-4">5 days</td>
                      <td className="py-3 px-4">
                        <Badge className="bg-green-100 text-green-800">In Stock</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <Button size="sm" variant="outline">
                          Plan
                        </Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-600">Showing 5 of 24 items</p>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    Previous
                  </Button>
                  <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* BOTTOM SECTION - What-If Scenario & Supplier Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* What-If Scenario Tester */}
            <Card>
              <CardHeader>
                <CardTitle>What-If Scenario Tester</CardTitle>
                <p className="text-sm text-gray-600">Simulate demand spikes, supply delays</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Product Category</label>
                    <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                      <SelectTrigger>
                        <SelectValue placeholder="Electronics" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="electronics">Electronics</SelectItem>
                        <SelectItem value="pharmaceuticals">Pharmaceuticals</SelectItem>
                        <SelectItem value="medical">Medical Devices</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Scenario Type</label>
                    <Select value={selectedScenario} onValueChange={setSelectedScenario}>
                      <SelectTrigger>
                        <SelectValue placeholder="Demand Spike" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="demand-spike">Demand Spike</SelectItem>
                        <SelectItem value="supply-delay">Supply Delay</SelectItem>
                        <SelectItem value="price-change">Price Change</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Increase Factor</label>
                    <Select value={increaseFactor} onValueChange={setIncreaseFactor}>
                      <SelectTrigger>
                        <SelectValue placeholder="150%" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="125">125%</SelectItem>
                        <SelectItem value="150">150%</SelectItem>
                        <SelectItem value="200">200%</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 mb-2 block">Duration</label>
                    <Select value={duration} onValueChange={setDuration}>
                      <SelectTrigger>
                        <SelectValue placeholder="2 weeks" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1-week">1 week</SelectItem>
                        <SelectItem value="2-weeks">2 weeks</SelectItem>
                        <SelectItem value="1-month">1 month</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button className="w-full bg-purple-600 hover:bg-purple-700">Run Simulation</Button>

                {/* Simulation Results */}
                <div className="mt-6 space-y-3">
                  <h4 className="font-medium text-gray-900">Simulation Results</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Additional units needed:</span>
                      <span className="font-medium">125 units</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Estimated stockout risk:</span>
                      <span className="font-medium text-red-600">High (85%)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Recommended safety stock:</span>
                      <span className="font-medium">+40 units</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Additional cost:</span>
                      <span className="font-medium">$12,500</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Supplier Lead Time Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Supplier Lead Time Summary</CardTitle>
                <p className="text-sm text-gray-600">Basis for ROP & safety stock planning</p>
              </CardHeader>
              <CardContent>
                {/* PLACEHOLDER FOR POWER BI CHART */}
                <div className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-6">
                  <div className="text-gray-500 mb-2">📊 Power BI Chart Placeholder</div>
                  <div className="text-sm text-gray-400">Supplier Lead Time Bar Chart</div>
                  <div className="text-xs text-gray-400 mt-1">Replace this div with Power BI embed</div>
                </div>

                {/* Supplier Performance Table */}
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Supplier 1</span>
                    <div className="flex items-center gap-4">
                      <span>18 days</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: "85%" }}></div>
                      </div>
                      <span className="text-green-600 font-medium">85%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Supplier 2</span>
                    <div className="flex items-center gap-4">
                      <span>12 days</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: "92%" }}></div>
                      </div>
                      <span className="text-green-600 font-medium">92%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Supplier 3</span>
                    <div className="flex items-center gap-4">
                      <span>24 days</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-yellow-500 h-2 rounded-full" style={{ width: "78%" }}></div>
                      </div>
                      <span className="text-yellow-600 font-medium">78%</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Supplier 4</span>
                    <div className="flex items-center gap-4">
                      <span>6 days</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-500 h-2 rounded-full" style={{ width: "95%" }}></div>
                      </div>
                      <span className="text-green-600 font-medium">95%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* DISCOUNT OPTIMIZATION PANEL */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Discount Optimization Panel</CardTitle>
                <p className="text-sm text-gray-600 mt-1">Suggests promos for slow-moving stock</p>
              </div>
              <Button variant="outline" size="sm">
                Sort by Value
              </Button>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Product</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Current Stock</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Days in Stock</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Value</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Suggested Discount</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Projected Savings</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">Biogesic</td>
                      <td className="py-3 px-4">45</td>
                      <td className="py-3 px-4">120</td>
                      <td className="py-3 px-4">$4,500</td>
                      <td className="py-3 px-4">25%</td>
                      <td className="py-3 px-4">$1,125</td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Apply
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">Cefuroxime</td>
                      <td className="py-3 px-4">32</td>
                      <td className="py-3 px-4">90</td>
                      <td className="py-3 px-4">$1,280</td>
                      <td className="py-3 px-4">15%</td>
                      <td className="py-3 px-4">$192</td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Apply
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">Bioflu</td>
                      <td className="py-3 px-4">28</td>
                      <td className="py-3 px-4">75</td>
                      <td className="py-3 px-4">$840</td>
                      <td className="py-3 px-4">20%</td>
                      <td className="py-3 px-4">$168</td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Apply
                        </Button>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="py-3 px-4">Amoxicillin</td>
                      <td className="py-3 px-4">65</td>
                      <td className="py-3 px-4">110</td>
                      <td className="py-3 px-4">$650</td>
                      <td className="py-3 px-4">30%</td>
                      <td className="py-3 px-4">$195</td>
                      <td className="py-3 px-4">
                        <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                          Apply
                        </Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Optimization Insight */}
              <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <div>
                    <h4 className="font-medium text-purple-900 mb-1">Optimization Insight</h4>
                    <p className="text-sm text-purple-800">
                      Applying all suggested discounts could free up $7,680 in inventory value and increase turnover
                      rate by 22% for slow-moving items.
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
