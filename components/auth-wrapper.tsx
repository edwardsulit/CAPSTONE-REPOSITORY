"use client"

import { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

interface AuthWrapperProps {
  children: React.ReactNode
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!isLoading) {
      // If not authenticated and not on login page, redirect to login
      if (!user?.isAuthenticated && pathname !== "/login") {
        router.push("/login")
      }
      // If authenticated and on login page, redirect to dashboard
      else if (user?.isAuthenticated && pathname === "/login") {
        router.push("/")
      }
    }
  }, [user, isLoading, pathname, router])

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  // If on login page or authenticated, show content
  if (pathname === "/login" || user?.isAuthenticated) {
    return <>{children}</>
  }

  // Otherwise, don't render anything (will redirect)
  return null
}
