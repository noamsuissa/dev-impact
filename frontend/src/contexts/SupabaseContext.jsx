import { createContext, useEffect, useState } from 'react'
import { supabase } from '../utils/supabaseClient'

// Create the context
const SupabaseContext = createContext()

// Clean up any old/conflicting auth tokens
const cleanupOldTokens = () => {
  try {
    // Remove old Supabase tokens that might conflict
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith('sb-') && key !== 'dev-impact-auth-token') {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key))
  } catch (e) {
    console.error('Failed to cleanup old tokens:', e)
  }
}

export const SupabaseProvider = ({ children }) => {
  const [session, setSession] = useState(null)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Cleanup old tokens on mount
    cleanupOldTokens()
    
    // Get initial session
    supabase.auth.getSession().then(({ data: { session }, error }) => {
      if (error) {
        console.error('Error getting session:', error)
        // Clear session if there's an error
        setSession(null)
        setUser(null)
      } else {
        setSession(session)
        setUser(session?.user ?? null)
      }
      setLoading(false)
    }).catch((err) => {
      console.error('Failed to get session:', err)
      setSession(null)
      setUser(null)
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      console.log('Auth state changed:', event)
      
      if (event === 'SIGNED_OUT' || event === 'USER_DELETED') {
        setSession(null)
        setUser(null)
      } else if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
        setSession(session)
        setUser(session?.user ?? null)
      } else if (event === 'INITIAL_SESSION') {
        setSession(session)
        setUser(session?.user ?? null)
      }
      
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const value = {
    supabase,
    session,
    user,
    loading,
  }

  return (
    <SupabaseContext.Provider value={value}>
      {children}
    </SupabaseContext.Provider>
  )
}

// Export context for use in the custom hook
export { SupabaseContext }
