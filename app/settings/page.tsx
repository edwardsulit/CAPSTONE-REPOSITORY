import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

export default function SettingsPage() {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* SIDEBAR NAVIGATION */}
      <DashboardSidebar />

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* TOP HEADER */}
        <DashboardHeader />

        {/* MAIN SETTINGS CONTENT */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* PAGE HEADER */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
              <p className="text-sm text-gray-600 mt-1">System configuration and preferences</p>
            </div>
            <Button className="bg-primary hover:bg-primary/90">Save Changes</Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* ACCOUNT & SECURITY */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Account & Security</CardTitle>
                <p className="text-sm text-gray-600">Manage account credentials and security settings</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="current-password" className="text-sm font-medium text-gray-700">
                    Current Password
                  </Label>
                  <Input id="current-password" type="password" className="mt-1" />
                </div>
                <div>
                  <Label htmlFor="new-password" className="text-sm font-medium text-gray-700">
                    New Password
                  </Label>
                  <Input id="new-password" type="password" className="mt-1" />
                </div>
                <div>
                  <Label htmlFor="confirm-password" className="text-sm font-medium text-gray-700">
                    Confirm New Password
                  </Label>
                  <Input id="confirm-password" type="password" className="mt-1" />
                </div>
                <div className="flex items-center justify-between pt-2">
                  <Label htmlFor="session-timeout" className="text-sm font-medium text-gray-700">
                    Session Timeout
                  </Label>
                  <Select defaultValue="30min">
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="15min">15 minutes</SelectItem>
                      <SelectItem value="30min">30 minutes</SelectItem>
                      <SelectItem value="1hour">1 hour</SelectItem>
                      <SelectItem value="2hours">2 hours</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* NOTIFICATION SETTINGS */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Email Notifications</CardTitle>
                <p className="text-sm text-gray-600">Configure when to receive email alerts</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="admin-email" className="text-sm font-medium text-gray-700">
                    Admin Email Address
                  </Label>
                  <Input id="admin-email" type="email" defaultValue="admin@shield.com" className="mt-1" />
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="low-stock-alerts" className="text-sm font-medium text-gray-700">
                      Low Stock Alerts
                    </Label>
                    <Switch id="low-stock-alerts" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="system-maintenance" className="text-sm font-medium text-gray-700">
                      System Maintenance Notifications
                    </Label>
                    <Switch id="system-maintenance" defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="daily-reports" className="text-sm font-medium text-gray-700">
                      Daily Summary Reports
                    </Label>
                    <Switch id="daily-reports" />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="weekly-reports" className="text-sm font-medium text-gray-700">
                      Weekly Performance Reports
                    </Label>
                    <Switch id="weekly-reports" defaultChecked />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* INVENTORY SETTINGS */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Inventory Thresholds</CardTitle>
                <p className="text-sm text-gray-600">Set default stock level warnings</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="low-stock-threshold" className="text-sm font-medium text-gray-700">
                    Low Stock Threshold (%)
                  </Label>
                  <Input id="low-stock-threshold" type="number" defaultValue="20" className="mt-1" />
                  <p className="text-xs text-gray-500 mt-1">Alert when stock falls below this percentage</p>
                </div>
                <div>
                  <Label htmlFor="critical-stock-threshold" className="text-sm font-medium text-gray-700">
                    Critical Stock Threshold (%)
                  </Label>
                  <Input id="critical-stock-threshold" type="number" defaultValue="5" className="mt-1" />
                  <p className="text-xs text-gray-500 mt-1">Urgent alert when stock falls below this percentage</p>
                </div>
                <div>
                  <Label htmlFor="expiry-warning" className="text-sm font-medium text-gray-700">
                    Expiry Warning (Days)
                  </Label>
                  <Input id="expiry-warning" type="number" defaultValue="30" className="mt-1" />
                  <p className="text-xs text-gray-500 mt-1">Alert when products expire within this many days</p>
                </div>
              </CardContent>
            </Card>

            {/* BRANCH MANAGEMENT */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Branch Locations</CardTitle>
                <p className="text-sm text-gray-600">Manage branch settings and locations</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Main Branch</p>
                      <p className="text-sm text-gray-600">123 Main Street, Manila</p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">North Branch</p>
                      <p className="text-sm text-gray-600">456 North Ave, Quezon City</p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">South Branch</p>
                      <p className="text-sm text-gray-600">789 South Road, Makati</p>
                    </div>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>
                </div>
                <Button variant="outline" className="w-full bg-transparent">
                  + Add New Branch
                </Button>
              </CardContent>
            </Card>

            {/* DATA MANAGEMENT */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Data Management</CardTitle>
                <p className="text-sm text-gray-600">Backup, export, and audit trail settings</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Automatic Backup</Label>
                    <p className="text-xs text-gray-500">Daily system backup at 2:00 AM</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-sm font-medium text-gray-700">Audit Trail Logging</Label>
                    <p className="text-xs text-gray-500">Track all system activities and changes</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div>
                  <Label htmlFor="audit-retention" className="text-sm font-medium text-gray-700">
                    Audit Log Retention
                  </Label>
                  <Select defaultValue="1year">
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3months">3 months</SelectItem>
                      <SelectItem value="6months">6 months</SelectItem>
                      <SelectItem value="1year">1 year</SelectItem>
                      <SelectItem value="2years">2 years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="pt-2 space-y-2">
                  <Button variant="outline" className="w-full bg-transparent">
                    Export All Data
                  </Button>
                  <Button variant="outline" className="w-full bg-transparent">
                    Download Backup
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* INTEGRATION SETTINGS */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Integration Settings</CardTitle>
                <p className="text-sm text-gray-600">Configure external service connections</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Power BI</p>
                    <p className="text-sm text-gray-600">Connected - Dashboard analytics</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <Button variant="outline" size="sm">
                      Configure
                    </Button>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Email Service</p>
                    <p className="text-sm text-gray-600">SMTP configuration for notifications</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <Button variant="outline" size="sm">
                      Configure
                    </Button>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">API Access</p>
                    <p className="text-sm text-gray-600">External system integrations</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <Button variant="outline" size="sm">
                      Setup
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
