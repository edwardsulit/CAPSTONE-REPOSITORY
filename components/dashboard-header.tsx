"use client"

import { useState } from "react"
import { Search, Bell, ChevronDown, LogOut, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useAuth } from "@/lib/auth-context"

export function DashboardHeader() {
  const { user, logout } = useAuth()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const currentDate = new Date().toLocaleDateString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric'
  })

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
  }

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
          </div>
        </div>

        {/* RIGHT SECTION - Language, notifications, user profile */}
        <div className="flex items-center space-x-4">
          {/* LANGUAGE SELECTOR - Dropdown button */}
          <Button variant="ghost" className="text-muted-foreground">
            English
            <ChevronDown className="ml-1 h-4 w-4" />
          </Button>

          {/* NOTIFICATION BELL - Icon button */}
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>

          {/* USER PROFILE SECTION - Avatar + info + dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 hover:bg-accent/50 rounded-md p-1 transition-colors"
            >
              {/* USER AVATAR - 32x32px circle */}
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {user?.username ? user.username.charAt(0).toUpperCase() : 'A'}
                </AvatarFallback>
              </Avatar>

              {/* USER INFO - Name and date */}
              <div className="text-sm text-left">
                <div className="font-medium capitalize">
                  {user?.username || 'Admin'}
                </div>
                <div className="text-muted-foreground">
                  {currentDate}
                </div>
              </div>

              {/* DROPDOWN ARROW - For user menu */}
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </button>

            {/* USER DROPDOWN MENU */}
            {showUserMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-background border border-border rounded-md shadow-lg z-50">
                <div className="p-2">
                  <div className="px-3 py-2 text-sm border-b border-border mb-2">
                    <div className="font-medium">Logged in as</div>
                    <div className="text-muted-foreground capitalize">{user?.username}</div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLogout}
                    className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Sign Out
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Backdrop to close menu when clicking outside */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </header>
  )
}
