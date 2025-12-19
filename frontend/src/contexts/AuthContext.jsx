import { createContext, useEffect, useState } from 'react'
import { auth } from '../utils/client'

// Create the context
const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(null)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    const loadSession = async () => {
      try {
        const data = await auth.getSession()
        
        if (data.user) {
          setSession(data.session)
          setUser(data.user)
        } else {
          setSession(null)
          setUser(null)
        }
      } catch (err) {
        console.error('Failed to get session:', err)
        setSession(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    loadSession()
  }, [])

  const value = {
    session,
    user,
    loading,
    signIn: async (email, password) => {
      const data = await auth.signIn(email, password)
      setSession(data.session)
      setUser(data.user)
      return data
    },
    signUp: async (email, password) => {
      const data = await auth.signUp(email, password)
      if (data.session) {
        setSession(data.session)
        setUser(data.user)
      }
      return data
    },
    signOut: async () => {
      await auth.signOut()
      setSession(null)
      setUser(null)
    },
    refreshSession: async () => {
      try {
        const data = await auth.getSession()
        if (data.user) {
          setSession(data.session)
          setUser(data.user)
        } else {
          setSession(null)
          setUser(null)
        }
        return data
      } catch (err) {
        console.error('Failed to refresh session:', err)
        setSession(null)
        setUser(null)
        return { user: null, session: null }
      }
    },
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Export context for use in the custom hook
export { AuthContext }

