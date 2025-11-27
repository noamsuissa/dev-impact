import { useContext } from 'react'
import { SupabaseContext } from '../contexts/SupabaseContext'

// Custom hook to use the Supabase context
export const useSupabase = () => {
  const context = useContext(SupabaseContext)
  if (context === undefined) {
    throw new Error('useSupabase must be used within a SupabaseProvider')
  }
  return context
}

