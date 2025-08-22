import { Search, Bell, ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

export function DashboardHeader() {
  return (
    // HEADER CONTAINER - Top navigation bar with border
    <header className="bg-background border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* LEFT SECTION - Search functionality */}
        <div className="flex items-center space-x-4">
          {/* SEARCH BAR - With search icon */}
          <div className="relative">
            {/* SEARCH ICON - Positioned inside input field */}
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />

            {/* SEARCH INPUT - 320px width with left padding for icon */}
            <Input placeholder="Search..." className="pl-10 w-80" />
            {/* TO CUSTOMIZE: Change placeholder text or width (w-80 = 320px) */}
          </div>
        </div>

        {/* RIGHT SECTION - Language, notifications, user profile */}
        <div className="flex items-center space-x-4">
          {/* LANGUAGE SELECTOR - Dropdown button */}
          <Button variant="ghost" className="text-muted-foreground">
            English
            {/* TO CUSTOMIZE: Change default language */}
            <ChevronDown className="ml-1 h-4 w-4" />
          </Button>

          {/* NOTIFICATION BELL - Icon button */}
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
            {/* TO ADD: Notification badge/count here */}
          </Button>

          {/* USER PROFILE SECTION - Avatar + info + dropdown */}
          <div className="flex items-center space-x-2">
            {/* USER AVATAR - 32x32px circle */}
            <Avatar className="h-8 w-8">
              <AvatarFallback>U</AvatarFallback>
              {/* TO CUSTOMIZE: Change "U" to user initials or add image */}
            </Avatar>

            {/* USER INFO - Name and date */}
            <div className="text-sm">
              <div className="font-medium">Username</div>
              {/* TO CUSTOMIZE: Replace with actual username */}

              <div className="text-muted-foreground">9/24/2024</div>
              {/* TO CUSTOMIZE: Replace with current date or last login */}
            </div>

            {/* DROPDOWN ARROW - For user menu */}
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </div>
        </div>
      </div>
    </header>
  )
}
