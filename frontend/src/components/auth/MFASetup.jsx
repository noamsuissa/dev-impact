import React, { useState, useEffect } from 'react';
import TerminalButton from '../common/TerminalButton';
import TerminalInput from '../common/TerminalInput';
import { auth as authClient } from '../../utils/client';
import { Shield, CheckCircle2, XCircle } from 'lucide-react';

const MFASetup = ({ onComplete, onCancel }) => {
  const [step, setStep] = useState('enroll'); // 'enroll', 'verify', 'success'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [qrCodeBlobUrl, setQrCodeBlobUrl] = useState(null);
  const [secret, setSecret] = useState(null);
  const [factorId, setFactorId] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const friendlyName = 'Authenticator App';

  useEffect(() => {
    // Start enrollment when component mounts
    handleEnroll();
  }, []);

  // Cleanup blob URL on unmount
  useEffect(() => {
    return () => {
      if (qrCodeBlobUrl) {
        URL.revokeObjectURL(qrCodeBlobUrl);
      }
    };
  }, [qrCodeBlobUrl]);

  const handleEnroll = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await authClient.mfaEnroll(friendlyName);
      
      // Handle different response structures
      const qrCodeValue = data.qr_code || data.totp?.qr_code || data.qrCode;
      const secretValue = data.secret || data.totp?.secret;
      const factorIdValue = data.id || data.factor_id;
      
      // QR code is optional, but secret and factorId are required
      if (!secretValue || !factorIdValue) {
        console.error('Missing required MFA data:', { qrCodeValue, secretValue, factorIdValue, fullData: data });
        throw new Error('MFA enrollment response missing required data (secret or factor ID)');
      }
      
      // Set QR code if available (it's optional)
      if (qrCodeValue) {
        setQrCode(qrCodeValue);
        
        // Handle different QR code formats
        try {
          if (qrCodeValue.startsWith('data:image/')) {
            // Already a data URI - convert to blob URL
            const response = await fetch(qrCodeValue);
            if (!response.ok) {
              throw new Error('Failed to fetch data URI');
            }
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            setQrCodeBlobUrl(blobUrl);
          } else if (qrCodeValue.startsWith('<?xml') || qrCodeValue.startsWith('<svg')) {
            // Raw SVG XML - convert to data URI then blob URL
            const svgBlob = new Blob([qrCodeValue], { type: 'image/svg+xml' });
            const blobUrl = URL.createObjectURL(svgBlob);
            setQrCodeBlobUrl(blobUrl);
          } else if (qrCodeValue.startsWith('http://') || qrCodeValue.startsWith('https://')) {
            // HTTP/HTTPS URL - use directly
            setQrCodeBlobUrl(qrCodeValue);
          } else {
            // Try as data URI (might be base64 encoded)
            const dataUri = `data:image/svg+xml;base64,${btoa(qrCodeValue)}`;
            const response = await fetch(dataUri);
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            setQrCodeBlobUrl(blobUrl);
          }
        } catch (err) {
          console.error('Failed to convert QR code to blob URL:', err);
          // Last resort: try creating data URI from raw SVG
          if (qrCodeValue.startsWith('<?xml') || qrCodeValue.startsWith('<svg')) {
            try {
              const encoded = encodeURIComponent(qrCodeValue);
              const dataUri = `data:image/svg+xml;charset=utf-8,${encoded}`;
              setQrCodeBlobUrl(dataUri);
            } catch (encodeErr) {
              console.error('Failed to encode SVG as data URI:', encodeErr);
            }
          }
        }
      }
      
      setSecret(secretValue);
      setFactorId(factorIdValue);
      setStep('verify');
    } catch (err) {
      console.error('MFA enroll error:', err);
      setError(err.message || 'Failed to start MFA enrollment');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError(null);

    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setLoading(true);

    try {
      await authClient.mfaVerifyEnrollment(factorId, verificationCode);
      setStep('success');
      setTimeout(() => {
        if (onComplete) {
          onComplete();
        }
      }, 2000);
    } catch (err) {
      setError(err.message || 'Invalid verification code');
      setVerificationCode('');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  if (step === 'success') {
    return (
      <div className="fade-in text-center">
        <CheckCircle2 size={64} className="text-terminal-green mx-auto mb-4" />
        <div className="text-xl mb-2 text-terminal-green">
          &gt; MFA Enabled Successfully
        </div>
        <div className="text-terminal-gray mb-5">
          Your account is now protected with two-factor authentication
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="mb-5">
        <div className="text-xl mb-2 flex items-center gap-2">
          <Shield size={24} />
          &gt; Set Up Two-Factor Authentication
        </div>
        <div className="text-terminal-gray">
          Scan the QR code with your authenticator app
        </div>
      </div>

      {step === 'enroll' && loading && (
        <div className="text-terminal-gray text-center py-10">
          &gt; Generating QR code...
        </div>
      )}

      {step === 'verify' && secret && factorId && (
        <div className="space-y-5">
          {/* QR Code - Optional, show if available */}
          {(qrCode || qrCodeBlobUrl) && (
            <div className="flex justify-center">
              <div className="border border-terminal-border p-4 bg-white rounded">
                <img 
                  src={qrCodeBlobUrl || qrCode} 
                  alt="MFA QR Code" 
                  className="w-64 h-64"
                  onError={(e) => {
                    console.error('QR code image failed to load:', qrCodeBlobUrl || qrCode);
                    e.target.style.display = 'none';
                    const fallback = e.target.nextElementSibling;
                    if (fallback) fallback.style.display = 'block';
                  }}
                />
                <div style={{ display: 'none' }} className="w-64 h-64 flex items-center justify-center text-terminal-gray text-sm">
                  QR code failed to load. Use the secret key below instead.
                </div>
              </div>
            </div>
          )}
          
          {!qrCode && !qrCodeBlobUrl && (
            <div className="text-yellow-400 bg-yellow-400/10 border border-yellow-400/30 p-3 rounded text-sm">
              ⚠ QR code not available. Please use the secret key below to manually add to your authenticator app.
            </div>
          )}

          {/* Secret Key (for manual entry) */}
          <div className="border border-terminal-border p-4 rounded bg-terminal-bg-lighter">
            <div className="text-terminal-gray text-sm mb-2">
              Can't scan? Enter this code manually:
            </div>
            <div className="text-terminal-orange font-mono text-sm break-all select-all">
              {secret}
            </div>
          </div>

          {/* Instructions */}
          <div className="text-terminal-gray text-sm space-y-1">
            <div>&gt; Install an authenticator app (Google Authenticator, Authy, etc.)</div>
            <div>&gt; Scan the QR code or enter the secret key manually</div>
            <div>&gt; Enter the 6-digit code from your app below</div>
          </div>

          {/* Verification Form */}
          <form onSubmit={handleVerify} className="space-y-5">
            <div>
              <div className="mb-2">
                <label htmlFor="verify-code">&gt; Verification Code:</label>
              </div>
              <input
                type="text"
                name="verify-code"
                id="verify-code"
                value={verificationCode}
                onChange={(e) => {
                  const value = e.target.value;
                  const cleanedValue = value.replace(/\D/g, '').slice(0, 6);
                  setVerificationCode(cleanedValue);
                  setError(null);
                }}
                placeholder="000000"
                disabled={loading}
                required
                autoComplete="one-time-code"
                maxLength={6}
                className="terminal-input text-center text-2xl tracking-widest"
              />
            </div>

            {error && (
              <div className="text-red-400 bg-red-400/10 border border-red-400/30 p-3 rounded flex items-center gap-2">
                <XCircle size={16} />
                {error}
              </div>
            )}

            <div className="flex gap-5 pt-5">
              <TerminalButton 
                type="submit" 
                disabled={loading || verificationCode.length !== 6}
              >
                {loading ? '[Verifying...]' : '[Verify & Enable]'}
              </TerminalButton>
              {onCancel && (
                <TerminalButton 
                  type="button"
                  onClick={handleCancel}
                  disabled={loading}
                >
                  [Cancel]
                </TerminalButton>
              )}
            </div>
          </form>
        </div>
      )}

      {error && step === 'enroll' && (
        <div className="text-red-400 bg-red-400/10 border border-red-400/30 p-3 rounded mt-5">
          ✗ {error}
        </div>
      )}
    </div>
  );
};

export default MFASetup;

