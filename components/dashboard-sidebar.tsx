"use client"

import { Home, ShoppingCart, Package, BarChart3, Settings } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { usePathname } from "next/navigation"

// NAVIGATION MENU DATA - Add/remove menu items here
const navigation = [
  { name: "Home", icon: Home, href: "/" },
  { name: "Sales", icon: BarChart3, href: "/sales" },
  { name: "Purchases", icon: ShoppingCart, href: "/purchases" },
  { name: "Inventory", icon: Package, href: "/inventory" },
  { name: "Reports", icon: BarChart3, href: "/reports" },
  { name: "Settings", icon: Settings, href: "/settings" },
]

export function DashboardSidebar() {
  const pathname = usePathname()

  return (
    // SIDEBAR CONTAINER - Fixed width (256px) with border
    <div className="w-64 bg-sidebar border-r border-sidebar-border">
      {/* LOGO SECTION - Brand name at top */}
      <div className="p-6">
        <h1 className="text-2xl font-bold text-sidebar-foreground">SHIELD</h1>
        {/* TO CUSTOMIZE: Change "SHIELD" to your app name */}
      </div>

      {/* NAVIGATION SECTION */}
      <nav className="px-3">
        {/* SECTION HEADER - "Payments" category */}
        <div className="mb-4">
          <h2 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Payments
            {/* TO CUSTOMIZE: Change section name here */}
          </h2>

          {/* MENU ITEMS LIST */}
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                    isActive
                      ? "bg-sidebar-accent text-sidebar-accent-foreground"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  )}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>
    </div>
  )
}
