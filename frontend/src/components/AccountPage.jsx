import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Github, ArrowLeft, Trash2, User, Shield, ShieldCheck, ShieldOff, CreditCard, Sparkles } from 'lucide-react';
import TerminalButton from './common/TerminalButton';
import DeleteAccountModal from './DeleteAccountModal';
import MFASetup from './auth/MFASetup';
import UpgradeModal from './UpgradeModal';
import { user as userClient, auth as authClient, subscriptions as subscriptionsClient } from '../utils/client';
import { useAuth } from '../hooks/useAuth';

const AccountPage = ({ user, projects }) => {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [mfaFactors, setMfaFactors] = useState([]);
  const [loadingMFA, setLoadingMFA] = useState(false);
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [mfaError, setMfaError] = useState(null);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);

  useEffect(() => {
    loadMFAFactors();
  }, []);

  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [isCancelling, setIsCancelling] = useState(false);

  useEffect(() => {
    loadMFAFactors();
    loadSubscriptionInfo();
  }, []);

  const loadSubscriptionInfo = async () => {
    try {
      const info = await subscriptionsClient.getSubscriptionInfo();
      setSubscriptionInfo(info);
    } catch (error) {
      console.error('Failed to load subscription info:', error);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your Pro subscription? You will lose access to Pro features at the end of your billing period.')) {
      return;
    }

    setIsCancelling(true);
    try {
      await subscriptionsClient.cancelSubscription();
      await loadSubscriptionInfo();
      alert('Subscription cancelled successfully. You will retain access until the end of your billing period.');

      // Poll for update
      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        if (attempts > 5) {
          clearInterval(interval);
          return;
        }
        await loadSubscriptionInfo();
      }, 2000);

    } catch (error) {
      console.error('Failed to cancel subscription:', error);
      alert('Failed to cancel subscription: ' + error.message);
    } finally {
      setIsCancelling(false);
    }
  };

  const loadMFAFactors = async () => {
    setLoadingMFA(true);
    setMfaError(null);
    try {
      const data = await authClient.mfaListFactors();
      setMfaFactors(data.factors || []);
    } catch (error) {
      console.error('Failed to load MFA factors:', error);
      setMfaError('Failed to load MFA settings');
    } finally {
      setLoadingMFA(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await userClient.deleteAccount();
      // Sign out and redirect to home
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Failed to delete account:', error);
      alert('Failed to delete account: ' + error.message);
      setIsDeleting(false);
    }
  };

  const handleUnenrollMFA = async (factorId) => {
    if (!confirm('Are you sure you want to disable two-factor authentication? This will make your account less secure.')) {
      return;
    }

    setLoadingMFA(true);
    setMfaError(null);
    try {
      await authClient.mfaUnenroll(factorId);
      await loadMFAFactors();
    } catch (error) {
      console.error('Failed to remove MFA:', error);
      setMfaError(error.message || 'Failed to disable MFA');
    } finally {
      setLoadingMFA(false);
    }
  };

  const handleMFASetupComplete = () => {
    setShowMFASetup(false);
    loadMFAFactors();
  };

  const handleMFASetupCancel = () => {
    setShowMFASetup(false);
  };

  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-10 flex items-center gap-5">
        <Link to="/dashboard">
          <TerminalButton>
            <ArrowLeft size={16} className="inline mr-2" />
            [Back to Dashboard]
          </TerminalButton>
        </Link>
      </div>

      <div className="border border-terminal-border p-10 mb-10">
        <div className="flex items-start gap-6 mb-6">
          {user.github?.avatar_url ? (
            <img
              src={user.github.avatar_url}
              alt={user.name}
              className="w-24 h-24 rounded-full border-2 border-terminal-orange"
            />
          ) : (
            <div className="w-24 h-24 rounded-full border-2 border-terminal-orange flex items-center justify-center bg-terminal-bg-lighter">
              <User size={40} className="text-terminal-orange" />
            </div>
          )}
          <div className="flex-1">
            <div className="text-[32px] mb-2.5 uppercase text-terminal-orange">
              {user.name || 'User'}
            </div>
            <div className="text-lg text-[#c9c5c0] mb-5">
              Account Settings
            </div>
            {user.github?.username && (
              <div className="mb-2.5 flex items-center gap-2">
                <Github size={16} />
                <span className="text-terminal-gray">github.com/{user.github.username}</span>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-terminal-border pt-5 mt-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-[#c9c5c0]">
            <div>
              <div className="text-terminal-gray text-sm mb-1">Username</div>
              <div className="text-terminal-orange">{user.username || 'N/A'}</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Full Name</div>
              <div className="text-terminal-orange">{user.name || 'N/A'}</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Projects</div>
              <div className="text-terminal-orange">{projects.length} {projects.length === 1 ? 'Project' : 'Projects'}</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Total Achievements</div>
              <div className="text-terminal-orange">{projects.reduce((sum, p) => sum + p.metrics.length, 0)} Achievements</div>
            </div>
            <div>
              <div className="text-terminal-gray text-sm mb-1">Location</div>
              <div className="text-terminal-orange">
                {user.city && user.country
                  ? `${user.city}, ${user.country}`
                  : user.city
                  ? user.city
                  : user.country
                  ? user.country
                  : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subscription Section */}
      <div className="border border-terminal-border p-10 mb-10">
        <div className="mb-6">
          <h3 className="text-lg text-terminal-orange mb-2 flex items-center gap-2">
            <CreditCard size={20} />
            Subscription Plan
          </h3>
          <p className="text-terminal-gray text-sm">
            Manage your subscription and billing details.
          </p>
        </div>

        {subscriptionInfo ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between border border-terminal-border p-4 bg-terminal-bg-lighter">
              <div>
                <div className="text-terminal-orange font-medium flex items-center gap-2">
                  {subscriptionInfo.subscription_type === 'pro' ? 'Pro Plan' : 'Free Plan'}
                  {subscriptionInfo.cancel_at_period_end && (
                    <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded border border-yellow-500/30">
                      Cancellation Pending
                    </span>
                  )}
                </div>
                <div className="text-terminal-gray text-sm mt-1">
                  {subscriptionInfo.subscription_type === 'pro'
                    ? (subscriptionInfo.cancel_at_period_end
                      ? `Access until ${subscriptionInfo.current_period_end ? new Date(subscriptionInfo.current_period_end).toLocaleDateString() : 'period end'}`
                      : 'Unlimited portfolios and more features')
                    : 'Limited to 1 portfolio and basic features'}
                </div>
              </div>

              {subscriptionInfo.subscription_type === 'pro' && !subscriptionInfo.cancel_at_period_end && (
                <TerminalButton
                  onClick={handleCancelSubscription}
                  disabled={isCancelling}
                  className="bg-red-500/10 hover:bg-red-500/20 border-red-500/30 text-red-400"
                >
                  {isCancelling ? '[Cancelling...]' : '[Cancel Subscription]'}
                </TerminalButton>
              )}

              {subscriptionInfo.subscription_type === 'free' && (
                <TerminalButton
                  onClick={() => setIsUpgradeModalOpen(true)}
                  className="text-terminal-orange border-terminal-orange hover:bg-terminal-orange/10"
                >
                  <Sparkles size={16} className="inline mr-2" />
                  {import.meta.env.VITE_ENABLE_PAYMENTS === 'true' ? "[Upgrade to Pro]" : "[Join Waitlist]"}
                </TerminalButton>
              )}
            </div>
          </div>
        ) : (
          <div className="text-terminal-gray">&gt; Loading subscription info...</div>
        )}
      </div>

      {/* MFA Section */}
      {import.meta.env.VITE_ENVIRONMENT === 'production' && (
        <div className="border border-terminal-border p-10 mb-10">
          <div className="mb-6">
            <h3 className="text-lg text-terminal-orange mb-2 flex items-center gap-2">
              <Shield size={20} />
              Two-Factor Authentication
            </h3>
            <p className="text-terminal-gray text-sm">
              Add an extra layer of security to your account by requiring a verification code from your authenticator app when signing in.
            </p>
          </div>

          {showMFASetup ? (
            <MFASetup
              onComplete={handleMFASetupComplete}
              onCancel={handleMFASetupCancel}
            />
          ) : (
            <>
              {loadingMFA ? (
                <div className="text-terminal-gray">
                  &gt; Loading MFA settings...
                </div>
              ) : (
                <>
                  {mfaError && (
                    <div className="text-red-400 bg-red-400/10 border border-red-400/30 p-3 rounded mb-5">
                      ✗ {mfaError}
                    </div>
                  )}

                  {mfaFactors.length === 0 ? (
                    <div className="space-y-4">
                      <div className="flex items-center gap-2 text-terminal-gray">
                        <ShieldOff size={16} />
                        <span>Two-factor authentication is not enabled</span>
                      </div>
                      <TerminalButton
                        onClick={() => setShowMFASetup(true)}
                        disabled={loadingMFA}
                      >
                        <Shield size={16} className="inline mr-2" />
                        [Enable Two-Factor Authentication]
                      </TerminalButton>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {mfaFactors.some(f => f.status === 'verified') ? (
                        <div className="flex items-center gap-2 text-terminal-green">
                          <ShieldCheck size={16} />
                          <span>Two-factor authentication is enabled</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-yellow-400">
                          <Shield size={16} />
                          <span>Two-factor authentication setup incomplete - please verify your authenticator app</span>
                        </div>
                      )}

                      <div className="space-y-3">
                        {mfaFactors.map((factor) => (
                          <div
                            key={factor.id}
                            className="border border-terminal-border p-4 rounded bg-terminal-bg-lighter flex items-center justify-between"
                          >
                            <div>
                              <div className="text-terminal-orange font-medium">
                                {factor.friendly_name || 'Authenticator App'}
                              </div>
                              <div className="text-terminal-gray text-sm">
                                {factor.type.toUpperCase()} • {factor.status}
                                {factor.status !== 'verified' && (
                                  <span className="text-yellow-400 ml-2">(Not verified)</span>
                                )}
                              </div>
                            </div>
                            <div className="flex gap-2">
                              {factor.status !== 'verified' && (
                                <TerminalButton
                                  onClick={() => {
                                    // Remove unverified factor and start fresh
                                    handleUnenrollMFA(factor.id).then(() => {
                                      setShowMFASetup(true);
                                    });
                                  }}
                                  disabled={loadingMFA}
                                  className="bg-yellow-500/20 hover:bg-yellow-500/30 border-yellow-500/50 text-yellow-400"
                                >
                                  [Retry Setup]
                                </TerminalButton>
                              )}
                              <TerminalButton
                                onClick={() => handleUnenrollMFA(factor.id)}
                                disabled={loadingMFA}
                                className="bg-red-500/20 hover:bg-red-500/30 border-red-500/50 text-red-400"
                              >
                                [Remove]
                              </TerminalButton>
                            </div>
                          </div>
                        ))}
                      </div>

                      <TerminalButton
                        onClick={() => setShowMFASetup(true)}
                        disabled={loadingMFA}
                      >
                        <Shield size={16} className="inline mr-2" />
                        [Add Another Authenticator]
                      </TerminalButton>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      )}

      <div className="border border-red-500/30 bg-red-500/10 p-6 rounded">
        <div className="mb-4">
          <h3 className="text-lg text-red-400 mb-2 flex items-center gap-2">
            <Trash2 size={20} />
            Danger Zone
          </h3>
          <p className="text-terminal-gray text-sm">
            Once you delete your account, there is no going back. This will permanently delete your profile, projects, and all associated data.
          </p>
        </div>
        <TerminalButton
          onClick={() => setShowDeleteModal(true)}
          disabled={isDeleting}
          className="bg-red-500/20 hover:bg-red-500/30 border-red-500/50 text-red-400"
        >
          <Trash2 size={16} className="inline mr-2" />
          {isDeleting ? '[Deleting...]' : '[Delete Account]'}
        </TerminalButton>
      </div>

      {showDeleteModal && (
        <DeleteAccountModal
          onConfirm={handleDeleteAccount}
          onCancel={() => {
            setShowDeleteModal(false);
            setIsDeleting(false);
          }}
          isDeleting={isDeleting}
        />
      )}

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={isUpgradeModalOpen}
        onClose={() => setIsUpgradeModalOpen(false)}
        isLimitReached={!subscriptionInfo?.can_add_portfolio && subscriptionInfo?.subscription_type !== 'pro'}
      />
    </div>
  );
};

export default AccountPage;

