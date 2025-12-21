import { createContext, useState, useEffect, useMemo } from 'react'
import { useAuth } from '../hooks/useAuth'
import { completeGitHubAuth } from '../utils/githubAuth'
import { profiles, userProfiles as userProfilesClient, subscriptions, projects as projectsClient, user as userClient } from '../utils/client'
import { generateProfileUrl } from '../utils/helpers'

// Create the context
const DashboardContext = createContext()

export const DashboardProvider = ({ children }) => {
  const { user, updateUserProfile } = useAuth()
  
  // GitHub state
  const [githubState, setGithubState] = useState('initial') // initial, loading, awaiting, success, error
  const [deviceCode, setDeviceCode] = useState(null)
  const [error, setError] = useState(null)
  
  // Publish state
  const [publishState, setPublishState] = useState('initial') // initial, loading, success, error
  const [publishedUrl, setPublishedUrl] = useState(null)
  const [isPublished, setIsPublished] = useState(false)
  const [showCopied, setShowCopied] = useState(false)
  
  // Data state
  const [projects, setProjects] = useState([])
  const [userProfilesList, setUserProfilesList] = useState([])
  const [selectedProfileId, setSelectedProfileId] = useState(null)
  const [publishedProfileSlugs, setPublishedProfileSlugs] = useState([])
  const [subscriptionInfo, setSubscriptionInfo] = useState(null)
  
  // Modal state
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false)
  const [isPublishModalOpen, setIsPublishModalOpen] = useState(false)
  const [isUnpublishModalOpen, setIsUnpublishModalOpen] = useState(false)
  const [isManageProfilesModalOpen, setIsManageProfilesModalOpen] = useState(false)
  const [editingProfile, setEditingProfile] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false)
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false)

  // Load projects on mount
  useEffect(() => {
    const loadProjects = async () => {
      if (!user) return
      try {
        const data = await projectsClient.list()
        setProjects(data || [])
      } catch (err) {
        console.error('Failed to load projects:', err)
        setProjects([])
      }
    }
    loadProjects()
  }, [user])

  // Load user profiles and subscription info on mount
  useEffect(() => {
    const loadProfiles = async () => {
      if (!user) return

      try {
        const profilesList = await userProfilesClient.list()
        setUserProfilesList(profilesList)

        // Load subscription info
        try {
          const subInfo = await subscriptions.getSubscriptionInfo()
          setSubscriptionInfo(subInfo)
        } catch (err) {
          console.error('Failed to load subscription info:', err)
          // Default to free tier if fetch fails
          setSubscriptionInfo({
            subscription_type: 'free',
            profile_count: profilesList.length,
            max_profiles: 3,
            can_add_profile: profilesList.length < 3
          })
        }

        // Select first profile if available and none is currently selected
        setSelectedProfileId(prev => {
          if (profilesList.length > 0 && !prev) {
            return profilesList[0].id
          }
          return prev
        })
      } catch (err) {
        console.error('Failed to load profiles:', err)
        setUserProfilesList([])
      }
    }

    loadProfiles()
  }, [user])

  // Check for plan=pro query parameter or pending subscription in localStorage
  useEffect(() => {
    const initCheckoutRedirect = async () => {
      const urlParams = new URLSearchParams(window.location.search)
      const planParam = urlParams.get('plan')
      const pendingSub = localStorage.getItem('pendingSubscription')

      if ((planParam === 'pro' || pendingSub === 'pro') && user) {
        try {
          // Create checkout session directly
          const baseUrl = window.location.origin
          const successUrl = `${baseUrl}/subscription/success`
          const cancelUrl = `${baseUrl}/subscription/cancel`

          const { checkout_url } = await subscriptions.createCheckoutSession(successUrl, cancelUrl)

          // Clean up flags only after successful creation
          if (planParam) {
            const newUrl = window.location.pathname
            window.history.replaceState({}, '', newUrl)
          }
          if (pendingSub) {
            localStorage.removeItem('pendingSubscription')
          }

          // Go to Stripe
          window.location.href = checkout_url

        } catch (err) {
          console.error('Direct checkout redirect failed:', err)
          // Fallback to modal on error so user isn't stuck
          if (!subscriptionInfo?.can_add_profile) {
            setIsUpgradeModalOpen(true)
          }
        }
      }
    }

    initCheckoutRedirect()
  }, [user, subscriptionInfo])

  // Check published status for all profiles
  useEffect(() => {
    const checkPublishedStatus = async () => {
      if (!user || userProfilesList.length === 0) return

      const username = user.username
      const publishedSlugs = []

      // Check each profile's published status
      for (const profile of userProfilesList) {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const response = await fetch(`${apiUrl}/api/profiles/${username}/${profile.slug}`)

          if (response.ok) {
            publishedSlugs.push(profile.slug)
          }
        } catch {
          // Profile not published, that's okay
        }
      }

      setPublishedProfileSlugs(publishedSlugs)

      // Update published state for selected profile
      if (selectedProfileId) {
        const selectedProfile = userProfilesList.find(p => p.id === selectedProfileId)
        if (selectedProfile && publishedSlugs.includes(selectedProfile.slug)) {
          setIsPublished(true)
          const shareUrl = generateProfileUrl(username, selectedProfile.slug)
          setPublishedUrl(shareUrl)
        } else {
          setIsPublished(false)
          setPublishedUrl(null)
        }
      }
    }

    checkPublishedStatus()
  }, [user, userProfilesList, selectedProfileId])

  // Save selected profile to localStorage
  useEffect(() => {
    if (selectedProfileId && typeof window !== 'undefined') {
      localStorage.setItem('selectedProfileId', selectedProfileId)
    }
  }, [selectedProfileId])

  // Filter projects by selected profile (derived state)
  const filteredProjects = useMemo(() => {
    if (!selectedProfileId) {
      // If no profile selected, show projects without a profile_id (unassigned)
      return projects.filter(p => {
        const pid = p.profile_id
        return !pid || pid === null || pid === undefined || pid === ''
      })
    }

    // Filter projects that belong ONLY to the selected profile
    // Also include unassigned projects (null/undefined) so user can assign them
    const filtered = projects.filter(p => {
      const pid = p.profile_id
      // Show if: unassigned (null/undefined/empty) OR exactly matches selected profile
      const isUnassigned = !pid || pid === null || pid === undefined || pid === ''
      const matchesProfile = pid === selectedProfileId
      return isUnassigned || matchesProfile
    })

    return filtered
  }, [projects, selectedProfileId])

  // GitHub handlers
  const handleConnectGitHub = async () => {
    setGithubState('loading')
    setError(null)

    try {
      const result = await completeGitHubAuth(
        ({ userCode, verificationUri }) => {
          setDeviceCode({ userCode, verificationUri })
          setGithubState('awaiting')
        },
        () => {
          // Progress callback - no logging needed in production
        }
      )

      setGithubState('success')

      // Update user profile with GitHub data
      await handleGitHubConnect(result)
    } catch (err) {
      console.error('GitHub OAuth error:', err)
      setError(err.message)
      setGithubState('error')
    }
  }

  const handleCancelGitHub = () => {
    setGithubState('initial')
    setDeviceCode(null)
    setError(null)
  }

  const handleGitHubConnect = async (githubData) => {
    try {
      await userClient.updateProfile({
        github_username: githubData.username,
        github_avatar_url: githubData.avatar_url
      })
      // Refresh the AuthContext user state to reflect the GitHub connection
      await updateUserProfile()
    } catch (err) {
      console.error('Failed to update profile with GitHub data:', err)
      throw err
    }
  }

  // Copy link handler
  const handleCopyLink = async () => {
    if (!publishedUrl) return

    try {
      await navigator.clipboard.writeText(publishedUrl)
      setShowCopied(true)
      setTimeout(() => setShowCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // Profile publish handlers
  const handlePublishProfile = async (profileIdToPublish) => {
    const profileToPublish = userProfilesList.find(p => p.id === profileIdToPublish)
    if (!profileToPublish) {
      throw new Error('Profile not found.')
    }

    // Check if profile has projects - filter by exact profile_id match (exclude null/undefined)
    const profileProjects = projects.filter(p => {
      const pid = p.profile_id
      return pid && pid === profileIdToPublish
    })

    if (profileProjects.length === 0) {
      throw new Error('Please add at least one project to this profile before publishing. Edit your projects to assign them to this profile.')
    }

    setPublishState('loading')
    setError(null)

    try {
      const username = user.username

      // Publish via API with profile_id
      const response = await profiles.publish({
        username,
        profile_id: profileIdToPublish
      })

      // Use URL from backend response
      const shareUrl = generateProfileUrl(username, response.profile_slug)
      setPublishedUrl(shareUrl)

      // Mark as published
      setIsPublished(true)
      setPublishedProfileSlugs([...publishedProfileSlugs, profileToPublish.slug])

      // If this is the selected profile, update the published URL
      if (profileIdToPublish === selectedProfileId) {
        setPublishedUrl(shareUrl)
      }

      try {
        await navigator.clipboard.writeText(shareUrl)
        setPublishState('success')

        // Reset success state after 5 seconds
        setTimeout(() => {
          setPublishState('initial')
        }, 5000)
      } catch (clipboardError) {
        console.error('Failed to copy to clipboard:', clipboardError)
        setPublishState('success')
      }
    } catch (err) {
      console.error('Error publishing profile:', err)
      setError(err.message)
      setPublishState('error')
      throw err // Re-throw so modal can handle it
    }
  }

  const handleUnpublishProfile = async (profileIdToUnpublish) => {
    const profileToUnpublish = userProfilesList.find(p => p.id === profileIdToUnpublish)
    if (!profileToUnpublish) {
      throw new Error('Profile not found.')
    }

    setPublishState('loading')
    setError(null)

    try {
      const username = user.username

      // Unpublish via API
      await profiles.unpublish(username, profileToUnpublish.slug)

      // Mark as unpublished
      setPublishedProfileSlugs(publishedProfileSlugs.filter(s => s !== profileToUnpublish.slug))

      // If this is the selected profile, update the published state
      if (profileIdToUnpublish === selectedProfileId) {
        setIsPublished(false)
        setPublishedUrl(null)
      }

      setPublishState('initial')
    } catch (err) {
      console.error('Error unpublishing profile:', err)
      setError(err.message)
      setPublishState('error')
      throw err // Re-throw so modal can handle it
    }
  }

  // Profile CRUD handlers
  const handleCreateProfile = async (profileData) => {
    const newProfile = await userProfilesClient.create(profileData)
    setUserProfilesList([...userProfilesList, newProfile])

    // Select the newly created profile
    setSelectedProfileId(newProfile.id)

    // Refresh subscription info
    try {
      const subInfo = await subscriptions.getSubscriptionInfo()
      setSubscriptionInfo(subInfo)
    } catch (err) {
      console.error('Failed to refresh subscription info:', err)
    }
  }

  const handleUpdateProfile = async (profileData) => {
    if (!editingProfile) return

    const updatedProfile = await userProfilesClient.update(editingProfile.id, profileData)
    setUserProfilesList(userProfilesList.map(p =>
      p.id === updatedProfile.id ? updatedProfile : p
    ))
    setEditingProfile(null)
  }

  const handleDeleteProfile = async (profileId) => {
    const profileToDelete = userProfilesList.find(p => p.id === profileId)
    if (!profileToDelete) {
      throw new Error('Profile not found.')
    }

    // Delete profile (backend will delete all assigned projects)
    await userProfilesClient.delete(profileId)

    // Remove profile from list
    setUserProfilesList(userProfilesList.filter(p => p.id !== profileId))

    // Filter out deleted projects from state
    setProjects(projects.filter(p => p.profile_id !== profileId))

    // Select first remaining profile or null
    const remaining = userProfilesList.filter(p => p.id !== profileId)
    setSelectedProfileId(remaining.length > 0 ? remaining[0].id : null)

    // Refresh subscription info
    try {
      const subInfo = await subscriptions.getSubscriptionInfo()
      setSubscriptionInfo(subInfo)
    } catch (err) {
      console.error('Failed to refresh subscription info:', err)
    }
  }

  // Project CRUD handlers
  const handleSaveProject = async (project) => {
    try {
      const isExisting = projects.some(p => p.id === project.id)
      if (isExisting) {
        const updated = await projectsClient.update(project.id, project)
        // Ensure profile_id is included in the updated project
        const updatedWithProfile = {
          ...updated,
          profile_id: updated.profile_id || project.profile_id || null
        }
        setProjects(projects.map(p => p.id === project.id ? updatedWithProfile : p))
      } else {
        const created = await projectsClient.create(project)
        // Ensure profile_id is included in the created project
        const createdWithProfile = {
          ...created,
          profile_id: created.profile_id || project.profile_id || null
        }
        setProjects([...projects, createdWithProfile])
      }
    } catch (err) {
      console.error('Failed to save project:', err)
      alert('Failed to save project: ' + err.message)
      throw err
    }
  }

  const handleDeleteProject = async (id) => {
    if (!confirm('Delete this project?')) return
    try {
      await projectsClient.delete(id)
      setProjects(projects.filter(p => p.id !== id))
    } catch (err) {
      console.error('Failed to delete project:', err)
      alert('Failed to delete project: ' + err.message)
    }
  }

  // Modal handlers
  const handleOpenPublishModal = () => {
    setIsPublishModalOpen(true)
  }

  const handleClosePublishModal = () => {
    setIsPublishModalOpen(false)
    setError(null)
  }

  const handleOpenUnpublishModal = () => {
    setIsUnpublishModalOpen(true)
  }

  const handleCloseUnpublishModal = () => {
    setIsUnpublishModalOpen(false)
    setError(null)
  }

  const handleOpenManageProfilesModal = () => {
    setIsManageProfilesModalOpen(true)
  }

  const handleCloseManageProfilesModal = () => {
    setIsManageProfilesModalOpen(false)
  }

  const handleOpenProfileModal = (profile = null) => {
    setEditingProfile(profile)
    setIsProfileModalOpen(true)
  }

  const handleCloseProfileModal = () => {
    setIsProfileModalOpen(false)
    setEditingProfile(null)
  }

  const value = {
    github: {
      state: githubState,
      deviceCode,
      handleConnect: handleConnectGitHub,
      handleCancel: handleCancelGitHub,
      handleGitHubConnect,
    },
    publish: {
      state: publishState,
      url: publishedUrl,
      isPublished,
      showCopied,
      handleCopyLink,
      handlePublish: handlePublishProfile,
      handleUnpublish: handleUnpublishProfile,
      openModal: handleOpenPublishModal,
      closeModal: handleClosePublishModal,
      isModalOpen: isPublishModalOpen,
      openUnpublishModal: handleOpenUnpublishModal,
      closeUnpublishModal: handleCloseUnpublishModal,
      isUnpublishModalOpen: isUnpublishModalOpen,
      publishedProfileSlugs,
    },
    profiles: {
      list: userProfilesList,
      selectedId: selectedProfileId,
      editing: editingProfile,
      canManage: subscriptionInfo?.can_add_profile ?? true,
      subscriptionInfo,
      handleCreate: handleCreateProfile,
      handleUpdate: handleUpdateProfile,
      handleDelete: handleDeleteProfile,
      setSelectedId: setSelectedProfileId,
      openManageModal: handleOpenManageProfilesModal,
      closeManageModal: handleCloseManageProfilesModal,
      isManageModalOpen: isManageProfilesModalOpen,
      openProfileModal: handleOpenProfileModal,
      closeProfileModal: handleCloseProfileModal,
      isProfileModalOpen,
    },
    projects: {
      list: projects,
      filtered: filteredProjects,
      selected: selectedProject,
      setSelected: setSelectedProject,
      save: handleSaveProject,
      handleDelete: handleDeleteProject,
      openModal: setIsProjectModalOpen,
      isModalOpen: isProjectModalOpen,
    },
    upgrade: {
      isModalOpen: isUpgradeModalOpen,
      setIsModalOpen: setIsUpgradeModalOpen,
    },
    error,
  }

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

// Export context for use in the custom hook
export { DashboardContext }
