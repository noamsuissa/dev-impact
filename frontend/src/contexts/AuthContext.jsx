import { createContext, useEffect, useState } from 'react'
import { auth, user as userClient } from '../utils/client'

// Create the context
const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(null)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Helper function to load and merge user profile with auth user
  const loadUserProfile = async (authUser) => {
    if (!authUser) return null
    
    try {
      const profileData = await userClient.getProfile()
      if (profileData) {
        // Merge auth user with profile data
        return {
          ...authUser,
          username: profileData.username,
          name: profileData.full_name,
          github: profileData.github_username ? {
            username: profileData.github_username,
            avatar_url: profileData.github_avatar_url
          } : null
        }
      }
    } catch (err) {
      console.error('Failed to load user profile:', err)
      // Return auth user without profile data if profile fetch fails
      return authUser
    }
    
    return authUser
  }

  useEffect(() => {
    // Get initial session
    const loadSession = async () => {
      try {
        const data = await auth.getSession()
        
        if (data.user) {
          setSession(data.session)
          // Load and merge profile data
          const mergedUser = await loadUserProfile(data.user)
          setUser(mergedUser)
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
      // Load and merge profile data
      const mergedUser = await loadUserProfile(data.user)
      setUser(mergedUser)
      return { ...data, user: mergedUser }
    },
    signUp: async (email, password) => {
      const data = await auth.signUp(email, password)
      if (data.session) {
        setSession(data.session)
        // Load and merge profile data
        const mergedUser = await loadUserProfile(data.user)
        setUser(mergedUser)
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
          // Load and merge profile data
          const mergedUser = await loadUserProfile(data.user)
          setUser(mergedUser)
          return { ...data, user: mergedUser }
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
    updateUserProfile: async () => {
      // Helper method to refresh just the profile part of the user
      if (user) {
        const mergedUser = await loadUserProfile(user)
        setUser(mergedUser)
        return mergedUser
      }
      return null
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

