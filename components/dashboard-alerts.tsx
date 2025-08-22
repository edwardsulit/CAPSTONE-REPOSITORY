import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ChevronRight } from "lucide-react"

// ALERTS DATA - Replace with your actual alerts/notifications
const alerts = [
  {
    id: 1,
    name: "James Robinson",
    message: "I need some help/support...",
    avatar: "JR", // USER INITIALS
    color: "bg-chart-4", // AVATAR BACKGROUND COLOR
  },
  {
    id: 2,
    name: "Enoca Igbinobaro",
    message: "I got my items but got a...",
    avatar: "EI",
    color: "bg-destructive", // RED COLOR FOR URGENT
  },
  {
    id: 3,
    name: "James Robinson",
    message: "I need some help/support...",
    avatar: "JR",
    color: "bg-chart-4",
  },
  {
    id: 4,
    name: "Lupita Sarah",
    message: "Order was delivered to...",
    avatar: "LS",
    color: "bg-chart-5", // DIFFERENT COLOR
  },
]
// TO CUSTOMIZE: Replace with dynamic data from your API

export function DashboardAlerts() {
  return (
    // ALERTS CARD - Full height to match left section
    <Card className="h-full">
      {/* CARD HEADER - Title and stats link */}
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Alerts</CardTitle>
          {/* TO CUSTOMIZE: Change section title */}

          <span className="text-sm text-muted-foreground">Stats</span>
          {/* TO CUSTOMIZE: Replace with actual stats or remove */}
        </div>
      </CardHeader>

      {/* CARD CONTENT - List of alerts */}
      <CardContent>
        {/* ALERTS LIST - Scrollable if too many items */}
        <div className="space-y-4">
          {alerts.map((alert) => (
            // INDIVIDUAL ALERT ITEM - Clickable with hover effect
            <div
              key={alert.id}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted/50 cursor-pointer group"
              // TO ADD: onClick handler for alert interaction
            >
              {/* USER AVATAR - Colored circle with initials */}
              <Avatar className="h-10 w-10">
                <AvatarFallback className={`${alert.color} text-white`}>
                  {alert.avatar}
                  {/* TO CUSTOMIZE: Replace with actual user image */}
                </AvatarFallback>
              </Avatar>

              {/* ALERT CONTENT - Name and message */}
              <div className="flex-1 min-w-0">
                {/* USER NAME */}
                <p className="text-sm font-medium text-foreground">{alert.name}</p>

                {/* ALERT MESSAGE - Truncated if too long */}
                <p className="text-xs text-muted-foreground truncate">{alert.message}</p>
                {/* TO CUSTOMIZE: Show full message on hover or click */}
              </div>

              {/* CHEVRON ARROW - Indicates clickable item */}
              <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
