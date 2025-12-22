import { createContext, useState, useEffect, useMemo } from 'react'
import { useAuth } from '../hooks/useAuth'
import { completeGitHubAuth } from '../utils/githubAuth'
import { portfolios as portfoliosClient, subscriptions, projects as projectsClient, user as userClient } from '../utils/client'
import { generatePortfolioUrl } from '../utils/helpers'

// Create the context
const DashboardContext = createContext()

export const DashboardProvider = ({ children }) => {
  const { user, updateUserProfile } = useAuth()
  
  // GitHub state
  const [githubState, setGithubState] = useState('initial') // initial, loading, awaiting, success, error
  const [deviceCode, setDeviceCode] = useState(null)
  const [githubError, setGithubError] = useState(null)
  
  // Publish state
  const [publishState, setPublishState] = useState('initial') // initial, loading, success, error
  const [publishedUrl, setPublishedUrl] = useState(null)
  const [isPublished, setIsPublished] = useState(false)
  const [showCopied, setShowCopied] = useState(false)
  const [publishError, setPublishError] = useState(null)
  
  // Data state
  const [projects, setProjects] = useState([])
  const [portfoliosList, setPortfoliosList] = useState([])
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null)
  const [publishedPortfolioSlugs, setPublishedPortfolioSlugs] = useState([])
  const [subscriptionInfo, setSubscriptionInfo] = useState(null)
  
  // Modal state
  const [isPortfolioModalOpen, setIsPortfolioModalOpen] = useState(false)
  const [isPublishModalOpen, setIsPublishModalOpen] = useState(false)
  const [isUnpublishModalOpen, setIsUnpublishModalOpen] = useState(false)
  const [isManagePortfoliosModalOpen, setIsManagePortfoliosModalOpen] = useState(false)
  const [editingPortfolio, setEditingPortfolio] = useState(null)
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
    const loadPortfolios = async () => {
      if (!user) return

      try {
        const portfoliosList = await portfoliosClient.list()
        setPortfoliosList(portfoliosList)

        // Load subscription info
        try {
          const subInfo = await subscriptions.getSubscriptionInfo()
          setSubscriptionInfo(subInfo)
        } catch (err) {
          console.error('Failed to load subscription info:', err)
          // Default to free tier if fetch fails
          setSubscriptionInfo({
            subscription_type: 'free',
            portfolio_count: portfoliosList.length,
            max_portfolios: 3,
            can_add_portfolio: portfoliosList.length < 3
          })
        }

        // Restore selected profile from localStorage or select first profile
        setSelectedPortfolioId(prev => {
          if (prev) return prev // Keep current selection if already set
          
          if (portfoliosList.length === 0) return null
          
          // Try to restore from localStorage
          if (typeof window !== 'undefined') {
            const stored = localStorage.getItem('selectedPortfolioId')
            if (stored && portfoliosList.some(p => p.id === stored)) {
              return stored
            }
          }
          
          // Default to first profile
          return portfoliosList[0].id
        })
      } catch (err) {
        console.error('Failed to load portfolios:', err)
        setPortfoliosList([])
      }
    }

    loadPortfolios()
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
          if (!subscriptionInfo?.can_add_portfolio) {
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
      if (!user || portfoliosList.length === 0) return

      const username = user.username
      const publishedSlugs = []

      // Check each profile's published status
      for (const portfolio of portfoliosList) {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const response = await fetch(`${apiUrl}/api/portfolios/${username}/${portfolio.slug}`)

          if (response.ok) {
            publishedSlugs.push(portfolio.slug)
          }
        } catch {
          // Profile not published, that's okay
        }
      }

      setPublishedPortfolioSlugs(publishedSlugs)

      // Update published state for selected profile
      if (selectedPortfolioId) {
        const selectedPortfolio = portfoliosList.find(p => p.id === selectedPortfolioId)
        if (selectedPortfolio && publishedSlugs.includes(selectedPortfolio.slug)) {
          setIsPublished(true)
          const shareUrl = generatePortfolioUrl(username, selectedPortfolio.slug)
          setPublishedUrl(shareUrl)
        } else {
          setIsPublished(false)
          setPublishedUrl(null)
        }
      }
    }

    checkPublishedStatus()
  }, [user, portfoliosList, selectedPortfolioId])

  // Save selected profile to localStorage
  useEffect(() => {
    if (selectedPortfolioId && typeof window !== 'undefined') {
      localStorage.setItem('selectedPortfolioId', selectedPortfolioId)
    }
  }, [selectedPortfolioId])

  // Filter projects by selected profile (derived state)
  const filteredProjects = useMemo(() => {
    if (!selectedPortfolioId) {
      // If no profile selected, show projects without a portfolio_id (unassigned)
      return projects.filter(p => {
        const pid = p.portfolio_id
        return !pid || pid === null || pid === undefined || pid === ''
      })
    }

    // Filter projects that belong ONLY to the selected profile
    // Also include unassigned projects (null/undefined) so user can assign them
    const filtered = projects.filter(p => {
      const pid = p.portfolio_id
      // Show if: unassigned (null/undefined/empty) OR exactly matches selected profile
      const isUnassigned = !pid || pid === null || pid === undefined || pid === ''
      const matchesPortfolio = pid === selectedPortfolioId
      return isUnassigned || matchesPortfolio
    })

    return filtered
  }, [projects, selectedPortfolioId])

  // GitHub handlers
  const handleConnectGitHub = async () => {
    setGithubState('loading')
    setGithubError(null)

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
      setGithubError(err.message)
      setGithubState('error')
    }
  }

  const handleCancelGitHub = () => {
    setGithubState('initial')
    setDeviceCode(null)
    setGithubError(null)
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
      console.error('Failed to update portfolio with GitHub data:', err)
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
  const handlePublishPortfolio = async (portfolioIdToPublish) => {
    const portfolioToPublish = portfoliosList.find(p => p.id === portfolioIdToPublish)
    if (!portfolioToPublish) {
      throw new Error('Portfolio not found.')
    }

    // Check if profile has projects - filter by exact portfolio_id match (exclude null/undefined)
    const portfolioProjects = projects.filter(p => {
      const pid = p.portfolio_id
      return pid && pid === portfolioIdToPublish
    })

    if (portfolioProjects.length === 0) {
      throw new Error('Please add at least one project to this profile before publishing. Edit your projects to assign them to this profile.')
    }

    setPublishState('loading')
    setPublishError(null)

    try {
      const username = user.username

      // Publish via API with portfolio_id
      const response = await portfoliosClient.publish({
        username,
        portfolio_id: portfolioIdToPublish
      })

      // Use URL from backend response
      const shareUrl = generatePortfolioUrl(username, response.portfolio_slug)
      setPublishedUrl(shareUrl)

      // Mark as published
      setIsPublished(true)
      setPublishedPortfolioSlugs([...publishedPortfolioSlugs, portfolioToPublish.slug])

      // If this is the selected profile, update the published URL
      if (portfolioIdToPublish === selectedPortfolioId) {
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
      console.error('Error publishing portfolio:', err)
      setPublishError(err.message)
      setPublishState('error')
      throw err // Re-throw so modal can handle it
    }
  }

  const handleUnpublishPortfolio = async (portfolioIdToUnpublish) => {
    const portfolioToUnpublish = portfoliosList.find(p => p.id === portfolioIdToUnpublish)
    if (!portfolioToUnpublish) {
      throw new Error('Portfolio not found.')
    }

    setPublishState('loading')
    setPublishError(null)

    try {
      const username = user.username

      // Unpublish via API
      await portfoliosClient.unpublish(username, portfolioToUnpublish.slug)

      // Mark as unpublished
      setPublishedPortfolioSlugs(publishedPortfolioSlugs.filter(s => s !== portfolioToUnpublish.slug))

      // If this is the selected profile, update the published state
      if (portfolioIdToUnpublish === selectedPortfolioId) {
        setIsPublished(false)
        setPublishedUrl(null)
      }

      setPublishState('initial')
    } catch (err) {
      console.error('Error unpublishing portfolio:', err)
      setPublishError(err.message)
      setPublishState('error')
      throw err // Re-throw so modal can handle it
    }
  }

  // Profile CRUD handlers
  const handleCreatePortfolio = async (portfolioData) => {
    const newPortfolio = await portfoliosClient.create(portfolioData)
    setPortfoliosList([...portfoliosList, newPortfolio])

    // Select the newly created profile
    setSelectedPortfolioId(newPortfolio.id)

    // Refresh subscription info
    try {
      const subInfo = await subscriptions.getSubscriptionInfo()
      setSubscriptionInfo(subInfo)
    } catch (err) {
      console.error('Failed to refresh subscription info:', err)
    }
  }

  const handleUpdatePortfolio = async (portfolioData) => {
    if (!editingPortfolio) return

    const updatedPortfolio = await portfoliosClient.update(editingPortfolio.id, portfolioData)
    setPortfoliosList(portfoliosList.map(p =>
      p.id === updatedPortfolio.id ? updatedPortfolio : p
    ))
    setEditingPortfolio(null)
  }

  const handleDeletePortfolio = async (portfolioId) => {
    const portfolioToDelete = portfoliosList.find(p => p.id === portfolioId)
    if (!portfolioToDelete) {
      throw new Error('Portfolio not found.')
    }

    // Delete profile (backend will delete all assigned projects)
    await portfoliosClient.delete(portfolioId)

    // Remove profile from list
    setPortfoliosList(portfoliosList.filter(p => p.id !== portfolioId))

    // Filter out deleted projects from state
    setProjects(projects.filter(p => p.portfolio_id !== portfolioId))

    // Select first remaining portfolio or null
    const remaining = portfoliosList.filter(p => p.id !== portfolioId)
    setSelectedPortfolioId(remaining.length > 0 ? remaining[0].id : null)

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
        // Ensure portfolio_id is included in the updated project
        const updatedWithPortfolio = {
          ...updated,
          portfolio_id: updated.portfolio_id || project.portfolio_id || null
        }
        setProjects(projects.map(p => p.id === project.id ? updatedWithPortfolio : p))
      } else {
        const created = await projectsClient.create(project)
        // Ensure portfolio_id is included in the created project
        const createdWithPortfolio = {
          ...created,
          portfolio_id: created.portfolio_id || project.portfolio_id || null
        }
        setProjects([...projects, createdWithPortfolio])
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
    setPublishError(null)
  }

  const handleOpenUnpublishModal = () => {
    setIsUnpublishModalOpen(true)
  }

  const handleCloseUnpublishModal = () => {
    setIsUnpublishModalOpen(false)
    setPublishError(null)
  }

  const handleOpenManagePortfoliosModal = () => {
    setIsManagePortfoliosModalOpen(true)
  }

  const handleCloseManagePortfoliosModal = () => {
    setIsManagePortfoliosModalOpen(false)
  }

  const handleOpenPortfolioModal = (portfolio = null) => {
    setEditingPortfolio(portfolio)
    setIsPortfolioModalOpen(true)
  }

  const handleClosePortfolioModal = () => {
    setIsPortfolioModalOpen(false)
    setEditingPortfolio(null)
  }

  const value = {
    github: {
      state: githubState,
      deviceCode,
      error: githubError,
      handleConnect: handleConnectGitHub,
      handleCancel: handleCancelGitHub,
      handleGitHubConnect,
    },
    publish: {
      state: publishState,
      url: publishedUrl,
      isPublished,
      showCopied,
      error: publishError,
      handleCopyLink,
      handlePublish: handlePublishPortfolio,
      handleUnpublish: handleUnpublishPortfolio,
      openModal: handleOpenPublishModal,
      closeModal: handleClosePublishModal,
      isModalOpen: isPublishModalOpen,
      openUnpublishModal: handleOpenUnpublishModal,
      closeUnpublishModal: handleCloseUnpublishModal,
      isUnpublishModalOpen: isUnpublishModalOpen,
      publishedPortfolioSlugs,
    },
    portfolios: {
      list: portfoliosList,
      selectedId: selectedPortfolioId,
      editing: editingPortfolio,
      canManage: subscriptionInfo?.can_add_portfolio ?? true,
      subscriptionInfo,
      handleCreate: handleCreatePortfolio,
      handleUpdate: handleUpdatePortfolio,
      handleDelete: handleDeletePortfolio,
      setSelectedId: setSelectedPortfolioId,
      openManageModal: handleOpenManagePortfoliosModal,
      closeManageModal: handleCloseManagePortfoliosModal,
      isManageModalOpen: isManagePortfoliosModalOpen,
      openPortfolioModal: handleOpenPortfolioModal,
      closePortfolioModal: handleClosePortfolioModal,
      isPortfolioModalOpen,
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
  }

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

// Export context for use in the custom hook
export { DashboardContext }
